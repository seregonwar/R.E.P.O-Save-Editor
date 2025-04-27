from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QProgressBar,
    QWidget, QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
from ui.styles import apply_style

# Definizione stili widget e colori
TEXT_COLOR = "#FFFFFF"
WIDGET_STYLES = {
    "QPushButton": """
        QPushButton {
            background-color: #f0a30a;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #f5b73a;
        }
        QPushButton:pressed {
            background-color: #d09000;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #7f7f7f;
        }
    """,
    "QLabel": """
        QLabel {
            color: white;
        }
    """,
    "QLineEdit": """
        QLineEdit {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #2a2a2a;
            padding: 6px;
            border-radius: 4px;
        }
        QLineEdit:focus {
            border: 1px solid #2a82da;
        }
    """,
    "QProgressBar": """
        QProgressBar {
            background-color: #2a2a2a;
            color: white;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #f0a30a;
            border-radius: 4px;
        }
    """
}

class ModernButton(QPushButton):
    """Pulsante moderno con stile personalizzato"""
    def __init__(self, text="", icon=None, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(WIDGET_STYLES["QPushButton"])
        if icon:
            self.setIcon(QIcon(icon))
            self.setIconSize(QSize(24, 24))
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class ModernLabel(QLabel):
    """Etichetta moderna con stile personalizzato"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(WIDGET_STYLES["QLabel"])
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class ModernLineEdit(QLineEdit):
    """Campo di testo moderno con stile personalizzato"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(WIDGET_STYLES["QLineEdit"])
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(35)

class ModernProgressBar(QProgressBar):
    """Barra di progresso moderna con stile personalizzato"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(WIDGET_STYLES["QProgressBar"])
        self.setTextVisible(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(25)

class IconButton(QWidget):
    """Pulsante con icona e testo"""
    def __init__(self, text="", icon_path=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        
        self.icon_label = QLabel()
        if icon_path:
            pixmap = QPixmap(icon_path)
            self.icon_label.setPixmap(pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        
        self.text_label = ModernLabel(text)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class CardWidget(QWidget):
    """Widget a card con stile moderno"""
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2c3e50;
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        if title:
            title_label = ModernLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #ecf0f1;
                }
            """)
            layout.addWidget(title_label)
        
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)

    def add_widget(self, widget):
        """Aggiunge un widget al contenuto della card"""
        self.content_layout.addWidget(widget) 