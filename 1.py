import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

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
        self.btn_back.setFont(QFont("Arial", 20, QFont.Weight.Bold))
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
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                padding: 5px;
                letter-spacing: 2px;
            }
        """)
        top_layout.addWidget(title, 1)
        empty_widget = QWidget()
        empty_widget.setFixedWidth(200)
        top_layout.addWidget(empty_widget)
        top_panel.setLayout(top_layout)
        main_layout.addWidget(top_panel)
        background_widget = QWidget()
        background_widget.setStyleSheet("background-color: #000000;")
        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)
        pixmap = QPixmap("images/фон2.jpg")
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
        subtitle.setFont(QFont("Arial", 80, QFont.Weight.Bold))
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
        button_size = min(380, max(320, int(screen_width / 5)))
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
                transform: scale(1.05);
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
        print(f"Кнопка уровня {level_num} нажата (ничего не происходит)")
    def do_nothing(self):
        print("Кнопка 'Назад' нажата (ничего не происходит)")

class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    def init_ui(self):
        self.setWindowTitle('ARCADE GAME - ПОЛНЫЙ ЭКРАН')
        self.showFullScreen()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
        """)
        self.stacked_widget = QStackedWidget()
        self.main_menu = MainMenu(self)
        self.stacked_widget.addWidget(self.main_menu)
        self.setCentralWidget(self.stacked_widget)
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = GameWindow()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()