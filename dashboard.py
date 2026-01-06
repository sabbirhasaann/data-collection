# from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
# from PySide6.QtCore import Qt


# class Dashboard(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setMinimumSize(700, 600)
#         self.setWindowTitle("Dashboard")
#         layout = QVBoxLayout()
#         label = QLabel("This is the Dashboard Window")
#         label.setAlignment(Qt.AlignCenter)
        
#         container = QWidget()
#         container.setLayout(layout)
#         layout.addWidget(label)
#         self.setCentralWidget(container)


from PySide6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

from entry import EntryWindow

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.resize(600, 400)

        # Central content
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(QLabel("Main Dashboard Area"), alignment=Qt.AlignCenter)
        self.setCentralWidget(container)

        # 1. Create the button with 'self' as parent to make it float
        self.btn_start = QPushButton("Start", self)
        self.btn_start.setFixedSize(100, 40)
        
        # Adding some style to make it pop
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-size: 14px;
            }
        """)
        self.btn_start.clicked.connect(self.entry_screen)

    # 2. This function triggers automatically whenever the window size changes
    def resizeEvent(self, event):
        super().resizeEvent(event)
        
        # Calculate coordinates for Right-Bottom alignment
        # Margin of 20px from the edges
        margin = 20
        x = self.width() - self.btn_start.width() - margin
        y = self.height() - self.btn_start.height() - margin
        
        self.btn_start.move(x, y)

    def entry_screen(self):
        self.entry_screen = EntryWindow()
        self.entry_screen.show()
        self.close()