from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QGridLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

class ModuleCard(QFrame):
    """A custom widget to represent a single Module Card"""
    def __init__(self, name):
        super().__init__()
        self.setFixedSize(150, 150)
        self.setFrameShape(QFrame.StyledPanel)
        
        # Styling the card
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 2px solid #dfe6e9;
                border-radius: 15px;
            }
            QFrame:hover {
                border: 2px solid #0984e3;
                background-color: #f1f2f6;
            }
        """)

        layout = QVBoxLayout(self)
        label = QLabel(name)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(label)

class ModulesWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Modules")
        self.setMinimumSize(600, 500)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 1. Top Title Bar
        self.title_bar = QLabel("Modules")
        self.title_bar.setFixedHeight(60)
        self.title_bar.setAlignment(Qt.AlignCenter)
        self.title_bar.setStyleSheet("""
            background-color: #2d3436;
            color: white;
            font-size: 20px;
            font-weight: bold;
        """)
        main_layout.addWidget(self.title_bar)

        # 2. Card Container (Center)
        card_container = QWidget()
        grid_layout = QGridLayout(card_container)
        
        # Sample Module Names
        module_names = ["Analytics", "Inventory", "Users", "Settings", "Reports", "Help"]
        
        # Create a 2x3 Grid
        rows = 2
        cols = 3
        for i, name in enumerate(module_names):
            card = ModuleCard(name)
            grid_layout.addWidget(card, i // cols, i % cols)

        # Add the card container to the main layout and center it
        main_layout.addStretch()
        main_layout.addWidget(card_container, alignment=Qt.AlignCenter)
        main_layout.addStretch()