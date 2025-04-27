"""
Finestra principale dell'applicazione
"""

import sys
import os
import json
import logging
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDoubleSpinBox, QFileDialog, 
    QFrame, QFormLayout, QGridLayout, QGroupBox, QHeaderView,
    QHBoxLayout, QLabel, QLineEdit, QListWidget, QMainWindow,
    QMenu, QMessageBox, QProgressBar, QPushButton, QScrollArea,
    QSplitter, QSizePolicy, QSpinBox, QTextEdit, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget, QToolBar,
    QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QColor, QSyntaxHighlighter, QTextCharFormat, QFont, QAction
from pathlib import Path

from ui.styles import apply_style
from ui.components.modern_widgets import ModernButton, ModernLineEdit, ModernLabel
from ui.tabs import PlayerTab, InventoryTab, AdvancedTab, SettingsTab
from utils.save_manager import SaveManager
from core import language_manager, tr

# Configurazione del logger per questo modulo
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Finestra principale dell'applicazione"""
    
    def __init__(self):
        super().__init__()
            
        # Imposta il titolo della finestra
        self.setWindowTitle("R.E.P.O Save Editor")
        
        # Imposta l'icona della finestra
        self.set_window_icon()
        
        # Dati del salvataggio
        self.save_data = None
        self.save_path = None
        
        # Manager for save operations
        self.save_manager = SaveManager()
        
        # Inizializza l'interfaccia utente
        self.init_ui()
        
        # Registra per gli aggiornamenti della lingua
        language_manager.add_observer(self.update_translations)
        
    def set_window_icon(self):
        """Imposta l'icona della finestra"""
        try:
            # Trova il percorso dell'icona
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            icon_path = os.path.join(root_dir, "assets", "icons", "reposaveeditor.png")
            
            # Verifica se l'icona esiste
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                logger.warning(f"Icona non trovata: {icon_path}")
        except Exception as e:
            logger.error(f"Errore durante l'impostazione dell'icona: {str(e)}")
        
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.resize(1000, 700)  # Dimensione maggiore per la nuova UI
        
        # Creazione menu e toolbar
        self.create_menu_bar()
        self.create_toolbar()
        
        # Barra di stato
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("main_window.ready", "Ready"))
        
        # Tab widget per i contenuti
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)  # Aspetto più moderno
        self.setCentralWidget(self.tab_widget)
        
        # Centralizzazione dati: assicuriamoci che save_data sia inizializzato
        if self.save_data is None:
            self.save_data = {}
            
        # Inizializzazione dei tab
        self.player_tab = PlayerTab(self.save_data)
        self.player_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.player_tab, tr("main_window.player_tab", "Player"))
        
        self.inventory_tab = InventoryTab(self.save_data)
        self.inventory_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.inventory_tab, tr("main_window.inventory_tab", "Inventory"))
        
        self.advanced_tab = AdvancedTab(self.save_data)
        self.advanced_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.advanced_tab, tr("main_window.advanced_tab", "Advanced"))
        
        self.settings_tab = SettingsTab()
        self.settings_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.settings_tab, tr("main_window.settings_tab", "Settings"))
        
    def update_translations(self):
        """Aggiorna le traduzioni dell'interfaccia quando cambia la lingua"""
        # Aggiorna il titolo delle schede
        self.tab_widget.setTabText(0, tr("main_window.player_tab", "Player"))
        self.tab_widget.setTabText(1, tr("main_window.inventory_tab", "Inventory"))
        self.tab_widget.setTabText(2, tr("main_window.advanced_tab", "Advanced"))
        self.tab_widget.setTabText(3, tr("main_window.settings_tab", "Settings"))
        
        # Aggiorna le azioni del menu
        self.file_menu.setTitle(tr("main_window.file_menu", "File"))
        self.edit_menu.setTitle(tr("main_window.edit_menu", "Edit"))
        self.help_menu.setTitle(tr("main_window.help_menu", "Help"))
        
        self.open_action.setText(tr("main_window.open_action", "Open"))
        self.save_action.setText(tr("main_window.save_action", "Save"))
        self.save_as_action.setText(tr("main_window.save_as_action", "Save As"))
        self.about_action.setText(tr("main_window.about_action", "About"))
        
        # Aggiorna la barra di stato
        if self.save_path:
            self.status_bar.showMessage(tr("main_window.file_loaded", f"File loaded: {self.save_path}"))
        else:
            self.status_bar.showMessage(tr("main_window.ready", "Ready"))
        
    def create_menu_bar(self):
        """Crea la barra dei menu"""
        menu_bar = self.menuBar()
        
        # Menu File
        self.file_menu = menu_bar.addMenu(tr("main_window.file_menu", "File"))
        
        self.open_action = QAction(tr("main_window.open_action", "Open"), self)
        self.open_action.triggered.connect(self.open_file)
        self.file_menu.addAction(self.open_action)
        
        self.save_action = QAction(tr("main_window.save_action", "Save"), self)
        self.save_action.triggered.connect(self.save_file)
        self.file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction(tr("main_window.save_as_action", "Save As"), self)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.file_menu.addAction(self.save_as_action)
        
        # Menu Edit
        self.edit_menu = menu_bar.addMenu(tr("main_window.edit_menu", "Edit"))
        
        # Menu Help
        self.help_menu = menu_bar.addMenu(tr("main_window.help_menu", "Help"))
        self.about_action = QAction(tr("main_window.about_action", "About"), self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)
        
    def create_toolbar(self):
        """Crea la barra degli strumenti moderna"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))  # Icone più grandi per un aspetto moderno
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #232323;
                spacing: 5px;
                padding: 5px;
                border: none;
            }
            
            QToolButton {
                background-color: #323232;
                border-radius: 4px;
                padding: 5px;
            }
            
            QToolButton:hover {
                background-color: #3d3d3d;
            }
            
            QToolButton:pressed {
                background-color: #f0a30a;
            }
        """)
        self.addToolBar(toolbar)
        
        # Aggiungi le azioni alla barra degli strumenti
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.save_as_action)
        toolbar.addSeparator()
        
        # Crea un'azione per mostrare il profilo utente
        root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        user_icon_path = os.path.join(root_dir, "assets", "icons", "user.png")
        
        if os.path.exists(user_icon_path):
            self.user_profile_action = QAction(QIcon(user_icon_path), tr("main_window.user_profile", "User Profile"), self)
            self.user_profile_action.triggered.connect(self.show_user_profile)
            toolbar.addAction(self.user_profile_action)
            
    def open_file(self):
        """Apre un file di salvataggio"""
        try:
            import getpass
            user = getpass.getuser()
            default_dir = fr"C:\\Users\\{user}\\AppData\\LocalLow\\semiwork\\Repo\\saves"
            
            dialog = QFileDialog(self)
            dialog.setWindowTitle(tr("main_window.open_file_dialog", "Open Save File"))
            dialog.setDirectory(default_dir)
            dialog.setNameFilter(tr("main_window.save_file_filter", "Save Files (*.es3);;All Files (*.*)"))
            dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
            # Imposta il filtro per mostrare tutti i file inizialmente
            dialog.selectNameFilter("All Files (*.*)")
            
            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_paths = dialog.selectedFiles()
                if file_paths:
                    file_path = file_paths[0]
                    logger.info(f"Richiesta apertura file: {file_path}")
                    
                    self.save_manager = SaveManager()
                    success, message = self.save_manager.open_file(file_path)
                    if not success:
                        logger.error(f"Errore apertura file da GUI: {message}")
                        QMessageBox.critical(
                            self,
                            tr("main_window.open_error", "Errore apertura file"),
                            tr("main_window.open_error_message", f"Errore durante l'apertura: {message}")
                        )
                        return
                    
                    # Ottieni i dati dal SaveManager
                    save_data = self.save_manager.json_data
                    logger.info(f"File caricato in GUI: {file_path}")
                    
                    # Memorizza i dati
                    self.save_data = save_data
                    self.save_path = file_path
                    
                    # Aggiorna la barra di stato
                    self.status_bar.showMessage(tr("main_window.file_loaded", f"File loaded: {file_path}"))
                    
                    # Aggiorna i dati nei tab
                    self.player_tab.save_data = save_data
                    self.inventory_tab.save_data = save_data
                    self.advanced_tab.save_data = save_data
                    
                    # Popola la UI dai dati caricati
                    try:
                        logger.info("Aggiornamento tab giocatore")
                        self.player_tab.refresh_ui_from_data()
                    except Exception as e:
                        logger.error(f"Errore aggiornamento tab giocatore: {str(e)}")
                        
                    try:
                        logger.info("Aggiornamento tab inventario")
                        self.inventory_tab.refresh_ui_from_data()
                    except Exception as e:
                        logger.error(f"Errore aggiornamento tab inventario: {str(e)}")
                        
                    try:
                        logger.info("Aggiornamento tab avanzato")
                        self.advanced_tab.refresh_ui_from_data()
                    except Exception as e:
                        logger.error(f"Errore aggiornamento tab avanzato: {str(e)}")
                    
                    # Notifica l'utente
                    QMessageBox.information(
                        self,
                        tr("main_window.file_loaded_title", "File caricato"),
                        tr("main_window.file_loaded_message", f"File caricato con successo: {file_path}")
                    )
                else:
                    logger.info("Apertura file annullata dall'utente.")
            else:
                logger.info("Apertura file annullata dall'utente.")
        except Exception as e:
            logger.error(f"Errore inatteso durante l'apertura: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(
                self,
                tr("main_window.open_error", "Errore apertura file"),
                tr("main_window.open_error_message", f"Errore durante l'apertura: {str(e)}")
            )
        
    def save_file(self):
        """Salva le modifiche nel file corrente"""
        if not self.save_path:
            return self.save_file_as()
            
        try:
            # Aggiorna i dati con le modifiche dalle diverse schede
            # Prima sincronizza le modifiche dell'advanced tab poiché gestisce direttamente il JSON
            if hasattr(self.advanced_tab, 'update_json_from_ui'):
                self.advanced_tab.update_json_from_ui()
                
            # Aggiorna il save_manager con i dati correnti
            self.save_manager.json_data = self.save_data
            self.save_manager.save_data = self.save_data
            
            # Salva il file
            success, message = self.save_manager.save_file(self.save_path)
            if not success:
                logger.error(f"Errore durante il salvataggio: {message}")
                QMessageBox.critical(
                    self, 
                    tr("main_window.save_error", "Errore di salvataggio"),
                    tr("main_window.save_error_message", f"Errore durante il salvataggio: {message}")
                )
                return False
                
            self.status_bar.showMessage(tr("main_window.file_saved", f"File saved: {self.save_path}"))
            return True
        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {str(e)}")
            QMessageBox.critical(
                self, 
                tr("main_window.save_error", "Errore di salvataggio"),
                tr("main_window.save_error_message", f"Errore durante il salvataggio: {str(e)}")
            )
            return False
    
    def save_file_as(self):
        """Salva le modifiche in un nuovo file"""
        try:
            dialog = QFileDialog(self)
            dialog.setWindowTitle(tr("main_window.save_file_dialog", "Save File As"))
            dialog.setNameFilter(tr("main_window.save_file_filter", "Save Files (*.es3);;All Files (*.*)"))
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
            dialog.setDefaultSuffix("es3")
            # Imposta il filtro per mostrare tutti i file inizialmente
            dialog.selectNameFilter("All Files (*.*)")
            
            if dialog.exec() == QFileDialog.DialogCode.Accepted:
                file_paths = dialog.selectedFiles()
                if file_paths:
                    file_path = file_paths[0]
                    
                    # Se non ha estensione .es3, aggiungerla
                    if not file_path.lower().endswith('.es3'):
                        file_path += '.es3'
                    
                    # Aggiorna il percorso corrente
                    self.save_path = file_path
                    
                    # Salva nel nuovo percorso
                    return self.save_file()
                else:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Errore durante il salvataggio: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            QMessageBox.critical(
                self, 
                tr("main_window.save_error", "Errore di salvataggio"),
                tr("main_window.save_error_message", f"Errore durante il salvataggio: {str(e)}")
            )
            return False
        
    def closeEvent(self, event):
        """Gestisce la chiusura dell'applicazione"""
        reply = QMessageBox.question(
            self, 
            tr("main_window.confirm_exit", "Confirm Exit"),
            tr("main_window.confirm_exit_message", "Are you sure you want to exit? Unsaved changes will be lost."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()
            
    def show_about_dialog(self):
        """Mostra la finestra di dialogo About"""
        QMessageBox.about(
            self,
            tr("main_window.about_title", "About R.E.P.O Save Editor"),
            tr("main_window.about_text", 
               "<h2>R.E.P.O Save Editor</h2>"
               "<p>Version 3.0.0</p>"
               "<p>A save editor for R.E.P.O</p>"
               "<p>Created by SeregonWar</p>"
               "<p><b>Support the developer:</b></p>"
               "<p><a href='https://ko-fi.com/seregon'>Ko-Fi</a> | "
               "<a href='https://paypal.me/seregonwar'>PayPal</a> | "
               "<a href='https://x.com/SeregonWar'>Twitter</a></p>")
        )

    def show_user_profile(self):
        """Mostra il profilo utente"""
        QMessageBox.information(
            self,
            tr("main_window.user_profile", "User Profile"),
            tr("main_window.user_profile_text", "User profile feature coming soon!")
        )

def main():
    """Funzione principale per l'avvio dell'applicazione dalla nuova UI"""
    app = QApplication(sys.argv)
    apply_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
