import sqlite3
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation
import arcade
from pyglet.graphics import Batch
from PyQt6.QtWidgets import *
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class DatabaseManager:
    def __init__(self, db_name='game_database.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_tables()

    def init_tables(self):
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            record INTEGER DEFAULT 0,
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        self.conn.commit()

    def authenticate(self, username, password):
        self.cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return self.cursor.fetchone() is not None

    def register(self, username, password):
        try:
            self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if self.cursor.fetchone():
                return False, "Пользователь уже существует!"

            self.cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            self.cursor.execute(
                "INSERT INTO game_levels (username, level, record) VALUES (?, ?, ?)",
                (username, 1, 0)
            )

            self.conn.commit()
            return True, "Регистрация прошла успешно!"

        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {e}"

    def get_user_record(self, username):
        self.cursor.execute(
            "SELECT record FROM game_levels WHERE username = ?",
            (username,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_user_record(self, username, record):
        try:
            current_record = self.get_user_record(username)
            if record > current_record:
                self.cursor.execute(
                    "UPDATE game_levels SET record = ? WHERE username = ?",
                    (record, username)
                )
                self.conn.commit()
                return True, f"Новый рекорд: {record} монет!"
            else:
                return False, f"Текущий рекорд: {current_record} монет. Новый результат: {record} монет."
        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {e}"

    def close(self):
        if self.conn:
            self.conn.close()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.current_user = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Вход в игру')
        self.setFixedSize(900, 675)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)

        button_style = """
            QPushButton {
                background-color: #4CAF50;
                border-radius: 3px;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                padding: 20px 40px;
                min-width: 300px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
                border: 3px solid #2E7D32;
            }
            QPushButton:pressed {
                background-color: #2E7D32;
            }
        """

        exit_button_style = """
            QPushButton {
                background-color: #f44336;
                border-radius: 3px;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                padding: 20px 40px;
                min-width: 300px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #da190b;
                border: 3px solid #ba000d;
            }
            QPushButton:pressed {
                background-color: #ba000d;
            }
        """

        self.play_button = QPushButton('🎮 ИГРАТЬ')
        self.play_button.setStyleSheet(button_style)
        self.play_button.clicked.connect(self.show_auth_dialog)
        self.play_button.setCursor(Qt.CursorShape.PointingHandCursor)

        self.exit_button = QPushButton('🚪 ВЫЙТИ')
        self.exit_button.setStyleSheet(exit_button_style)
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)

        main_layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)

        self.create_bottom_panel(main_layout)
        self.set_background()
        self.center_window()

    def set_background(self):
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, 900, 675)

        pixmap = QPixmap("doc/image.png")

        pixmap = pixmap.scaled(900, 675,
                               Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                               Qt.TransformationMode.SmoothTransformation)

        self.background_label.setPixmap(pixmap)
        self.background_label.lower()

    def center_window(self):
        frame_geometry = self.frameGeometry()
        screen_center = QApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def showEvent(self, event):
        super().showEvent(event)
        self.center_window()

    def create_bottom_panel(self, main_layout):
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 10)

        info_label = QLabel("Разработали: Бобков Григорий, Бугреев Роман")
        info_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(0, 0, 0, 150)
            }
        """)

        bottom_layout.addWidget(info_label)
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(bottom_widget)

    def show_auth_dialog(self):
        dialog = AuthDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            username, password, is_register = dialog.get_credentials()

            if is_register:
                success, message = self.db.register(username, password)
                if success:
                    QMessageBox.information(self, "Успех", message)
                    self.current_user = username
                    self.start_game()
                else:
                    QMessageBox.warning(self, "Ошибка", message)
            else:
                if self.db.authenticate(username, password):
                    QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
                    self.current_user = username
                    self.start_game()
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")

    def start_game(self):
        self.hide()
        self.game_window = GameWindow(self.current_user, self.db)
        self.game_window.show()

    def closeEvent(self, event):
        if hasattr(self, 'db') and self.db:
            self.db.close()
        event.accept()


class AuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Вход")
        self.setFixedSize(400, 320)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 2px solid #3498db;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1abc9c;
            }
            QPushButton {
                border-radius: 3px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton#loginBtn {
                border-radius: 3px;
                background-color: #3498db;
                color: white;
            }
            QPushButton#registerBtn {
                border-radius: 3px;
                background-color: #2ecc71;
                color: white;
            }
            QPushButton#cancelBtn {
                border-radius: 5px;
                background-color: #e74c3c;
                color: white;
            }
        """)

        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Войти")
        self.login_button.setObjectName("loginBtn")
        self.login_button.clicked.connect(self.accept)
        buttons_layout.addWidget(self.login_button)

        self.register_button = QPushButton("Регистрация")
        self.register_button.setObjectName("registerBtn")
        self.register_button.clicked.connect(self.show_register_dialog)
        buttons_layout.addWidget(self.register_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelBtn")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

    def get_credentials(self):
        return (
            self.username_input.text().strip(),
            self.password_input.text(),
            False
        )

    def show_register_dialog(self):
        dialog = RegisterDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.username_input.setText(dialog.username)
            self.password_input.setText(dialog.password)
            self.accept()


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self.password = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 320)
        self.setModal(True)

        layout = QVBoxLayout(self)

        self.setStyleSheet("""
            QDialog {
                background-color: #34495e;
            }
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                padding: 10px;
                font-size: 16px;
                border: 2px solid #2ecc71;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #27ae60;
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border: none;
                margin: 5px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton#registerBtn {
                background-color: #2ecc71;
                color: white;
            }
            QPushButton#cancelBtn {
                background-color: #e74c3c;
                color: white;
            }
        """)

        layout.addWidget(QLabel("Имя пользователя:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введите имя пользователя")
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("Пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Введите пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)

        layout.addWidget(QLabel("Подтвердите пароль:"))
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Повторите пароль")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_input)

        buttons_layout = QHBoxLayout()

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.setObjectName("registerBtn")
        self.register_button.clicked.connect(self.register_user)
        buttons_layout.addWidget(self.register_button)

        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.setObjectName("cancelBtn")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_button)

        layout.addLayout(buttons_layout)

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Ошибка", "Имя пользователя должно быть не менее 3 символов!")
            return

        if len(password) < 3:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 3 символов!")
            return

        parent = self.parent()
        if parent and hasattr(parent, 'parent'):
            login_window = parent.parent()
            if hasattr(login_window, 'db'):
                success, message = login_window.db.register(username, password)
                if success:
                    self.username = username
                    self.password = password
                    QMessageBox.information(self, "Успех", message)
                    self.accept()
                else:
                    QMessageBox.warning(self, "Ошибка", message)


class MainMenu(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        top_panel = QFrame()
        top_panel.setFixedHeight(100)
        top_panel.setStyleSheet("""
            QFrame {
                background-color: #1A1A1A;
                border-bottom: 2px solid #333333;
            }
        """)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(40, 10, 40, 10)
        self.btn_back = QPushButton("◄ НАЗАД")
        self.btn_back.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.btn_back.setMinimumHeight(60)
        self.btn_back.setMinimumWidth(200)
        self.btn_back.setStyleSheet("""
            QPushButton {
                background-color: #2A2A2A;
                color: #E0E0E0;
                border: 2px solid #555555;
                border-radius: 12px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3A3A3A;
                border: 2px solid #777777;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #1A1A1A;
                border: 2px solid #555555;
            }
        """)
        self.btn_back.clicked.connect(self.do_nothing)
        top_layout.addWidget(self.btn_back)
        title = QLabel("ГЛАВНОЕ МЕНЮ")
        title.setFont(QFont("Arial", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                padding: 5px;
                letter-spacing: 2px;
            }
        """)
        top_layout.addWidget(title, 1)

        # Добавляем отображение рекорда
        if hasattr(self.main_window, 'current_user') and self.main_window.current_user:
            record = self.main_window.db.get_user_record(self.main_window.current_user)
            record_label = QLabel(f"Рекорд: {record}")
            record_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            record_label.setStyleSheet("""
                QLabel {
                    color: #FFD700;
                    padding: 10px;
                    background-color: rgba(0, 0, 0, 150);
                    border-radius: 10px;
                }
            """)
            top_layout.addWidget(record_label)

        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)
        background_widget = QWidget()
        background_widget.setStyleSheet("background-color: #000000;")
        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)
        pixmap = QPixmap("doc/image2.jpg")
        screen_size = self.main_window.size()
        bg_width = screen_size.width()
        bg_height = screen_size.height() - 100
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(bg_width, bg_height,
                                          Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                          Qt.TransformationMode.SmoothTransformation)
        else:
            scaled_pixmap = QPixmap(bg_width, bg_height)
            scaled_pixmap.fill(Qt.GlobalColor.black)
        self.background_label = QLabel()
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        container_layout.addWidget(self.background_label)
        overlay_widget = QWidget()
        overlay_widget.setStyleSheet("background-color: transparent;")
        overlay_layout = QVBoxLayout(overlay_widget)
        overlay_layout.setContentsMargins(0, 0, 0, 0)
        overlay_layout.setSpacing(0)
        overlay_layout.addStretch(1)
        subtitle = QLabel("УРОВНИ")
        subtitle.setFont(QFont("Arial", 40, QFont.Weight.Bold))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("""
            QLabel {
                color: #F0F0F0;
                padding: 25px;
                margin-bottom: 80px;
                background-color: rgba(30, 30, 30, 0.7);
                border-radius: 15px;
                border: 1px solid #555555;
                letter-spacing: 1px;
            }
        """)
        overlay_layout.addWidget(subtitle, 0, Qt.AlignmentFlag.AlignCenter)
        levels_layout = QHBoxLayout()
        levels_layout.setSpacing(120)
        levels_layout.setContentsMargins(60, 0, 60, 0)
        levels_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_level1 = self.create_square_level_button("1", "#4A4A4A", "#E0E0E0")
        self.btn_level1.clicked.connect(lambda: self.start_level(1))
        levels_layout.addWidget(self.btn_level1)
        self.btn_level2 = self.create_square_level_button("2", "#4A4A4A", "#E0E0E0")
        self.btn_level2.clicked.connect(lambda: self.start_level(2))
        levels_layout.addWidget(self.btn_level2)
        self.btn_level3 = self.create_square_level_button("3", "#4A4A4A", "#E0E0E0")
        self.btn_level3.clicked.connect(lambda: self.start_level(3))
        levels_layout.addWidget(self.btn_level3)
        overlay_layout.addLayout(levels_layout)
        overlay_layout.addStretch(1)
        overlay_container = QWidget()
        overlay_container.setStyleSheet("background-color: transparent;")
        overlay_container.setLayout(overlay_layout)
        overlay_container.setParent(container_widget)
        overlay_container.setGeometry(0, 0, bg_width, bg_height)
        background_layout.addWidget(container_widget)
        main_layout.addWidget(background_widget)
        self.setLayout(main_layout)

    def create_square_level_button(self, number, bg_color, text_color):
        button = QPushButton()
        screen_width = self.main_window.size().width()
        button_size = min(300, max(200, int(screen_width / 5)))
        button.setFixedSize(button_size, button_size)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 4px solid #777777;
                border-radius: 20px;
            }}
            QPushButton:hover {{
                border: 5px solid #999999;
                background-color: {bg_color};
            }}
            QPushButton:pressed {{
                border: 4px solid #777777;
                background-color: {bg_color};
            }}
        """)
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)
        button_layout.setSpacing(5)
        button_layout.setContentsMargins(20, 20, 20, 20)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_size = button_size // 3
        level_number = QLabel(number)
        level_number.setFont(QFont("Arial", font_size, QFont.Weight.Bold))
        level_number.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_number.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                margin: 0;
                padding: 0;
            }}
        """)
        level_number.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        button_layout.addWidget(level_number)
        level_text = QLabel("УРОВЕНЬ")
        level_text.setFont(QFont("Arial", max(16, button_size // 12), QFont.Weight.Normal))
        level_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_text.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                margin: 0;
                padding: 0;
                opacity: 0.9;
            }}
        """)
        level_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        button_layout.addWidget(level_text)
        button.setLayout(button_layout)
        return button

    def start_level(self, level_num):
        self.main_window.hide()
        self.level = MazeGame(self.main_window.current_user, self.main_window.db)
        self.level.setup(level_num)
        arcade.run()

    def do_nothing(self):
        self.main_window.close()
        self.login_window = LoginWindow()
        self.login_window.show()


class GameWindow(QMainWindow):
    def __init__(self, username, db):
        super().__init__()
        self.current_user = username
        self.db = db
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Меню уровней')
        self.setFixedSize(900, 675)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        self.stacked_widget = QStackedWidget()
        self.main_menu = MainMenu(self)
        self.stacked_widget.addWidget(self.main_menu)
        self.setCentralWidget(self.stacked_widget)
        self.show()


SCREEN_TITLE = "Game"
n = 2

SCALING = 4
SCREEN_WIDHT = 16 * 15 * SCALING
SCREEN_HEIGHT = 16 * 12 * SCALING
SPEED = 1
all_coins = 0


class MazeGame(arcade.Window):
    def __init__(self, username, db):
        super().__init__(SCREEN_WIDHT, SCREEN_HEIGHT, SCREEN_TITLE)
        self.username = username
        self.db = db
        arcade.set_background_color(arcade.color.BLACK)

        self.money = [12, 15, 18]
        self.all_coins = 0

    def setup(self, n):
        self.coin_count = 0

        self.hit_sound = arcade.load_sound('doc/clear-ringing-blow-to-the-stump.wav')
        self.exit_sound = arcade.load_sound('doc/victory-fanfare-sound.wav')
        self.death_sound = arcade.load_sound('doc/brutal-death-blow.wav')

        self.n = n
        self.is_moving = False
        self.can_play = True
        map_name = f"level_{self.n}_upd.tmx"
        tile_map = arcade.load_tilemap(map_name, scaling=SCALING)

        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.exit_list = arcade.SpriteList()
        self.spikes_list = arcade.SpriteList()

        self.player_list = tile_map.sprite_lists['player_layer']
        self.wall_list = tile_map.sprite_lists['wall_layer']
        self.coin_list = tile_map.sprite_lists['coin_layer']
        self.exit_list = tile_map.sprite_lists['exit_layer']
        self.spikes_list = tile_map.sprite_lists['spikes_layer']

        self.player_sprite = self.player_list[0]
        if self.n == 3:
            self.player_sprite.center_x = SCREEN_WIDHT // 2
            self.player_sprite.center_y = SCREEN_HEIGHT - 16 * SCALING * 0.5
        else:
            self.player_sprite.center_x = 16 * SCALING * 1.5
            self.player_sprite.center_y = SCREEN_HEIGHT - 16 * SCALING * 1.5

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

        self.coin_count = 0

    def on_draw(self):
        self.batch = Batch()
        self.main_text = arcade.Text(f"Монет: {self.coin_count}/{self.money[self.n - 1]}, R - возрождение", 170, 0,
                                     arcade.color.WHITE, font_size=20, anchor_x="center", batch=self.batch)
        self.clear()

        self.exit_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.spikes_list.draw()
        self.player_list.draw()

        self.batch.draw()

    def on_key_press(self, key, modifiers):
        if self.can_play and not self.is_moving:
            if key == arcade.key.UP:
                self.player_sprite.change_y = SPEED
            elif key == arcade.key.DOWN:
                self.player_sprite.change_y = -SPEED
            elif key == arcade.key.LEFT:
                self.player_sprite.change_x = -SPEED
            elif key == arcade.key.RIGHT:
                self.player_sprite.change_x = SPEED
            self.is_moving = True

        if key == arcade.key.R:
            self.coin_count = 0
            self.setup(self.n)
            self.can_play = True

        if key == arcade.key.E:
            self.close()
            app = QApplication.instance()
            for window in app.topLevelWidgets():
                if isinstance(window, GameWindow):
                    window.show()
                    break

    def on_key_release(self, key, modifiers):
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

    def on_update(self, delta_time):
        self.physics_engine.update()

        if self.is_moving:
            exit_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.exit_list)
            collisions = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)

            while not (exit_hit_list or collisions):
                self.player_sprite.center_x += self.player_sprite.change_x
                self.player_sprite.center_y += self.player_sprite.change_y

                collisions = arcade.check_for_collision_with_list(self.player_sprite, self.wall_list)
                coins_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
                spikes_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.spikes_list)
                exit_hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.exit_list)

                for coin in coins_hit_list:
                    self.coin_count += 1
                    coin.remove_from_sprite_lists()

                if spikes_hit_list:
                    self.can_play = False
                    self.death_sound.play()
                    self.player_sprite.remove_from_sprite_lists()
                    break

                if exit_hit_list:
                    self.is_moving = False
                    if self.n < 3:
                        self.n += 1
                        self.all_coins += self.coin_count
                        self.exit_sound.play()
                        self.setup(self.n)
                    else:
                        self.all_coins += self.coin_count
                        total_coins = self.all_coins
                        self.close()
                        app = QApplication.instance()
                        victory = VictoryDialog(self.username, self.db, total_coins)
                        victory.show()
                        break

            if self.can_play:
                self.hit_sound.play()
            self.is_moving = False


class VictoryDialog(QDialog):
    return_to_menu = pyqtSignal()
    exit_game = pyqtSignal()

    def __init__(self, username, db, total_coins, parent=None):
        super().__init__(parent)
        self.username = username
        self.db = db
        self.total_coins = total_coins
        self.setup_ui()
        self.setup_style()
        self.update_record()

    def setup_ui(self):
        self.setWindowTitle("Победа!")
        self.setFixedSize(700, 600)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        main_widget = QWidget(self)
        main_widget.setObjectName("mainWidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)

        title_label = QLabel("ИГРА ПРОЙДЕНА!")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #FFD700;
            text-shadow: 3px 3px 0px #000000;
            margin: 0px;
            padding: 0px;
        """)

        trophy_label = QLabel("🏆")
        trophy_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        trophy_label.setStyleSheet("font-size: 60px; margin: 0px;")

        completion_label = QLabel("Вы успешно завершили игру!")
        completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        completion_label.setStyleSheet("""
            font-size: 24px;
            color: #CCCCCC;
            margin: 0px;
        """)

        # Отображаем количество собранных монет
        self.count_label = QLabel(f"Монет собрано: {self.total_coins}/45")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.count_label.setStyleSheet("""
            font-size: 24px;
            color: #CCCCCC;
            margin: 0px;
        """)

        # Отображаем рекорд
        record = self.db.get_user_record(self.username)
        self.record_label = QLabel(f"Ваш рекорд: {record} монет")
        self.record_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.record_label.setStyleSheet("""
            font-size: 20px;
            color: #4CAF50;
            margin: 0px;
            font-weight: bold;
        """)

        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 20, 0, 0)
        buttons_layout.setSpacing(10)

        self.menu_btn = QPushButton("В ГЛАВНОЕ МЕНЮ")
        self.menu_btn.setFixedHeight(45)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.clicked.connect(self.return_to_menu_action)

        self.exit_btn = QPushButton("ВЫЙТИ ИЗ ИГРЫ")
        self.exit_btn.setFixedHeight(45)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.exit_game_action)

        buttons_layout.addWidget(self.menu_btn)
        buttons_layout.addWidget(self.exit_btn)

        main_layout.addWidget(title_label)
        main_layout.addWidget(trophy_label)
        main_layout.addWidget(completion_label)
        main_layout.addWidget(self.count_label)
        main_layout.addWidget(self.record_label)
        main_layout.addWidget(buttons_widget)

        main_layout_wrapper = QVBoxLayout(self)
        main_layout_wrapper.setContentsMargins(0, 0, 0, 0)
        main_layout_wrapper.addWidget(main_widget)

    def setup_style(self):
        self.setStyleSheet("""
            QWidget#mainWidget {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4A00E0,
                    stop: 1 #8E2DE2
                );
                border-radius: 3px;
                border: 3px solid #FFD700;
            }

            QPushButton {
                border-radius: 3px;  
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                transition: all 0.3s;
                min-width: 200px;
            }

            QPushButton#menu_btn {
                border-radius: 5px;
                background-color: #FFD700;
                color: #000000;
                border: 2px solid #FFD700;
            }

            QPushButton#menu_btn:hover {
                background-color: #FFE44D;
                border-color: #FFE44D;
                box-shadow: 0px 5px 15px rgba(255, 215, 0, 0.4);
                transform: translateY(-2px);
            }

            QPushButton#menu_btn:pressed {
                background-color: #E6BE00;
                border-color: #E6BE00;
                transform: translateY(1px);
            }

            QPushButton#exit_btn {
                border-radius: 5px;
                background-color: transparent;
                color: #FFFFFF;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }

            QPushButton#exit_btn:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: rgba(255, 255, 255, 0.6);
            }

            QPushButton#exit_btn:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)

        self.menu_btn.setObjectName("menu_btn")
        self.exit_btn.setObjectName("exit_btn")

    def update_record(self):
        if self.total_coins > 0:
            success, message = self.db.update_user_record(self.username, self.total_coins)
            if success:
                self.record_label.setText(f"{message}")
                self.record_label.setStyleSheet("""
                    font-size: 20px;
                    color: #FFD700;
                    margin: 0px;
                    font-weight: bold;
                """)
            else:
                self.record_label.setText(message)
                self.record_label.setStyleSheet("""
                    font-size: 20px;
                    color: #4CAF50;
                    margin: 0px;
                    font-weight: bold;
                """)

    def return_to_menu_action(self):
        app = QApplication.instance()
        for window in app.topLevelWidgets():
            if isinstance(window, GameWindow):
                window.show()
                break
        self.accept()

    def exit_game_action(self):
        app = QApplication.instance()
        app.quit()

    def showEvent(self, event):
        super().showEvent(event)
        self.setup_animation()

    def setup_animation(self):
        self.setWindowOpacity(0)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


def main():
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
