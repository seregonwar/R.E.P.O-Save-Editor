"""Main application window"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox,
    QTabWidget, QMenuBar, QMenu, QStatusBar, QToolBar,
    QApplication
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor, QPixmap

from .tabs import (
    PlayerTab, InventoryTab, SkillsTab,
    QuestsTab, MapTab, SettingsTab
)
from ..core.encryption import encrypt_save, decrypt_save
from ..core.game_data import GameData
from ..core.save_manager import SaveManager
from ..core.error_handler import handle_error, SaveLoadError, EncryptionError, DataError

# Variabile globale per l'icona dell'applicazione
APP_ICON = None

class REPOSaveEditor(QMainWindow):
    """Main window of the save editor"""
    
    def __init__(self):
        super().__init__()
        self.save_manager = SaveManager()
        
        # Per il supporto undo/redo
        self.history = []          # Cronologia dei dati
        self.history_index = -1    # Indice della cronologia corrente
        self.max_history = 20      # Numero massimo di stati da memorizzare
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("R.E.P.O Save Editor")
        self.setMinimumSize(800, 600)
        
        # Set application icon
        if APP_ICON:
            self.setWindowIcon(APP_ICON)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Menu bar
        self.create_menu_bar()
        
        # Toolbar
        self.create_toolbar()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs and assign status bar to each
        self.player_tab = PlayerTab()
        self.player_tab.status_bar = self.status_bar
        
        self.inventory_tab = InventoryTab()
        self.inventory_tab.status_bar = self.status_bar
        
        self.quests_tab = QuestsTab()
        self.quests_tab.status_bar = self.status_bar
        
        self.skills_tab = SkillsTab()
        self.skills_tab.status_bar = self.status_bar
        
        self.map_tab = MapTab()
        self.map_tab.status_bar = self.status_bar
        
        self.settings_tab = SettingsTab()
        self.settings_tab.status_bar = self.status_bar
        
        # Add tabs to widget
        self.tab_widget.addTab(self.player_tab, "Player")
        self.tab_widget.addTab(self.inventory_tab, "Inventory")
        self.tab_widget.addTab(self.quests_tab, "Quests")
        self.tab_widget.addTab(self.skills_tab, "Skills")
        self.tab_widget.addTab(self.map_tab, "Map")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        # Footer with credits
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(10, 5, 10, 5)
        
        # Created with love by SeregonWar
        footer_label = QLabel("Created with ❤️ by SeregonWar")
        footer_label.setStyleSheet("color: #888; font-style: italic;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        footer_layout.addStretch()
        footer_layout.addWidget(footer_label)
        main_layout.addLayout(footer_layout)
        
        # Connect signals
        self.connect_signals()
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Save", self)
        open_action.triggered.connect(self.open_save)
        file_menu.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_save)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save As", self)
        save_as_action.triggered.connect(self.save_save_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # Import/Export submenu
        export_menu = file_menu.addMenu("Export")
        
        export_json_action = QAction("Export to JSON", self)
        export_json_action.triggered.connect(self.export_to_json)
        export_menu.addAction(export_json_action)
        
        import_menu = file_menu.addMenu("Import")
        
        import_json_action = QAction("Import from JSON", self)
        import_json_action.triggered.connect(self.import_from_json)
        import_menu.addAction(import_json_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("Edit")
        
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        # Help Menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Create the toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Actions
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_save)
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_save)
        toolbar.addAction(save_action)
        
        undo_action = QAction("Undo", self)
        undo_action.triggered.connect(self.undo)
        toolbar.addAction(undo_action)
        
        redo_action = QAction("Redo", self)
        redo_action.triggered.connect(self.redo)
        toolbar.addAction(redo_action)
        
    def connect_signals(self):
        """Connect signals to methods"""
        pass

    def update_tabs_with_data(self, data: Dict[str, Any]):
        """
        Update tabs with save data
        
        Args:
            data: Save data
        """
        try:
            # Update each tab with data
            if hasattr(self.player_tab, 'update_data'):
                self.player_tab.update_data(data)
                
            if hasattr(self.inventory_tab, 'update_data'):
                self.inventory_tab.update_data(data)
                
            if hasattr(self.quests_tab, 'update_data'):
                self.quests_tab.update_data(data)
                
            if hasattr(self.skills_tab, 'update_data'):
                self.skills_tab.update_data(data)
                
            if hasattr(self.map_tab, 'update_data'):
                self.map_tab.update_data(data)
                
            self.status_bar.showMessage("All tabs updated with save data")
        
        except Exception as e:
            handle_error(
                DataError(
                    "UI Update Error",
                    f"Unable to update the interface with data: {str(e)}"
                ),
                parent=self
            )
        
    def add_to_history(self, data):
        """
        Aggiunge dati alla cronologia per supportare undo/redo
        
        Args:
            data: Dati da aggiungere alla cronologia
        """
        # Se siamo in un punto diverso dall'ultimo, tronca la cronologia
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
            
        # Aggiungi una copia dei dati alla cronologia
        import copy
        self.history.append(copy.deepcopy(data))
        
        # Limita la cronologia alla dimensione massima
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        # Aggiorna l'indice
        self.history_index = len(self.history) - 1
        
    def undo(self):
        """Annulla l'ultima modifica"""
        if self.history_index > 0:
            self.history_index -= 1
            
            # Ripristina i dati dalla cronologia
            self.save_manager.current_data = self.history[self.history_index]
            
            # Aggiorna l'interfaccia con i dati ripristinati
            self.update_tabs_with_data(self.save_manager.current_data)
            
            self.status_bar.showMessage("Operazione annullata")
        else:
            self.status_bar.showMessage("Nessuna operazione da annullare")
        
    def redo(self):
        """Ripristina l'ultima operazione annullata"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            
            # Ripristina i dati dalla cronologia
            self.save_manager.current_data = self.history[self.history_index]
            
            # Aggiorna l'interfaccia con i dati ripristinati
            self.update_tabs_with_data(self.save_manager.current_data)
            
            self.status_bar.showMessage("Operazione ripristinata")
        else:
            self.status_bar.showMessage("Nessuna operazione da ripristinare")
        
    def open_save(self):
        """Open a save file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Save",
            "",
            "Save Files (*.es3);;All Files (*.*)"
        )
        
        if file_path:
            try:
                path = Path(file_path)
                data = self.save_manager.load_save(path)
                
                # Aggiunge i dati caricati alla cronologia
                self.history = []
                self.add_to_history(data)
                
                # Update tabs with data
                self.update_tabs_with_data(data)
                
                self.status_bar.showMessage(f"Save loaded: {path}")
            except Exception as e:
                handle_error(
                    SaveLoadError(
                        "Error during loading",
                        f"Cannot load the file: {str(e)}"
                    ),
                    parent=self
                )
    
    def sync_tabs_data(self):
        """
        Synchronize data from all tabs back to the SaveManager before saving
        """
        try:
            # Make sure we have current data to work with
            if not self.save_manager.current_data:
                self.status_bar.showMessage("Error: No base data to synchronize with")
                return False
                
            # Make a deep copy of the current data to work with
            import copy
            base_data = copy.deepcopy(self.save_manager.current_data)
            
            print("Inizio sincronizzazione dati dalle schede...")
            
            # Helper function to merge nested dictionaries
            def deep_update(target, source):
                print(f"Aggiornamento struttura dati")
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        # If both are dictionaries, recursively update
                        deep_update(target[key], value)
                    else:
                        # Otherwise replace/add the value
                        target[key] = value
                return target
            
            # Sync each tab's data
            tabs_with_data = []
            
            # Player tab (prioritario perché contiene dati fondamentali)
            if hasattr(self.player_tab, 'save_data') and self.player_tab.save_data:
                print("Sincronizzando dati dalla scheda Player...")
                deep_update(base_data, self.player_tab.save_data)
                tabs_with_data.append("Player")
            
            # Inventory tab    
            if hasattr(self.inventory_tab, 'save_data') and self.inventory_tab.save_data:
                print("Sincronizzando dati dalla scheda Inventory...")
                deep_update(base_data, self.inventory_tab.save_data)
                tabs_with_data.append("Inventory")
            
            # Quests tab    
            if hasattr(self.quests_tab, 'save_data') and self.quests_tab.save_data:
                print("Sincronizzando dati dalla scheda Quests...")
                deep_update(base_data, self.quests_tab.save_data)
                tabs_with_data.append("Quests")
            
            # Skills tab    
            if hasattr(self.skills_tab, 'save_data') and self.skills_tab.save_data:
                print("Sincronizzando dati dalla scheda Skills...")
                deep_update(base_data, self.skills_tab.save_data)
                tabs_with_data.append("Skills")
            
            # Map tab    
            if hasattr(self.map_tab, 'save_data') and self.map_tab.save_data:
                print("Sincronizzando dati dalla scheda Map...")
                deep_update(base_data, self.map_tab.save_data)
                tabs_with_data.append("Map")
            
            # Controlla se ci sono cambiamenti rispetto ai dati originali
            has_changes = base_data != self.save_manager.original_data
            print(f"There are changes compared to the original data: {has_changes}")
            
            # Update the SaveManager's current_data with our combined data
            self.save_manager.current_data = base_data
            
            if tabs_with_data:
                self.status_bar.showMessage(f"Data synchronized from tabs: {', '.join(tabs_with_data)}")
            else:
                self.status_bar.showMessage("Warning: No tab data to synchronize")
                
            return True
            
        except Exception as e:
            import traceback
            print(f"Sync error: {str(e)}\n{traceback.format_exc()}")
            handle_error(
                DataError(
                    "Sync Error",
                    f"Unable to synchronize data from tabs: {str(e)}"
                ),
                parent=self
            )
            return False
            
    def save_save(self):
        """Save the save"""
        if not self.save_manager.current_path:
            self.save_save_as()
            return
            
        try:
            # First synchronize data from all tabs
            if not self.sync_tabs_data():
                return
                
            # Controlliamo se i dati sono cambiati effettivamente dopo la sincronizzazione
            print("Synchronization complete, saving...")
            print(f"Save path: {self.save_manager.current_path}")
                
            # Add current state to history before saving
            self.add_to_history(self.save_manager.current_data)
            
            # Now save the synchronized data
            self.save_manager.save_save()
            self.status_bar.showMessage(f"Save saved: {self.save_manager.current_path}")
            
            # Aggiorniamo tutti i tab con i nuovi dati salvati per garantire la coerenza
            self.update_tabs_with_data(self.save_manager.current_data)
        except Exception as e:
            handle_error(
                SaveLoadError(
                    "Error during saving",
                    f"Cannot save the file: {str(e)}"
                ),
                parent=self
            )
            
    def save_save_as(self):
        """Save the save with a new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            "",
            "Save Files (*.es3);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # First synchronize data from all tabs
                if not self.sync_tabs_data():
                    return
                    
                path = Path(file_path)
                self.save_manager.save_save_as(path)
                self.status_bar.showMessage(f"Save saved as: {path}")
            except Exception as e:
                handle_error(
                    SaveLoadError(
                        "Error during saving",
                        f"Cannot save the file: {str(e)}"
                    ),
                    parent=self
                )
                
    def show_about(self):
        """Show the about window"""
        about_text = (
            "<h2>R.E.P.O Save Editor</h2>"
            "<p>Version 1.0.0</p>"
            "<p>A save editor for R.E.P.O</p>"
            "<p>Created by SeregonWar</p>"
            "<p><b>Support the developer:</b></p>"
            "<p><a href='https://ko-fi.com/seregon'>Ko-Fi</a> | "
            "<a href='https://paypal.me/seregonwar'>PayPal</a> | "
            "<a href='https://x.com/SeregonWar'>Twitter</a></p>"
        )
        
        QMessageBox.about(
            self,
            "About",
            about_text
        )

    def export_to_json(self):
        """Export save data to JSON"""
        if not self.save_manager.current_data:
            handle_error(
                DataError(
                    "No data to export",
                    "Load a save first to export it to JSON."
                ),
                parent=self
            )
            return
            
        # Request the file path for saving
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export JSON",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # Add .json extension if not present
            if not file_path.lower().endswith('.json'):
                file_path += '.json'
                
            # Save data in JSON format with readable indentation
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.save_manager.current_data, f, indent=4, ensure_ascii=False)
                
            self.status_bar.showMessage(f"Data exported to: {file_path}")
            QMessageBox.information(
                self,
                "Export Complete",
                f"The data has been successfully exported to JSON format at:\n{file_path}"
            )
        except Exception as e:
            handle_error(
                SaveLoadError(
                    "Export error",
                    f"Cannot export data: {str(e)}"
                ),
                parent=self
            )
    
    def import_from_json(self):
        """Import data from a JSON file"""
        # Request the file path to import
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import JSON",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # Load data from JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Check that data is a dictionary
            if not isinstance(data, dict):
                raise DataError(
                    "Invalid data format",
                    "The file does not contain a valid JSON object for a save."
                )
                
            # Check that the file contains essential save structures
            required_keys = ["dictionaryOfDictionaries", "playerNames", "teamName"]
            missing_keys = [key for key in required_keys if key not in data]
            
            if missing_keys:
                # Warn the user that important data might be missing
                result = QMessageBox.warning(
                    self,
                    "Incomplete Data",
                    f"The imported JSON file may not be a valid save. "
                    f"The following keys are missing: {', '.join(missing_keys)}. "
                    f"Do you want to continue anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if result == QMessageBox.StandardButton.No:
                    return
            
            # Update the save manager with the new data
            self.save_manager.current_data = data
            
            # Notify the user
            self.status_bar.showMessage(f"Data imported from: {file_path}")
            
            # Update the interface
            self.update_tabs_with_data(data)
            
            QMessageBox.information(
                self,
                "Import Complete",
                f"The data has been successfully imported from the JSON file:\n{file_path}\n\n"
                "Note: the data is only in memory. Use 'Save' or 'Save As' "
                "to create an ES3 save file."
            )
            
        except json.JSONDecodeError as e:
            handle_error(
                DataError(
                    "JSON parsing error",
                    f"The file does not contain valid JSON: {str(e)}"
                ),
                parent=self
            )
        except DataError as e:
            handle_error(e, parent=self)
        except Exception as e:
            handle_error(
                SaveLoadError(
                    "Import error",
                    f"Cannot import data: {str(e)}"
                ),
                parent=self
            )

def apply_style(app: QApplication):
    """Applies the style to the application"""
    # Set dark theme
    app.setStyle("Fusion")
    
    # Create a custom palette
    palette = QPalette()
    
    # Base colors - Using REPO theme colors (orange/dark)
    palette.setColor(QPalette.ColorRole.Window, QColor(35, 35, 35))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(45, 45, 45))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.white)
    
    # REPO Orange highlight
    highlight_color = QColor(230, 159, 0)
    palette.setColor(QPalette.ColorRole.Link, highlight_color)
    palette.setColor(QPalette.ColorRole.Highlight, highlight_color)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    
    # Disabled colors
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))
    
    # Apply the palette
    app.setPalette(palette)
    
    # Global CSS style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #232323;
        }
        
        QTabWidget::pane {
            border: 1px solid #232323;
            background: #232323;
            border-radius: 5px;
        }
        
        QTabBar::tab {
            background: #323232;
            color: white;
            padding: 8px 16px;
            border: none;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background: #E69F00;
            color: black;
            font-weight: bold;
        }
        
        QTabBar::tab:hover:!selected {
            background: #454545;
        }
        
        QPushButton {
            background-color: #E69F00;
            color: black;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #FFB21C;
        }
        
        QPushButton:pressed {
            background-color: #D18C00;
        }
        
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background-color: #323232;
            color: white;
            border: 1px solid #454545;
            padding: 6px;
            border-radius: 5px;
            selection-background-color: #E69F00;
            selection-color: black;
        }
        
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
            border: 1px solid #E69F00;
        }
        
        QComboBox::drop-down {
            border: none;
            background: #E69F00;
            width: 24px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        }
        
        QTableWidget {
            background-color: #2a2a2a;
            color: white;
            gridline-color: #454545;
            border: 1px solid #454545;
            border-radius: 5px;
            alternate-background-color: #323232;
        }
        
        QTableWidget::item {
            padding: 6px;
        }
        
        QTableWidget::item:selected {
            background-color: #E69F00;
            color: black;
        }
        
        QHeaderView::section {
            background-color: #323232;
            color: white;
            padding: 6px;
            font-weight: bold;
            border: none;
            border-bottom: 1px solid #454545;
        }
        
        QMenuBar {
            background-color: #2a2a2a;
            color: white;
            border-bottom: 1px solid #454545;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 6px 12px;
        }
        
        QMenuBar::item:selected {
            background-color: #E69F00;
            color: black;
        }
        
        QMenu {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #454545;
        }
        
        QMenu::item {
            padding: 6px 24px;
        }
        
        QMenu::item:selected {
            background-color: #E69F00;
            color: black;
        }
        
        QToolBar {
            background-color: #2a2a2a;
            border: none;
            spacing: 6px;
            padding: 3px;
        }
        
        QToolBar::separator {
            width: 1px;
            background-color: #454545;
            margin: 0 6px;
        }
        
        QStatusBar {
            background-color: #2a2a2a;
            color: white;
            border-top: 1px solid #454545;
            padding: 2px;
        }
        
        QMessageBox {
            background-color: #323232;
        }
        
        QMessageBox QLabel {
            color: white;
        }
        
        QMessageBox QPushButton {
            min-width: 100px;
            min-height: 30px;
        }
        
        QGroupBox {
            background-color: #2a2a2a;
            border: 1px solid #454545;
            border-radius: 5px;
            padding-top: 15px;
            font-weight: bold;
            margin-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 5px;
            background-color: #2a2a2a;
            color: #E69F00;
        }
        
        QLabel {
            color: white;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #2a2a2a;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #E69F00;
            min-height: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #2a2a2a;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #E69F00;
            min-width: 20px;
            border-radius: 6px;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            border: none;
            background: none;
            width: 0px;
        }
    """)

def main():
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Apply material theme
    apply_style(app)
    
    # Import application icon DOPO aver creato QApplication
    global APP_ICON
    try:
        # Get the application root directory from environment, or use the current file's directory
        root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        # First try to load icon from PNG file
        icon_path = os.path.join(root_dir, "assets", "icons", "reposaveeditor.png")
        APP_ICON = QIcon(icon_path) if os.path.exists(icon_path) else None
        
        # If PNG loading fails, load a default icon
        if not APP_ICON or APP_ICON.isNull():
            # Non utilizziamo più app_icon.py
            default_icon = QIcon()
            APP_ICON = default_icon
    except Exception as e:
        print(f"Warning: Could not load application icon: {e}")
        APP_ICON = None
    
    # Load application icon
    if APP_ICON:
        app.setWindowIcon(APP_ICON)
    
    window = REPOSaveEditor()
    window.show()
    
    sys.exit(app.exec()) 