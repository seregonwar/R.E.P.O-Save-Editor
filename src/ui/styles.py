"""
Stili per l'interfaccia grafica di R.E.P.O Save Editor
"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor

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
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    
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
            background-color: #f0a30a;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
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
            background-color: #f0a30a;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        
        QComboBox {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #2a2a2a;
            padding: 4px;
            border-radius: 4px;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox QAbstractItemView {
            background-color: #2a2a2a;
            color: white;
            selection-background-color: #2a82da;
        }
        
        QGroupBox {
            border: 1px solid #2a2a2a;
            border-radius: 4px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 3px;
            color: white;
        }
        
        QCheckBox {
            color: white;
        }
        
        QCheckBox::indicator {
            width: 13px;
            height: 13px;
        }
        
        QRadioButton {
            color: white;
        }
        
        QRadioButton::indicator {
            width: 13px;
            height: 13px;
        }
        
        QTextEdit {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #2a2a2a;
            border-radius: 4px;
        }
        
        QScrollBar:vertical {
            background-color: #2a2a2a;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #5a5a5a;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #2a2a2a;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #5a5a5a;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """)
