import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer

#dashboard
from dashboard import Dashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowTitle("My First PySide App")
        self.setMinimumSize(700, 600)

        # Create a central widget and layout
        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Add UI Elements
        self.label = QLabel("Hello! Press the button below.")
        self.label.setAlignment(Qt.AlignCenter)

        self.label_copyright = QLabel("@2025-2026 Right Reserved")
        self.label_copyright.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)



        layout.addWidget(self.label)
        layout.addWidget(self.label_copyright)
        

        QTimer.singleShot(2000, self.launch_dashboard)



    def launch_dashboard(self):
        self.dashboard = Dashboard()
        self.dashboard.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
