"""
Stili per l'interfaccia grafica di R.E.P.O Save Editor
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from qt_material import apply_stylesheet
from PyQt6.QtGui import QPalette, QColor

# Colori principali
PRIMARY_COLOR = "#3498db"
SECONDARY_COLOR = "#2ecc71"
BACKGROUND_COLOR = "#1a1a1a"
CARD_BACKGROUND = "#2c3e50"
TEXT_COLOR = "#ecf0f1"
BORDER_COLOR = "#34495e"
HOVER_COLOR = "#2980b9"
DISABLED_COLOR = "#7f8c8d"

# Stili comuni
COMMON_STYLES = {
    "font_size": "14px",
    "border_radius": "5px",
    "padding": "5px",
    "min_height": "40px"
}

# Stili per i widget
WIDGET_STYLES = {
    "QMainWindow": f"""
        background-color: {BACKGROUND_COLOR};
    """,
    
    "QMenuBar": f"""
        QMenuBar {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            border-bottom: 1px solid {PRIMARY_COLOR};
        }}
        QMenuBar::item {{
            padding: 5px 10px;
            background-color: transparent;
        }}
        QMenuBar::item:selected {{
            background-color: {PRIMARY_COLOR};
        }}
        QMenu {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            border: 1px solid {PRIMARY_COLOR};
        }}
        QMenu::item {{
            padding: 5px 20px;
        }}
        QMenu::item:selected {{
            background-color: {PRIMARY_COLOR};
        }}
    """,
    
    "QStatusBar": f"""
        QStatusBar {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            border-top: 1px solid {PRIMARY_COLOR};
        }}
    """,
    
    "QTabWidget": f"""
        QTabWidget::pane {{
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            background-color: {CARD_BACKGROUND};
        }}
        QTabBar::tab {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            padding: 8px 16px;
            border: 1px solid {BORDER_COLOR};
            border-bottom: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }}
        QTabBar::tab:selected {{
            background-color: {PRIMARY_COLOR};
            color: white;
        }}
        QTabBar::tab:hover {{
            background-color: {HOVER_COLOR};
        }}
    """,
    
    "QPushButton": f"""
        QPushButton {{
            background-color: {PRIMARY_COLOR};
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {HOVER_COLOR};
        }}
        QPushButton:disabled {{
            background-color: {DISABLED_COLOR};
        }}
    """,
    
    "QLineEdit": f"""
        QLineEdit {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            padding: 8px;
        }}
        QLineEdit:focus {{
            border: 1px solid {PRIMARY_COLOR};
        }}
    """,
    
    "QComboBox": f"""
        QComboBox {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            padding: 8px;
        }}
        QComboBox::drop-down {{
            border: none;
        }}
        QComboBox::down-arrow {{
            image: url(assets/icons/down_arrow.png);
            width: 12px;
            height: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {CARD_BACKGROUND};
            color: {TEXT_COLOR};
            selection-background-color: {PRIMARY_COLOR};
        }}
    """,
    
    "QCheckBox": f"""
        QCheckBox {{
            color: {TEXT_COLOR};
            spacing: 5px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {BORDER_COLOR};
            border-radius: 3px;
            background-color: {CARD_BACKGROUND};
        }}
        QCheckBox::indicator:checked {{
            background-color: {PRIMARY_COLOR};
            border: 1px solid {PRIMARY_COLOR};
        }}
    """,
    
    "QProgressBar": f"""
        QProgressBar {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
            text-align: center;
            color: {TEXT_COLOR};
        }}
        QProgressBar::chunk {{
            background-color: {PRIMARY_COLOR};
            border-radius: 5px;
        }}
    """,
    
    "QScrollArea": f"""
        QScrollArea {{
            background-color: {CARD_BACKGROUND};
            border: 1px solid {BORDER_COLOR};
            border-radius: 5px;
        }}
        QScrollBar:vertical {{
            background-color: {CARD_BACKGROUND};
            width: 12px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: {PRIMARY_COLOR};
            min-height: 20px;
            border-radius: 6px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """
}

def apply_style(app: QApplication):
    """Applica lo stile all'applicazione"""
    # Imposta il tema scuro
    app.setStyle("Fusion")
    
    # Crea una palette personalizzata
    palette = QPalette()
    
    # Colori di base
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    # Colori disabilitati
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorRole.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    
    # Applica la palette
    app.setPalette(palette)
    
    # Stile CSS globale
    app.setStyleSheet("""
        QMainWindow {
            background-color: #353535;
        }
        
        QTabWidget::pane {
            border: 1px solid #2a2a2a;
            background: #353535;
        }
        
        QTabBar::tab {
            background: #2a2a2a;
            color: white;
            padding: 8px 12px;
            border: 1px solid #2a2a2a;
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }
        
        QTabBar::tab:selected {
            background: #353535;
            border-color: #2a82da;
        }
        
        QTabBar::tab:hover {
            background: #3a3a3a;
        }
        
        QPushButton {
            background-color: #2a82da;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #3a92ea;
        }
        
        QPushButton:pressed {
            background-color: #1a72ca;
        }
        
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #7f7f7f;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #2a2a2a;
            padding: 4px;
            border-radius: 4px;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #2a82da;
        }
        
        QTableWidget {
            background-color: #2a2a2a;
            color: white;
            gridline-color: #353535;
            border: 1px solid #2a2a2a;
            border-radius: 4px;
        }
        
        QTableWidget::item {
            padding: 4px;
        }
        
        QTableWidget::item:selected {
            background-color: #2a82da;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #2a2a2a;
            color: white;
            padding: 4px;
            border: 1px solid #353535;
        }
        
        QMenuBar {
            background-color: #2a2a2a;
            color: white;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        
        QMenuBar::item:selected {
            background-color: #353535;
        }
        
        QMenu {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #353535;
        }
        
        QMenu::item {
            padding: 4px 16px;
        }
        
        QMenu::item:selected {
            background-color: #2a82da;
        }
        
        QToolBar {
            background-color: #2a2a2a;
            border: none;
        }
        
        QStatusBar {
            background-color: #2a2a2a;
            color: white;
        }
        
        QMessageBox {
            background-color: #353535;
        }
        
        QMessageBox QLabel {
            color: white;
        }
        
        QMessageBox QPushButton {
    """) 