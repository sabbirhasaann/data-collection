import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My First PySide App")
        self.setMinimumSize(400, 300)

        # Create a central widget and layout
        layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Add UI Elements
        self.label = QLabel("Hello! Press the button below.")
        self.label.setAlignment(Qt.AlignCenter)

        self.button = QPushButton("Click Me!")
        self.button.clicked.connect(self.on_button_click)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def on_button_click(self):
        self.label.setText("The button was clicked! 🎉")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
