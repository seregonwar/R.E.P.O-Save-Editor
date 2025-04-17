from PyQt6.QtWidgets import QWidget, QHBoxLayout
from .modern_widgets import ModernButton

class ToolBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #2c3e50;")
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        self.open_btn = ModernButton("Open File")
        self.save_btn = ModernButton("Save File")
        
        self.layout.addWidget(self.open_btn)
        self.layout.addWidget(self.save_btn)
        self.layout.addStretch() 