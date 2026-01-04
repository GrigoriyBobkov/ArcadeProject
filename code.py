import sys
import sqlite3
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


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
            FOREIGN KEY (username) REFERENCES users(username)
        )
        ''')

        self.conn.commit()

    def authenticate(self, username, password):

        self.cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        )

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
                "INSERT INTO game_levels (username, level) VALUES (?, ?)",
                (username, 1)
            )

            self.conn.commit()
            return True, "Регистрация прошла успешно!"

        except sqlite3.Error as e:
            return False, f"Ошибка базы данных: {e}"

    def close(self):
        if self.conn:
            self.conn.close()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Вход в игру')
        self.setFixedSize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        main_layout.addStretch(1)

        button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
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
                color: white;
                font-size: 24px;
                font-weight: bold;
                border: none;
                border-radius: 15px;
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
        self.background_label.setGeometry(0, 0, 800, 600)

        pixmap = QPixmap("doc/image.png")

        pixmap = pixmap.scaled(800, 600,
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
                background-color: rgba(0, 0, 0, 150);
                border-radius: 10px;
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
                    self.start_game(username)
                else:
                    QMessageBox.warning(self, "Ошибка", message)
            else:
                if self.db.authenticate(username, password):
                    QMessageBox.information(self, "Успех", f"Добро пожаловать, {username}!")
                    self.start_game(username)
                else:
                    QMessageBox.warning(self, "Ошибка", "Неверное имя пользователя или пароль!")

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
        self.setFixedSize(400, 300)
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
                border-radius: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #1abc9c;
            }
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 12px;
                border: none;
                border-radius: 5px;
                margin: 5px;
            }
            QPushButton:hover {
                opacity: 0.9;
            }
            QPushButton#loginBtn {
                background-color: #3498db;
                color: white;
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


class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.username = ""
        self.password = ""
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Регистрация")
        self.setFixedSize(400, 300)
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
                border-radius: 5px;
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
                border-radius: 5px;
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


def main():
    app = QApplication(sys.argv)

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
