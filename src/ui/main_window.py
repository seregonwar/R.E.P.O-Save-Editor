"""
Finestra principale dell'applicazione
"""

from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QToolBar, QStatusBar, QFileDialog,
    QMessageBox, QMenu, QMenuBar
)
from PyQt6.QtGui import QAction
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize
import os
import json
import sys
import copy

from .tabs import PlayerTab, InventoryTab, SettingsTab, AdvancedTab
from .styles import apply_style
from ..core.language import tr, language_manager
from ..core.backup import backup_manager


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
        
        # Inizializza l'interfaccia utente
        self.init_ui()
        
        # Registra per gli aggiornamenti della lingua
        language_manager.add_observer(self.update_translations)
        
    def set_window_icon(self):
        """Imposta l'icona della finestra"""
        try:
            # Trova il percorso dell'icona
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            icon_path = os.path.join(root_dir, "assets", "icons", "reposaveeditor.png")
            
            # Verifica se l'icona esiste
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
            else:
                print(f"Icona non trovata: {icon_path}")
        except Exception as e:
            print(f"Errore durante l'impostazione dell'icona: {str(e)}")
        
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        # Imposta le dimensioni della finestra
        self.resize(800, 600)
        
        # Crea la barra dei menu
        self.create_menu_bar()
        
        # Crea la barra degli strumenti
        self.create_toolbar()
        
        # Crea la barra di stato
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(tr("main_window.ready", "Ready"))
        
        # Crea il widget delle schede
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.setCentralWidget(self.tab_widget)
        
        # Crea le schede
        self.player_tab = PlayerTab()
        self.player_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.player_tab, tr("main_window.player_tab", "Player"))
        
        self.inventory_tab = InventoryTab()
        self.inventory_tab.status_bar = self.status_bar
        self.tab_widget.addTab(self.inventory_tab, tr("main_window.inventory_tab", "Inventory"))
        
        self.advanced_tab = AdvancedTab()
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
        
        # Menu Edit
        self.edit_menu = menu_bar.addMenu(tr("main_window.edit_menu", "Edit"))
        
        # Menu Help
        self.help_menu = menu_bar.addMenu(tr("main_window.help_menu", "Help"))
        self.about_action = QAction(tr("main_window.about_action", "About"), self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)
        
    def create_toolbar(self):
        """Crea la barra degli strumenti"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # Aggiungi le azioni alla barra degli strumenti
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        
    def open_file(self):
        """Apre un file di salvataggio"""
        try:
            # Apri il dialogo di selezione del file
            import getpass
            user = getpass.getuser()
            default_dir = fr"C:\\Users\\{user}\\AppData\\LocalLow\\semiwork\\Repo\\saves"
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                tr("main_window.open_file_dialog", "Open Save File"),
                default_dir,
                tr("main_window.save_file_filter", "Save Files (*.es3);;All Files (*)")
            )
            
            if not file_path:
                return
            
            # Prova prima la decrittazione
            from src.core.encryption import decrypt_data, EncryptionError, DataError
            try:
                save_data = decrypt_data(file_path)
            except (EncryptionError, DataError):
                # Se fallisce la decrittazione, prova come JSON normale
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        save_data = json.load(f)
                except UnicodeDecodeError:
                    QMessageBox.critical(
                        self,
                        tr("main_window.error", "Errore"),
                        tr("main_window.decode_error", "Il file selezionato non è un file di testo leggibile (UTF-8). Potrebbe essere corrotto, binario o criptato.")
                    )
                    return
                except json.JSONDecodeError:
                    QMessageBox.critical(
                        self,
                        tr("main_window.error", "Errore"),
                        tr("main_window.json_error", "Il file selezionato non contiene dati JSON validi.")
                    )
                    return
            except Exception as e:
                QMessageBox.critical(
                    self,
                    tr("main_window.open_error", "Errore apertura file"),
                    tr("main_window.open_error", f"Errore durante l'apertura o la decrittazione del file: {str(e)}")
                )
                return
            
            # Memorizza i dati
            self.save_data = save_data
            self.save_path = file_path
            
            # Aggiorna le schede
            self.player_tab.update_data(save_data)
            self.inventory_tab.update_data(save_data)
            self.advanced_tab.update_data(save_data)
            
            # Aggiorna la barra di stato
            self.status_bar.showMessage(tr("main_window.file_loaded", f"File loaded: {file_path}"))
            
            # Avvia il backup automatico
            backup_manager.start_auto_backup(file_path)
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante l'apertura del file: {str(e)}\n{traceback_str}")
            QMessageBox.critical(
                self,
                tr("general.error", "Errore"),
                tr("main_window.open_error", f"Failed to open file: {str(e)}")
            )
            
    def save_file(self):
        """Salva il file di salvataggio"""
        if not self.save_data or not self.save_path:
            self.save_file_as()
            return
            
        try:
            # Crea un backup prima di salvare
            backup_manager.create_backup(self.save_path)
            
            # Aggiorna i dati dalle schede
            old_data = copy.deepcopy(self.save_data)
            self.save_data = self.advanced_tab.save_data
            
            # Salva il file
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(self.save_data, f, indent=4)
                
            # Aggiorna la barra di stato
            self.status_bar.showMessage(tr("main_window.file_saved", f"File saved: {self.save_path}"))
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante il salvataggio del file: {str(e)}\n{traceback_str}")
            QMessageBox.critical(
                self,
                tr("general.error", "Errore"),
                tr("main_window.save_error", f"Failed to save file: {str(e)}")
            )
            
    def save_file_as(self):
        """Salva il file di salvataggio con un nuovo nome"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                tr("general.warning", "Attenzione"),
                tr("main_window.no_data", "No save data to save. Please load a save file first.")
            )
            return
            
        try:
            # Apri il dialogo di selezione del file
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                tr("main_window.save_file_dialog", "Save File"),
                "",
                tr("main_window.save_file_filter", "Save Files (*.es3);;All Files (*)")
            )
            
            if not file_path:
                return
                
            # Assicurati che il file abbia l'estensione .es3
            if not file_path.endswith(".es3"):
                file_path += ".es3"
                
            # Aggiorna i dati dalle schede
            self.save_data = self.advanced_tab.save_data
            
            # Salva il file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.save_data, f, indent=4)
                
            # Aggiorna il percorso del file
            self.save_path = file_path
            
            # Aggiorna la barra di stato
            self.status_bar.showMessage(tr("main_window.file_saved", f"File saved: {file_path}"))
            
            # Avvia il backup automatico
            backup_manager.start_auto_backup(file_path)
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante il salvataggio del file: {str(e)}\n{traceback_str}")
            QMessageBox.critical(
                self,
                tr("general.error", "Errore"),
                tr("main_window.save_error", f"Failed to save file: {str(e)}")
            )
            
    def closeEvent(self, event):
        """Gestisce la chiusura della finestra"""
        # Ferma il thread di backup automatico
        backup_manager.stop_auto_backup()
        
        # Chiedi conferma se ci sono modifiche non salvate
        if self.save_data and self.save_path:
            reply = QMessageBox.question(
                self,
                tr("main_window.confirm_exit", "Confirm Exit"),
                tr("main_window.unsaved_changes", "Do you want to save changes before exiting?"),
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            
            if reply == QMessageBox.StandardButton.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()
            
    def show_about_dialog(self):
        """Show the about window"""
        about_text = (
            "<h2>R.E.P.O Save Editor</h2>"
            "<p>Version 1.1.0</p>"
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

def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    apply_style(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
