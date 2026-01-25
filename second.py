from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation


class ExitDialog(QDialog):
    exit_confirmed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        self.setWindowTitle("Выход из игры")
        self.setFixedSize(400, 200)

        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        main_widget = QWidget(self)
        main_widget.setObjectName("mainWidget")
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        icon_label = QLabel("⏸")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 40px; margin-bottom: 5px;")

        text_label = QLabel("Покинуть текущую игру?")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setWordWrap(True)
        text_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #333333;
            margin: 0px;
        """)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)

        self.cancel_btn = QPushButton("ОСТАТЬСЯ")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        self.exit_btn = QPushButton("ВЫЙТИ")
        self.exit_btn.setFixedHeight(40)
        self.exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_btn.clicked.connect(self.accept_and_emit)

        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(self.exit_btn)

        main_layout.addWidget(icon_label)
        main_layout.addWidget(text_label)
        main_layout.addStretch()
        main_layout.addWidget(buttons_widget)

        main_layout_wrapper = QVBoxLayout(self)
        main_layout_wrapper.setContentsMargins(0, 0, 0, 0)
        main_layout_wrapper.addWidget(main_widget)

    def setup_style(self):
        self.setStyleSheet("""
            QWidget#mainWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 5px;
                border: 1px solid #e0e0e0;
            }

            QPushButton {
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
                padding: 8px 16px;
                transition: all 0.2s;
            }

            QPushButton#cancel_btn {
                border-radius: 3px;
                background-color: transparent;
                color: #666666;
                border: 2px solid #cccccc;
            }

            QPushButton#cancel_btn:hover {
                background-color: #f8f8f8;
                border-color: #999999;
                color: #333333;
            }

            QPushButton#cancel_btn:pressed {
                background-color: #eeeeee;
            }

            QPushButton#exit_btn {
                border-radius: 3px;
                background-color: #ff4444;
                color: white;
                border: 2px solid #ff4444;
            }

            QPushButton#exit_btn:hover {
                background-color: #ff5555;
                border-color: #ff5555;
                box-shadow: 0px 4px 8px rgba(255, 68, 68, 0.3);
            }

            QPushButton#exit_btn:pressed {
                background-color: #dd3333;
                border-color: #dd3333;
            }
        """)

        self.cancel_btn.setObjectName("cancel_btn")
        self.exit_btn.setObjectName("exit_btn")

    def accept_and_emit(self):
        self.accept()
        self.exit_confirmed.emit()

    def showEvent(self, event):
        super().showEvent(event)
        self.setup_animation()

    def setup_animation(self):
        self.setWindowOpacity(0)

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


class VictoryDialog(QDialog):
    return_to_menu = pyqtSignal()
    exit_game = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_style()

    def setup_ui(self):
        self.setWindowTitle("Победа!")
        self.setFixedSize(500, 500)

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

        count_label = QLabel("Монет собрано: 0/45")
        count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        count_label.setStyleSheet("""
                    font-size: 24px;
                    color: #CCCCCC;
                    margin: 0px;
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
        main_layout.addWidget(count_label)
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

    def return_to_menu_action(self):
        self.accept()
        self.return_to_menu.emit()

    def exit_game_action(self):
        self.accept()
        self.exit_game.emit()

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


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Тест окон:
    exit_dialog = ExitDialog()
    exit_dialog.exec()
    victory_dialog = VictoryDialog()
    victory_dialog.exec()

    sys.exit(app.exec())
