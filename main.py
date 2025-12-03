import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_path = r"src/ui/style.qss"
    try:
        with open(style_path, "r") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Stylesheet not found, using default styling")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
