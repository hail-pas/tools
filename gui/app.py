import sys
import typing
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Tools")
        self.setMinimumSize(QSize(800, 550))

        button = QPushButton("translate")

        # Set the central widget of the Window.
        self.setCentralWidget(button)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # Start the event loop.
    app.exec()
