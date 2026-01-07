from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton
)
from PySide6.QtCore import Qt

from modules import ModulesWindow

class EntryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Candidate Entry")
        self.setMinimumSize(700, 600)

        # Main Layout
        main_layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # 1. Heading (Top-Center)
        self.heading = QLabel("Kindly Insert Candidate's Info")
        # Bold and larger font for the heading
        self.heading.setStyleSheet("font-size: 18px; font-weight: bold; margin-top: 10px;")
        main_layout.addWidget(self.heading, alignment=Qt.AlignHCenter | Qt.AlignTop)

        # Add a stretch to push the form to the vertical center
        main_layout.addStretch()

        # 2. Form Section (Centered)
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)

        # Creating the inputs
        self.name_input = self.create_form_row(form_layout, "ID:")
        self.email_input = self.create_form_row(form_layout, "Gender:")
        self.position_input = self.create_form_row(form_layout, "Tasks:")

        # 3. Enter Button
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.setFixedWidth(150)
        self.enter_btn.setStyleSheet("padding: 8px; background-color: #4CAF50; color: white;")

        self.enter_btn.clicked.connect(self.modules_screen)
        
        # Adding elements to form layout
        form_layout.addWidget(self.enter_btn, alignment=Qt.AlignCenter)

        # Add form container to main layout
        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)

        # Add another stretch to balance the vertical spacing
        main_layout.addStretch()

    def create_form_row(self, layout, label_text):
        """Helper function to create a label and textbox pair"""
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        
        label = QLabel(label_text)
        label.setFixedWidth(120)
        
        line_edit = QLineEdit()
        line_edit.setFixedWidth(200)
        
        row_layout.addWidget(label)
        row_layout.addWidget(line_edit)
        
        layout.addWidget(row_widget, alignment=Qt.AlignCenter)
        return line_edit # Return the textbox to access data later

    def modules_screen(self):
        # Logic to save data could go here
        self.modules_screen = ModulesWindow()
        self.modules_screen.show()
        self.close()