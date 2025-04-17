"""Tab dell'interfaccia principale"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QProgressBar, QScrollArea, QGroupBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
    QGridLayout, QCheckBox, QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QColor
from typing import Dict, Any
import os
import json
import requests
from io import BytesIO
import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path

class BaseTab(QWidget):
    """Tab base con funzionalità comuni"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Inizializza l'interfaccia utente"""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        
    def show_error(self, message):
        """Mostra un messaggio di errore"""
        QMessageBox.critical(self, "Errore", message)
        
    def show_info(self, message):
        """Mostra un messaggio informativo"""
        QMessageBox.information(self, "Informazione", message)

class PlayerTab(QWidget):
    """Tab for player data management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = None
        self.player_data = {}
        self.players = {}  # Dictionary of available players
        self.current_player_id = None  # ID of currently selected player
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selettore giocatore (partecipante)
        player_select_layout = QHBoxLayout()
        player_select_layout.addWidget(QLabel("Seleziona Giocatore:"))
        
        self.player_selector = QComboBox()
        self.player_selector.currentIndexChanged.connect(self.on_player_changed)
        player_select_layout.addWidget(self.player_selector)
        
        layout.addLayout(player_select_layout)
        
        # Top section with player info and avatar
        top_layout = QHBoxLayout()
        
        # Player info form
        info_form = QFormLayout()
        
        
        self.player_level = QSpinBox()
        self.player_level.setRange(1, 100)
        info_form.addRow("Level:", self.player_level)
        
        self.player_health = QSpinBox()
        self.player_health.setRange(1, 10000)
        info_form.addRow("Health:", self.player_health)
        
        self.player_money = QDoubleSpinBox()
        self.player_money.setRange(0, 1000000)
        self.player_money.setSingleStep(100)
        info_form.addRow("Money:", self.player_money)
        
        info_widget = QWidget()
        info_widget.setLayout(info_form)
        
        # Player avatar
        avatar_layout = QVBoxLayout()
        
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.avatar_label.setStyleSheet("background-color: #1a1a1a; border-radius: 50px;")
        
        # Imposta un placeholder invece dell'icona - il caricamento avverrà più tardi
        self.avatar_label.setText("No Image")
        
        avatar_layout.addWidget(self.avatar_label)
        
        steam_id_layout = QHBoxLayout()
        self.steam_id_edit = QLineEdit()
        self.steam_id_edit.setPlaceholderText("Steam ID (autodection)")
        self.steam_id_edit.setReadOnly(True)  # Steam ID non modificabile
        self.steam_id_edit.setStyleSheet("background-color: #2a2a2a;")
        steam_id_layout.addWidget(self.steam_id_edit)
        
        self.load_avatar_button = QPushButton("Reload Avatar")
        self.load_avatar_button.clicked.connect(self.load_steam_avatar)
        steam_id_layout.addWidget(self.load_avatar_button)
        
        avatar_layout.addLayout(steam_id_layout)
        
        # Add info and avatar to top layout
        top_layout.addLayout(avatar_layout)
        top_layout.addWidget(info_widget, 1)  # 1 is the stretch factor
        
        layout.addLayout(top_layout)
        
        # Stats group
        stats_group = QGroupBox("Player Stats")
        stats_layout = QFormLayout()
        
        self.player_strength = QSpinBox()
        self.player_strength.setRange(1, 100)
        stats_layout.addRow("Strength:", self.player_strength)
        
        self.player_agility = QSpinBox()
        self.player_agility.setRange(1, 100)
        stats_layout.addRow("Agility:", self.player_agility)
        
        self.player_intelligence = QSpinBox()
        self.player_intelligence.setRange(1, 100)
        stats_layout.addRow("Intelligence:", self.player_intelligence)
        
        self.player_endurance = QSpinBox()
        self.player_endurance.setRange(1, 100)
        stats_layout.addRow("Endurance:", self.player_endurance)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Save button
        save_button = QPushButton("Save Changes")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)
        
        self.setLayout(layout)
        
        # Carica l'avatar default quando il widget è mostrato
        self.show_default_avatar()
        
    def on_player_changed(self, index):
        """Gestisce il cambio di giocatore selezionato"""
        if index < 0 or not self.save_data:
            return
            
        # Non chiamare save_changes qui, per evitare problemi quando si cambia selezione
        # ma teniamo traccia del player_id precedente se disponibile
        previous_player_id = self.current_player_id
            
        # Ottieni l'ID del giocatore selezionato
        player_id = self.player_selector.itemData(index)
        self.current_player_id = player_id
        
        # Aggiorna l'interfaccia con i dati del giocatore selezionato
        self.update_player_data(player_id)
        
    def update_player_data(self, player_id):
        """Aggiorna l'interfaccia con i dati del giocatore selezionato"""
        if not player_id or not self.save_data:
            return
            
        try:
            # Aggiorna l'ID del giocatore corrente
            self.current_player_id = player_id
            
            # Debug: mostra l'ID del giocatore
            print(f"Aggiornamento dati per il giocatore ID={player_id}")
            
            # Aggiorna il nome del giocatore
            if "playerNames" in self.save_data and player_id in self.save_data["playerNames"]:
                player_name_data = self.save_data["playerNames"][player_id]
                # Usa la funzione extract_player_name per ottenere un nome leggibile
                display_name = self.extract_player_name(player_name_data, player_id)
                self.player_name.setText(display_name)
            
            # Estrai dati del giocatore dalla struttura dictionaryOfDictionaries
            if "dictionaryOfDictionaries" in self.save_data:
                dict_data = self.save_data["dictionaryOfDictionaries"]
                if isinstance(dict_data, dict) and "value" in dict_data:
                    dict_data = dict_data["value"]
                
                # Strutture dati per ogni statistiche del giocatore
                player_data_structures = [
                    "playerHealth", "playerUpgradeHealth", "playerUpgradeStamina", 
                    "playerUpgradeExtraJump", "playerUpgradeLaunch", "playerUpgradeMapPlayerCount",
                    "playerUpgradeSpeed", "playerUpgradeStrength", "playerUpgradeRange", 
                    "playerUpgradeThrow"
                ]
                
                # Estrai i dati del giocatore da ogni struttura
                player_stats = {}
                for stat_key in player_data_structures:
                    if stat_key in dict_data and player_id in dict_data[stat_key]:
                        player_stats[stat_key] = dict_data[stat_key][player_id]
                
                # Debug: mostra le statistiche trovate
                print(f"Statistiche trovate per il giocatore {player_id}: {list(player_stats.keys())}")
                
                # Aggiorna i controlli UI con le statistiche del giocatore
                if "playerHealth" in player_stats:
                    health_value = self.extract_value(player_stats["playerHealth"], 100)
                    self.player_health.setValue(health_value)
                    
                if "playerUpgradeHealth" in player_stats:
                    self.player_strength.setValue(self.extract_value(player_stats.get("playerUpgradeHealth"), 10))
                
                if "playerUpgradeStamina" in player_stats:
                    self.player_agility.setValue(self.extract_value(player_stats.get("playerUpgradeStamina"), 10))
                
                if "playerUpgradeStrength" in player_stats:
                    self.player_intelligence.setValue(self.extract_value(player_stats.get("playerUpgradeStrength"), 10))
                
                if "playerUpgradeSpeed" in player_stats:
                    self.player_endurance.setValue(self.extract_value(player_stats.get("playerUpgradeSpeed"), 10))
                
                # Aggiorna il livello da runStats
                if "runStats" in dict_data and "level" in dict_data["runStats"]:
                    self.player_level.setValue(self.extract_value(dict_data["runStats"]["level"], 1))
                    print(f"Livello giocatore impostato a: {self.player_level.value()}")
                
                if "runStats" in dict_data and "currency" in dict_data["runStats"]:
                    self.player_money.setValue(self.extract_value(dict_data["runStats"]["currency"], 0))
                    print(f"Soldi giocatore impostati a: {self.player_money.value()}")
                
                # Memorizza i dati del giocatore per uso futuro
                self.player_data = player_stats
            
            # Cerca lo Steam ID e carica l'avatar
            self.find_and_set_steam_id(player_id)
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante l'aggiornamento dei dati del giocatore: {str(e)}\n{traceback_str}")
            QMessageBox.warning(
                self,
                "Errore aggiornamento dati",
                f"Impossibile aggiornare i dati del giocatore: {str(e)}"
            )
    
    def find_and_set_steam_id(self, player_id):
        """Cerca e imposta lo Steam ID per il giocatore specificato"""
        steam_id = None
        
        try:
            # Controlla se l'ID del giocatore è già un ID Steam (inizia con 7656119)
            if player_id and str(player_id).startswith("7656119") and len(str(player_id)) >= 17:
                print(f"L'ID giocatore {player_id} è già un ID Steam")
                steam_id = player_id
            else:
                # Cerchiamo di recuperare lo Steam ID in modo simile a come fa name.py
                if "dictionaryOfDictionaries" in self.save_data:
                    dict_data = self.save_data["dictionaryOfDictionaries"]
                    if isinstance(dict_data, dict) and "value" in dict_data:
                        dict_data = dict_data["value"]
                    
                        # name.py utilizza i seguenti passaggi:
                        # 1. Cerca nelle strutture dati dei giocatori
                        player_structures = ["playerMetadata", "userProfiles", "steamProfiles", "steamIds"]
                        for structure in player_structures:
                            if structure in dict_data and player_id in dict_data[structure]:
                                data = dict_data[structure][player_id]
                                if isinstance(data, str) and data.isdigit() and len(data) >= 17:
                                    steam_id = data
                                    break
                                elif isinstance(data, dict):
                                    # Cerca nelle sottostrutture
                                    for k, v in data.items():
                                        if (k == "steamId" or k == "steam_id" or k == "id") and isinstance(v, (str, int)):
                                            steam_id = str(v)
                                            break
                
                        # 2. Se non trovato, cerca un ID che sembra un Steam ID (un numero di 17+ cifre che inizia con 7656119)
                        if not steam_id:
                            for structure_name, structure in dict_data.items():
                                if isinstance(structure, dict) and player_id in structure:
                                    value = structure[player_id]
                                    if isinstance(value, str) and value.isdigit() and len(value) >= 17 and value.startswith("7656119"):
                                        steam_id = value
                                        break
                
                # 3. Se ancora non trovato, utilizza un approccio più generale
                if not steam_id:
                    # Funzione per verificare se un valore sembra un SteamID64
                    def looks_like_steam_id(value):
                        if isinstance(value, (str, int)):
                            value_str = str(value)
                            # Verifica se è un lungo numero che inizia con 7656119 (SteamID64)
                            if value_str.isdigit() and len(value_str) >= 17 and value_str.startswith("7656119"):
                                return True
                        return False
                    
                    # Cerca ricorsivamente in tutta la struttura dati
                    def find_steam_id_in_dict(d, depth=0, max_depth=3):
                        if depth > max_depth or not isinstance(d, dict):
                            return None
                            
                        for k, v in d.items():
                            if looks_like_steam_id(v):
                                return v
                            elif isinstance(v, dict):
                                result = find_steam_id_in_dict(v, depth + 1, max_depth)
                                if result:
                                    return result
                        return None
                    
                    steam_id = find_steam_id_in_dict(self.save_data)
            
            # Se abbiamo trovato uno Steam ID, imposta il campo e carica l'avatar
            if steam_id:
                print(f"Steam ID trovato per il giocatore {player_id}: {steam_id}")
                self.steam_id_edit.setText(str(steam_id))
                self.load_steam_avatar()
            else:
                print(f"Nessun Steam ID trovato per il giocatore {player_id}")
                self.steam_id_edit.setText("")
                self.show_default_avatar()
                
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante la ricerca dello Steam ID: {str(e)}\n{traceback_str}")
            self.steam_id_edit.setText("")
            self.show_default_avatar()
            
    def show_default_avatar(self):
        """Mostra l'avatar default quando il widget è pronto"""
        try:
            # Try to load from PNG file first
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            icon_path = os.path.join(root_dir, "assets", "icons", "reposaveeditor.png")
            
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                self.avatar_label.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            else:
                # Non utilizziamo più app_icon.py
                self.avatar_label.setText("No Image")
        except Exception as e:
            print(f"Warning: Could not load avatar image: {e}")
            self.avatar_label.setText("No Image")

    def load_steam_avatar(self):
        """Load the Steam avatar for the provided Steam ID"""
        import requests
        import os
        import xml.etree.ElementTree as ElementTree
        from pathlib import Path
        
        # Create cache directory if it doesn't exist
        cache_dir = Path(os.environ.get("REPO_SAVE_EDITOR_ROOT", 
                       os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))) / "cache"
        if not cache_dir.exists():
            os.makedirs(cache_dir)
        
        steam_id = self.steam_id_edit.text().strip()
        if not steam_id:
            # If steam ID field is empty, try to use current player ID
            if self.current_player_id and str(self.current_player_id).startswith("7656119"):
                steam_id = self.current_player_id
                self.steam_id_edit.setText(str(steam_id))
            else:
                # Try to extract Steam ID from ES3 file
                if self.save_data and "dictionaryOfDictionaries" in self.save_data:
                    try:
                        # Automatic extraction of Steam ID from ES3 file
                        dict_data = self.save_data["dictionaryOfDictionaries"]
                        if isinstance(dict_data, dict) and "value" in dict_data:
                            dict_data = dict_data["value"]
                            
                            # Look for a value that looks like a Steam ID
                            for key, items in dict_data.items():
                                if isinstance(items, dict):
                                    for id_key, value in items.items():
                                        if isinstance(value, str) and value.isdigit() and len(value) >= 17 and value.startswith("7656119"):
                                            steam_id = value
                                            self.steam_id_edit.setText(steam_id)
                                            break
                                    if steam_id:
                                        break
                    except Exception as e:
                        print(f"Error extracting Steam ID: {e}")
                
                if not steam_id:
                    self.status_bar.showMessage("No Steam ID found for this player")
                    return
        
        self.status_bar.showMessage(f"Loading Steam avatar for {steam_id}...")
            
        try:
            # Check cache first
            cached_image_path = cache_dir / f"{steam_id}.png"
            
            if cached_image_path.exists():
                # Use cached image
                pixmap = QPixmap(str(cached_image_path))
                self.avatar_label.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
                self.status_bar.showMessage("Steam avatar loaded from local cache")
                return
            
            # Not in cache, download using XML API
            url = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                try:
                    tree = ElementTree.fromstring(response.content)
                    avatar_element = tree.find('avatarFull')  # Use full size avatar
                    
                    if avatar_element is not None:
                        img_url = avatar_element.text
                        img_response = requests.get(img_url, timeout=10)
                        
                        if img_response.status_code == 200:
                            # Save image to cache
                            with open(cached_image_path, 'wb') as file:
                                file.write(img_response.content)
                            
                            # Show image
                            avatar_image = QImage.fromData(img_response.content)
                            pixmap = QPixmap.fromImage(avatar_image)
                            self.avatar_label.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            
                            # Save Steam ID in player data
                            if self.save_data and self.current_player_id:
                                if "playerMetadata" not in self.save_data:
                                    self.save_data["playerMetadata"] = {}
                                
                                if self.current_player_id not in self.save_data["playerMetadata"]:
                                    self.save_data["playerMetadata"][self.current_player_id] = {}
                                
                                # Check if it's already a dictionary or create a new one
                                if not isinstance(self.save_data["playerMetadata"][self.current_player_id], dict):
                                    self.save_data["playerMetadata"][self.current_player_id] = {}
                                
                                self.save_data["playerMetadata"][self.current_player_id]["steamId"] = steam_id
                            
                            self.status_bar.showMessage("Steam avatar loaded successfully")
                            return
                except Exception as e:
                    print(f"Error processing Steam XML: {e}")
            
            # Fallback to direct URL if XML API fails
            avatar_url = f"https://avatars.steamstatic.com/{steam_id}_full.jpg"
            avatar_response = requests.get(avatar_url, timeout=5)
            
            if avatar_response.status_code == 200:
                # Save image to cache
                with open(cached_image_path, 'wb') as file:
                    file.write(avatar_response.content)
                
                # Show image
                avatar_image = QImage.fromData(avatar_response.content)
                pixmap = QPixmap.fromImage(avatar_image)
                self.avatar_label.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
                # Update Steam ID
                if self.save_data and self.current_player_id:
                    if "playerMetadata" not in self.save_data:
                        self.save_data["playerMetadata"] = {}
                    
                    if self.current_player_id not in self.save_data["playerMetadata"]:
                        self.save_data["playerMetadata"][self.current_player_id] = {}
                    
                    if not isinstance(self.save_data["playerMetadata"][self.current_player_id], dict):
                        self.save_data["playerMetadata"][self.current_player_id] = {}
                    
                    self.save_data["playerMetadata"][self.current_player_id]["steamId"] = steam_id
                
                self.status_bar.showMessage("Steam avatar loaded using direct URL")
                return
            
            # If we get here, all attempts failed, use default icon
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            icon_path = os.path.join(root_dir, "assets", "icons", "reposaveeditor.png")
            
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path)
                self.avatar_label.setPixmap(pixmap.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                
                # Still update Steam ID if available
                if self.save_data and self.current_player_id and steam_id:
                    if "playerMetadata" not in self.save_data:
                        self.save_data["playerMetadata"] = {}
                    
                    if self.current_player_id not in self.save_data["playerMetadata"]:
                        self.save_data["playerMetadata"][self.current_player_id] = {}
                    
                    if not isinstance(self.save_data["playerMetadata"][self.current_player_id], dict):
                        self.save_data["playerMetadata"][self.current_player_id] = {}
                    
                    self.save_data["playerMetadata"][self.current_player_id]["steamId"] = steam_id
            else:
                self.avatar_label.setText("No Image")
            
            self.status_bar.showMessage("Steam API unreachable, using application icon as avatar")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error loading avatar: {str(e)}")
            self.avatar_label.setText("Avatar Error")
        
    def save_changes(self):
        """Save changes to player data"""
        if not self.save_data or not self.current_player_id:
            QMessageBox.warning(
                self,
                "No Data Loaded",
                "No save data to update. Please load a save file first."
            )
            return
            
        try:
            print(f"Salvando modifiche per il giocatore {self.current_player_id}...")
            
            # Assicuriamoci che le strutture dati necessarie esistano
            if "dictionaryOfDictionaries" not in self.save_data:
                self.save_data["dictionaryOfDictionaries"] = {"value": {}}
            elif "value" not in self.save_data["dictionaryOfDictionaries"]:
                self.save_data["dictionaryOfDictionaries"]["value"] = {}
                
            dict_data = self.save_data["dictionaryOfDictionaries"]["value"]
            
            # Assicuriamoci che le strutture per le statistiche del player esistano
            if "playerStats" not in self.save_data:
                self.save_data["playerStats"] = {}
                
            if self.current_player_id not in self.save_data["playerStats"]:
                self.save_data["playerStats"][self.current_player_id] = {}
            
            stats = self.save_data["playerStats"][self.current_player_id]
            
            # Assicuriamoci che esista runStats
            if "runStats" not in dict_data:
                dict_data["runStats"] = {}
                
            # Dati da modificare
            level = self.player_level.value()
            health = self.player_health.value()
            money = self.player_money.value()
            strength = self.player_strength.value()
            agility = self.player_agility.value()
            intelligence = self.player_intelligence.value()
            endurance = self.player_endurance.value()
            
            # Log dei valori da salvare
            print(f"Valori da salvare - Livello: {level}, Salute: {health}, Soldi: {money}")
            print(f"Statistiche - Forza: {strength}, Agilità: {agility}, Intelligenza: {intelligence}, Resistenza: {endurance}")
            
            # Update stats in the data
            # Prima proviamo a salvare nelle strutture statistiche appropriate
            # Nel dizionario principale (dictionaryOfDictionaries)
            
            # Aggiorna il livello nel runStats
            dict_data["runStats"]["level"] = level
            
            # Aggiorna la valuta nel runStats
            dict_data["runStats"]["currency"] = money
            
            # Aggiorna la salute
            if "playerHealth" not in dict_data:
                dict_data["playerHealth"] = {}
            dict_data["playerHealth"][self.current_player_id] = health
            
            # Aggiorna le statistiche del personaggio
            stat_mappings = {
                "playerUpgradeHealth": strength,
                "playerUpgradeStamina": agility,
                "playerUpgradeStrength": intelligence,
                "playerUpgradeSpeed": endurance
            }
            
            for stat_key, value in stat_mappings.items():
                if stat_key not in dict_data:
                    dict_data[stat_key] = {}
                dict_data[stat_key][self.current_player_id] = value
            
            # Aggiorna il playerStats (struttura separata)
            stats_to_update = {
                "level": level,
                "health": health,
                "money": money,
                "strength": strength,
                "agility": agility,
                "intelligence": intelligence,
                "endurance": endurance
            }
            
            for key, value in stats_to_update.items():
                stats[key] = value
            
            # Add Steam ID to save data if available
            steam_id = self.steam_id_edit.text().strip()
            if steam_id:
                # Store Steam ID in the appropriate place in the save
                if "playerMetadata" not in self.save_data:
                    self.save_data["playerMetadata"] = {}
                
                if self.current_player_id not in self.save_data["playerMetadata"]:
                    self.save_data["playerMetadata"][self.current_player_id] = {}
                
                # Controlla se è già un dizionario o crea uno nuovo
                if not isinstance(self.save_data["playerMetadata"][self.current_player_id], dict):
                    self.save_data["playerMetadata"][self.current_player_id] = {}
                
                self.save_data["playerMetadata"][self.current_player_id]["steamId"] = steam_id
            
            # Conferma del salvataggio
            print("Modifiche applicate con successo al modello di dati")
            self.status_bar.showMessage("Modifiche salvate con successo")
            
            QMessageBox.information(
                self,
                "Success",
                "Player data updated successfully!"
            )
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Errore durante il salvataggio: {str(e)}\n{error_trace}")
            QMessageBox.critical(
                self,
                "Error Saving Data",
                f"An error occurred while saving player data: {str(e)}"
            )
    
    def update_data(self, data: Dict[str, Any]):
        """
        Update the tab with save data
        
        Args:
            data: Save data
        """
        try:
            self.save_data = data
            self.player_data = {}
            self.players = {}
            
            # Clear the player selector
            self.player_selector.clear()
            
            # Extract player names and populate the selector
            if "playerNames" in data:
                # In R.E.P.O. playerNames può essere:
                # 1. Dizionario con player_id -> nome
                # 2. Dizionario con player_id -> oggetto C# Dictionary (structure complessa)
                # 3. Oggetto con valore in "value"
                
                # Se playerNames ha una proprietà "value", usa quella
                player_names_data = data["playerNames"]
                if isinstance(player_names_data, dict) and "value" in player_names_data:
                    player_names_data = player_names_data["value"]
                
                # Ora iteriamo sui giocatori
                for player_id, player_name in player_names_data.items():
                    # Estrai il nome del giocatore dalla struttura
                    display_name = self.extract_player_name(player_name, player_id)
                    
                    # Memorizza e aggiunge al selettore
                    self.players[player_id] = display_name
                    self.player_selector.addItem(display_name, player_id)
                    
                    # Debug
                    print(f"Giocatore trovato: ID={player_id}, Nome={display_name}, Dato originale={player_name}")
            
            # Se ci sono giocatori, seleziona il primo e carica i suoi dati
            if self.player_selector.count() > 0:
                self.player_selector.setCurrentIndex(0)
                
            # Altrimenti mostra un messaggio
            else:
                QMessageBox.warning(
                    self,
                    "Nessun giocatore",
                    "Nessun giocatore trovato nel salvataggio."
                )
                
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante l'aggiornamento dei dati: {str(e)}\n{traceback_str}")
            QMessageBox.warning(
                self,
                "Data Update Error",
                f"Failed to update player data: {str(e)}"
            )

    def extract_player_name(self, player_name_data, player_id):
        """Estrae il nome del giocatore da varie strutture possibili"""
        # Caso 1: Stringa semplice
        if isinstance(player_name_data, str):
            return player_name_data
            
        # Caso 2: Dizionario con "value"
        elif isinstance(player_name_data, dict) and "value" in player_name_data:
            value = player_name_data["value"]
            if isinstance(value, str):
                return value
            elif isinstance(value, dict):
                # Prova a estrarre il primo valore come nome
                first_val = next(iter(value.values()), None)
                if first_val:
                    return str(first_val)
        
        # Caso 3: Dizionario C# serializzato 
        # (Se contiene "System.Collections.Generic.Dictionary", è un riferimento a un oggetto C#)
        elif isinstance(player_name_data, str) and "System.Collections.Generic.Dictionary" in player_name_data:
            # Prova a estrarre un nome leggibile
            match = re.search(r'\[\[(.*?)\]\]', player_name_data)
            if match:
                return match.group(1)
        
        # Caso fallback: se il valore è un dizionario, prova a prendere il primo valore
        elif isinstance(player_name_data, dict):
            # Prendi il primo valore come nome
            first_val = next(iter(player_name_data.values()), None)
            if first_val and isinstance(first_val, str):
                return first_val
            # Altrimenti prendi la prima chiave
            first_key = next(iter(player_name_data.keys()), None)
            if first_key:
                return str(first_key)
                
        # Fallback sicuro: usa l'ID del giocatore
        return f"Giocatore {player_id}"

    def extract_value(self, data, default_value=0):
        """Estrae un valore numerico da varie strutture dati possibili"""
        if isinstance(data, (int, float)):
            return data
        elif isinstance(data, dict) and "value" in data:
            # A volte i valori sono incapsulati in un dizionario con chiave "value"
            return self.extract_value(data["value"], default_value)
        elif isinstance(data, dict) and len(data) > 0:
            # Prova a estrarre il primo valore utile da un dizionario
            for k, v in data.items():
                if isinstance(v, (int, float)):
                    return v
            # Se non trova valori numerici, restituisce il default
            return default_value
        elif isinstance(data, str) and data.isdigit():
            # Converti stringhe numeriche
            return int(data)
        else:
            return default_value

class InventoryTab(QWidget):
    """Tab for inventory management"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = None
        self.inventory_data = {}
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Description"])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.inventory_table)
        
        # Edit panel
        edit_group = QGroupBox("Edit Item")
        edit_layout = QFormLayout()
        
        self.item_id_edit = QLineEdit()
        self.item_id_edit.setReadOnly(True)
        edit_layout.addRow("ID:", self.item_id_edit)
        
        self.item_name_edit = QLineEdit()
        edit_layout.addRow("Name:", self.item_name_edit)
        
        self.item_quantity_spin = QSpinBox()
        self.item_quantity_spin.setRange(0, 9999)
        edit_layout.addRow("Quantity:", self.item_quantity_spin)
        
        self.item_description_edit = QLineEdit()
        edit_layout.addRow("Description:", self.item_description_edit)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Item")
        self.add_button.clicked.connect(self.add_item)
        buttons_layout.addWidget(self.add_button)
        
        self.update_button = QPushButton("Update Item")
        self.update_button.clicked.connect(self.update_item)
        buttons_layout.addWidget(self.update_button)
        
        self.remove_button = QPushButton("Remove Item")
        self.remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.remove_button)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.inventory_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self):
        """Gestisce il cambio di selezione nella tabella"""
        selected_rows = self.inventory_table.selectedItems()
        if not selected_rows:
            return
            
        # Prendi la prima riga selezionata
        row = selected_rows[0].row()
        
        # Recupera i dati dell'oggetto dalla tabella
        item_id = self.inventory_table.item(row, 0).text()
        item_name = self.inventory_table.item(row, 1).text()
        item_quantity = int(self.inventory_table.item(row, 2).text())
        item_description = self.inventory_table.item(row, 3).text()
        
        # Aggiorna i campi di modifica
        self.item_id_edit.setText(item_id)
        self.item_name_edit.setText(item_name)
        self.item_quantity_spin.setValue(item_quantity)
        self.item_description_edit.setText(item_description)
        
    def update_data(self, data: Dict[str, Any]):
        """
        Aggiorna i dati dell'inventario
        
        Args:
            data: Dati del salvataggio
        """
        try:
            self.save_data = data
            self.inventory_data = {}
            
            # Pulisci la tabella
            self.inventory_table.setRowCount(0)
            
            # Cerca i dati dell'inventario nel salvataggio
            if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
                dict_of_dicts = data["dictionaryOfDictionaries"]["value"]
                
                # Cerca le chiavi relative all'inventario
                inventory_keys = [key for key in dict_of_dicts.keys() if "inventory" in key.lower() or "item" in key.lower()]
                
                if inventory_keys:
                    for key in inventory_keys:
                        items = dict_of_dicts[key]
                        for item_id, item_value in items.items():
                            # Cerca informazioni aggiuntive sull'oggetto
                            item_name = f"Oggetto {item_id}"
                            item_description = ""
                            
                            # Controlla se esiste un dizionario con i nomi degli oggetti
                            if "itemNames" in dict_of_dicts and item_id in dict_of_dicts["itemNames"]:
                                item_name = dict_of_dicts["itemNames"][item_id]
                                
                            # Controlla se esiste un dizionario con le descrizioni degli oggetti
                            if "itemDescriptions" in dict_of_dicts and item_id in dict_of_dicts["itemDescriptions"]:
                                item_description = dict_of_dicts["itemDescriptions"][item_id]
                                
                            # Salva i dati dell'oggetto
                            self.inventory_data[item_id] = {
                                "name": item_name,
                                "quantity": item_value,
                                "description": item_description,
                                "source_key": key
                            }
                            
                            # Aggiungi alla tabella
                            self.add_item_to_table(item_id, item_name, item_value, item_description)
                else:
                    # Se non ci sono chiavi specifiche per l'inventario, cerca altri elementi
                    # che potrebbero essere interpretati come oggetti
                    
                    # Esempi di strutture che potrebbero contenere oggetti:
                    general_items = {}
                    
                    if "playerItems" in dict_of_dicts:
                        general_items.update(dict_of_dicts["playerItems"])
                        
                    if "collectibles" in dict_of_dicts:
                        general_items.update(dict_of_dicts["collectibles"])
                        
                    if "resources" in dict_of_dicts:
                        general_items.update(dict_of_dicts["resources"])
                    
                    # Aggiungi gli oggetti trovati
                    for item_id, item_value in general_items.items():
                        item_name = f"Oggetto {item_id}"
                        item_description = ""
                        
                        self.inventory_data[item_id] = {
                            "name": item_name,
                            "quantity": item_value if isinstance(item_value, int) else 1,
                            "description": item_description,
                            "source_key": "generalItems"
                        }
                        
                        # Aggiungi alla tabella
                        self.add_item_to_table(
                            item_id, 
                            item_name, 
                            item_value if isinstance(item_value, int) else 1, 
                            item_description
                        )
                        
            # Se non ci sono oggetti, mostra un messaggio
            if not self.inventory_data:
                QMessageBox.information(
                    self,
                    "Inventario vuoto",
                    "Nessun oggetto trovato nel salvataggio o la struttura dell'inventario non è supportata."
                )
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Errore di Aggiornamento",
                f"Impossibile aggiornare i dati dell'inventario: {str(e)}"
            )
            
    def add_item_to_table(self, item_id, name, quantity, description):
        """
        Aggiunge un oggetto alla tabella
        
        Args:
            item_id: ID dell'oggetto
            name: Nome dell'oggetto
            quantity: Quantità dell'oggetto
            description: Descrizione dell'oggetto
        """
        row = self.inventory_table.rowCount()
        self.inventory_table.insertRow(row)
        
        # Imposta i dati nelle celle
        self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
        self.inventory_table.setItem(row, 1, QTableWidgetItem(str(name)))
        self.inventory_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
        self.inventory_table.setItem(row, 3, QTableWidgetItem(str(description)))
        
    def add_item(self):
        """Aggiunge un nuovo oggetto all'inventario"""
        # Genera un nuovo ID (puoi adottare una strategia migliore se necessario)
        import random
        new_id = f"item_{random.randint(1000, 9999)}"
        
        # Crea un nuovo oggetto con valori predefiniti
        self.inventory_data[new_id] = {
            "name": "Nuovo Oggetto",
            "quantity": 1,
            "description": "Descrizione dell'oggetto",
            "source_key": "playerItems"
        }
        
        # Aggiungi alla tabella
        self.add_item_to_table(
            new_id,
            "Nuovo Oggetto",
            1,
            "Descrizione dell'oggetto"
        )
        
        # Seleziona la nuova riga
        self.inventory_table.selectRow(self.inventory_table.rowCount() - 1)
        
        QMessageBox.information(
            self, 
            "Oggetto Aggiunto", 
            f"Nuovo oggetto aggiunto con ID: {new_id}"
        )
        
    def update_item(self):
        """Aggiorna i dati di un oggetto selezionato"""
        # Controlla se c'è un ID valido
        item_id = self.item_id_edit.text()
        if not item_id or item_id not in self.inventory_data:
            QMessageBox.warning(
                self,
                "Errore di Aggiornamento",
                "Seleziona prima un oggetto valido dalla tabella."
            )
            return
            
        # Aggiorna i dati in memoria
        self.inventory_data[item_id]["name"] = self.item_name_edit.text()
        self.inventory_data[item_id]["quantity"] = self.item_quantity_spin.value()
        self.inventory_data[item_id]["description"] = self.item_description_edit.text()
        
        # Aggiorna la tabella
        for row in range(self.inventory_table.rowCount()):
            if self.inventory_table.item(row, 0).text() == item_id:
                self.inventory_table.setItem(row, 1, QTableWidgetItem(self.item_name_edit.text()))
                self.inventory_table.setItem(row, 2, QTableWidgetItem(str(self.item_quantity_spin.value())))
                self.inventory_table.setItem(row, 3, QTableWidgetItem(self.item_description_edit.text()))
                break
                
        QMessageBox.information(
            self,
            "Oggetto Aggiornato",
            f"Oggetto {item_id} aggiornato con successo."
        )
        
    def remove_item(self):
        """Rimuove un oggetto dall'inventario"""
        # Controlla se c'è un ID valido
        item_id = self.item_id_edit.text()
        if not item_id or item_id not in self.inventory_data:
            QMessageBox.warning(
                self,
                "Errore di Rimozione",
                "Seleziona prima un oggetto valido dalla tabella."
            )
            return
            
        # Conferma la rimozione
        reply = QMessageBox.question(
            self,
            "Conferma Rimozione",
            f"Sei sicuro di voler rimuovere l'oggetto {item_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Rimuovi dalla struttura dati
            del self.inventory_data[item_id]
            
            # Rimuovi dalla tabella
            for row in range(self.inventory_table.rowCount()):
                if self.inventory_table.item(row, 0).text() == item_id:
                    self.inventory_table.removeRow(row)
                    break
                    
            # Pulisci i campi di modifica
            self.item_id_edit.clear()
            self.item_name_edit.clear()
            self.item_quantity_spin.setValue(0)
            self.item_description_edit.clear()
            
            QMessageBox.information(
                self,
                "Oggetto Rimosso",
                f"Oggetto {item_id} rimosso con successo."
            )
        
    def save_changes(self):
        """Salva le modifiche all'inventario"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                "Nessun dato caricato",
                "Non ci sono dati da salvare. Carica prima un salvataggio."
            )
            return
            
        try:
            # Aggiorna i dati del salvataggio
            for item_id, item_data in self.inventory_data.items():
                source_key = item_data["source_key"]
                quantity = item_data["quantity"]
                
                # Assicurati che la struttura dati esista
                if "dictionaryOfDictionaries" in self.save_data and "value" in self.save_data["dictionaryOfDictionaries"]:
                    dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
                    
                    # Crea il dizionario se non esiste
                    if source_key not in dict_of_dicts:
                        dict_of_dicts[source_key] = {}
                        
                    # Aggiorna la quantità
                    dict_of_dicts[source_key][item_id] = quantity
                    
                    # Aggiorna nome e descrizione se possibile
                    if "itemNames" in dict_of_dicts:
                        dict_of_dicts["itemNames"][item_id] = item_data["name"]
                        
                    if "itemDescriptions" in dict_of_dicts:
                        dict_of_dicts["itemDescriptions"][item_id] = item_data["description"]
            
            QMessageBox.information(
                self,
                "Salvate modifiche",
                "Le modifiche all'inventario sono state salvate nel salvataggio."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore di salvataggio",
                f"Si è verificato un errore durante il salvataggio: {str(e)}"
            )

class QuestsTab(QWidget):
    """Tab per la gestione delle missioni"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = None
        self.quests_data = {}
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabella missioni
        self.quests_table = QTableWidget()
        self.quests_table.setColumnCount(4)
        self.quests_table.setHorizontalHeaderLabels(["ID", "Nome", "Stato", "Azioni"])
        self.quests_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.quests_table)
        
        # Aggiunta di un pannello di modifica sotto la tabella
        edit_group = QGroupBox("Modifica Missione")
        edit_layout = QFormLayout()
        
        self.quest_id_edit = QLineEdit()
        self.quest_id_edit.setReadOnly(True)
        edit_layout.addRow("ID:", self.quest_id_edit)
        
        self.quest_name_edit = QLineEdit()
        edit_layout.addRow("Nome:", self.quest_name_edit)
        
        self.quest_status_combo = QComboBox()
        self.quest_status_combo.addItems(["Non completata", "Completata"])
        edit_layout.addRow("Stato:", self.quest_status_combo)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.complete_button = QPushButton("Completa Missione")
        self.complete_button.clicked.connect(self.complete_quest)
        buttons_layout.addWidget(self.complete_button)
        
        self.reset_button = QPushButton("Reset Missione")
        self.reset_button.clicked.connect(self.reset_quest)
        buttons_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connetti segnali
        self.quests_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self):
        """Gestisce il cambio di selezione nella tabella"""
        selected_rows = self.quests_table.selectedItems()
        if not selected_rows:
            return
            
        # Prendi la prima riga selezionata
        row = selected_rows[0].row()
        
        # Recupera i dati della missione dalla tabella
        quest_id = self.quests_table.item(row, 0).text()
        quest_name = self.quests_table.item(row, 1).text()
        quest_status = self.quests_table.item(row, 2).text()
        
        # Aggiorna i campi di modifica
        self.quest_id_edit.setText(quest_id)
        self.quest_name_edit.setText(quest_name)
        self.quest_status_combo.setCurrentText(quest_status)
        
    def complete_quest(self):
        """Completa una missione"""
        # Controlla se c'è un ID valido
        quest_id = self.quest_id_edit.text()
        if not quest_id or quest_id not in self.quests_data:
            QMessageBox.warning(
                self,
                "Errore di Completamento",
                "Seleziona prima una missione valida dalla tabella."
            )
            return
            
        # Imposta lo stato della missione a "Completata"
        self.quest_status_combo.setCurrentText("Completata")
        
        # Aggiorna la tabella
        for row in range(self.quests_table.rowCount()):
            if self.quests_table.item(row, 0).text() == quest_id:
                self.quests_table.setItem(row, 2, QTableWidgetItem("Completata"))
                break
        
        QMessageBox.information(self, "Completamento", "Missione completata!")
        
    def reset_quest(self):
        """Resetta una missione"""
        # Controlla se c'è un ID valido
        quest_id = self.quest_id_edit.text()
        if not quest_id or quest_id not in self.quests_data:
            QMessageBox.warning(
                self,
                "Errore di Reset",
                "Seleziona prima una missione valida dalla tabella."
            )
            return
            
        # Imposta lo stato della missione a "Non completata"
        self.quest_status_combo.setCurrentText("Non completata")
        
        # Aggiorna la tabella
        for row in range(self.quests_table.rowCount()):
            if self.quests_table.item(row, 0).text() == quest_id:
                self.quests_table.setItem(row, 2, QTableWidgetItem("Non completata"))
                break
                
        QMessageBox.information(self, "Reset", "Missione resettata!")
        
    def save_changes(self):
        """Salva le modifiche alle missioni"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                "Nessun dato caricato",
                "Non ci sono dati da salvare. Carica prima un salvataggio."
            )
            return
            
        # Controlla se c'è un ID valido
        quest_id = self.quest_id_edit.text()
        if not quest_id or quest_id not in self.quests_data:
            QMessageBox.warning(
                self,
                "Errore di Salvataggio",
                "Seleziona prima una missione valida dalla tabella."
            )
            return
            
        try:
            # Aggiorna i dati in memoria
            quest_name = self.quest_name_edit.text()
            quest_status = self.quest_status_combo.currentText() == "Completata"
            
            # Aggiorna l'oggetto quests_data
            self.quests_data[quest_id]["name"] = quest_name
            self.quests_data[quest_id]["status"] = quest_status
            
            # Aggiorna la tabella
            for row in range(self.quests_table.rowCount()):
                if self.quests_table.item(row, 0).text() == quest_id:
                    self.quests_table.setItem(row, 1, QTableWidgetItem(quest_name))
                    self.quests_table.setItem(row, 2, QTableWidgetItem("Completata" if quest_status else "Non completata"))
                    break
            
            # Aggiorna i dati del salvataggio
            if "dictionaryOfDictionaries" in self.save_data and "value" in self.save_data["dictionaryOfDictionaries"]:
                dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
                
                source_key = self.quests_data[quest_id]["source_key"]
                
                # Assicurati che il dizionario esista
                if source_key not in dict_of_dicts:
                    dict_of_dicts[source_key] = {}
                    
                # Aggiorna lo stato della missione
                dict_of_dicts[source_key][quest_id] = quest_status
                
                # Aggiorna anche il nome se possibile
                if "questNames" in dict_of_dicts:
                    dict_of_dicts["questNames"][quest_id] = quest_name
            
            QMessageBox.information(
                self,
                "Successo",
                "Modifiche salvate con successo!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore di salvataggio",
                f"Si è verificato un errore durante il salvataggio: {str(e)}"
            )
        
    def update_data(self, data: Dict[str, Any]):
        """
        Aggiorna i dati delle missioni
        
        Args:
            data: Dati del salvataggio
        """
        try:
            self.save_data = data
            self.quests_data = {}
            
            # Pulisci la tabella
            self.quests_table.setRowCount(0)
            
            # Cerca i dati delle missioni nel salvataggio
            if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
                dict_of_dicts = data["dictionaryOfDictionaries"]["value"]
                
                # Cerca le chiavi relative alle missioni
                quest_keys = [key for key in dict_of_dicts.keys() if "quest" in key.lower() or "mission" in key.lower()]
                
                if quest_keys:
                    for key in quest_keys:
                        quests = dict_of_dicts[key]
                        for quest_id, quest_value in quests.items():
                            # Cerca informazioni aggiuntive sulla missione
                            quest_name = f"Missione {quest_id}"
                            quest_status = "Completata" if quest_value else "Non completata"
                            
                            # Controlla se esiste un dizionario con i nomi delle missioni
                            if "questNames" in dict_of_dicts and quest_id in dict_of_dicts["questNames"]:
                                quest_name = dict_of_dicts["questNames"][quest_id]
                            
                            # Salva i dati della missione
                            self.quests_data[quest_id] = {
                                "name": quest_name,
                                "status": quest_value,
                                "source_key": key
                            }
                            
                            # Aggiungi alla tabella
                            self.add_quest_to_table(quest_id, quest_name, quest_status)
                else:
                    # Se non ci sono chiavi specifiche per le missioni, cerca altri elementi
                    # che potrebbero essere interpretati come missioni
                    
                    # Esempi di strutture che potrebbero contenere missioni:
                    general_quests = {}
                    
                    if "playerQuests" in dict_of_dicts:
                        general_quests.update(dict_of_dicts["playerQuests"])
                        
                    if "missions" in dict_of_dicts:
                        general_quests.update(dict_of_dicts["missions"])
                    
                    # Aggiungi le missioni trovate
                    for quest_id, quest_value in general_quests.items():
                        quest_name = f"Missione {quest_id}"
                        quest_status = "Completata" if quest_value else "Non completata"
                        
                        self.quests_data[quest_id] = {
                            "name": quest_name,
                            "status": quest_value,
                            "source_key": "generalQuests"
                        }
                        
                        # Aggiungi alla tabella
                        self.add_quest_to_table(quest_id, quest_name, quest_status)
                        
            # Se non ci sono missioni, mostra un messaggio
            if not self.quests_data:
                QMessageBox.information(
                    self,
                    "Nessuna missione",
                    "Nessuna missione trovata nel salvataggio o la struttura delle missioni non è supportata."
                )
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Errore di Aggiornamento",
                f"Impossibile aggiornare i dati delle missioni: {str(e)}"
            )
            
    def add_quest_to_table(self, quest_id, name, status):
        """
        Aggiunge una missione alla tabella
        
        Args:
            quest_id: ID della missione
            name: Nome della missione
            status: Stato della missione
        """
        row = self.quests_table.rowCount()
        self.quests_table.insertRow(row)
        
        # Imposta i dati nelle celle
        self.quests_table.setItem(row, 0, QTableWidgetItem(str(quest_id)))
        self.quests_table.setItem(row, 1, QTableWidgetItem(str(name)))
        self.quests_table.setItem(row, 2, QTableWidgetItem(str(status)))
        
        # Pulsante azioni (opzionale)
        action_cell = QTableWidgetItem("Modifica")
        self.quests_table.setItem(row, 3, action_cell)

class SkillsTab(QWidget):
    """Tab per la gestione delle abilità"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = None
        self.skills_data = {}
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tabella abilità
        self.skills_table = QTableWidget()
        self.skills_table.setColumnCount(4)
        self.skills_table.setHorizontalHeaderLabels(["ID", "Nome", "Livello", "Azioni"])
        self.skills_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.skills_table)
        
        # Aggiunta di un pannello di modifica sotto la tabella
        edit_group = QGroupBox("Modifica Abilità")
        edit_layout = QFormLayout()
        
        self.skill_id_edit = QLineEdit()
        self.skill_id_edit.setReadOnly(True)
        edit_layout.addRow("ID:", self.skill_id_edit)
        
        self.skill_name_edit = QLineEdit()
        edit_layout.addRow("Nome:", self.skill_name_edit)
        
        self.skill_level_spin = QSpinBox()
        self.skill_level_spin.setRange(0, 100)
        edit_layout.addRow("Livello:", self.skill_level_spin)
        
        edit_group.setLayout(edit_layout)
        layout.addWidget(edit_group)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.level_up_button = QPushButton("Aumenta Livello")
        self.level_up_button.clicked.connect(self.level_up_skill)
        buttons_layout.addWidget(self.level_up_button)
        
        self.reset_button = QPushButton("Reset Abilità")
        self.reset_button.clicked.connect(self.reset_skill)
        buttons_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Salva Modifiche")
        self.save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connetti segnali
        self.skills_table.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self):
        """Gestisce il cambio di selezione nella tabella"""
        selected_rows = self.skills_table.selectedItems()
        if not selected_rows:
            return
            
        # Prendi la prima riga selezionata
        row = selected_rows[0].row()
        
        # Recupera i dati dell'abilità dalla tabella
        skill_id = self.skills_table.item(row, 0).text()
        skill_name = self.skills_table.item(row, 1).text()
        skill_level = int(self.skills_table.item(row, 2).text())
        
        # Aggiorna i campi di modifica
        self.skill_id_edit.setText(skill_id)
        self.skill_name_edit.setText(skill_name)
        self.skill_level_spin.setValue(skill_level)
        
    def level_up_skill(self):
        """Aumenta il livello di un'abilità"""
        # Controlla se c'è un ID valido
        skill_id = self.skill_id_edit.text()
        if not skill_id or skill_id not in self.skills_data:
            QMessageBox.warning(
                self,
                "Errore di Aggiornamento",
                "Seleziona prima un'abilità valida dalla tabella."
            )
            return
            
        # Aggiorna il livello
        current_level = self.skill_level_spin.value()
        if current_level < 100:  # Limite massimo
            self.skill_level_spin.setValue(current_level + 1)
            
            # Aggiorna la tabella
            for row in range(self.skills_table.rowCount()):
                if self.skills_table.item(row, 0).text() == skill_id:
                    self.skills_table.setItem(row, 2, QTableWidgetItem(str(current_level + 1)))
                    break
            
            QMessageBox.information(self, "Livello", "Abilità potenziata al livello " + str(current_level + 1))
        else:
            QMessageBox.information(self, "Livello Massimo", "Questa abilità è già al livello massimo!")
        
    def reset_skill(self):
        """Resetta un'abilità"""
        # Controlla se c'è un ID valido
        skill_id = self.skill_id_edit.text()
        if not skill_id or skill_id not in self.skills_data:
            QMessageBox.warning(
                self,
                "Errore di Reset",
                "Seleziona prima un'abilità valida dalla tabella."
            )
            return
            
        # Imposta il livello a 1
        self.skill_level_spin.setValue(1)
        
        # Aggiorna la tabella
        for row in range(self.skills_table.rowCount()):
            if self.skills_table.item(row, 0).text() == skill_id:
                self.skills_table.setItem(row, 2, QTableWidgetItem("1"))
                break
                
        QMessageBox.information(self, "Reset", "Abilità resettata al livello 1!")
        
    def save_changes(self):
        """Salva le modifiche alle abilità"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                "Nessun dato caricato",
                "Non ci sono dati da salvare. Carica prima un salvataggio."
            )
            return
            
        # Controlla se c'è un ID valido
        skill_id = self.skill_id_edit.text()
        if not skill_id or skill_id not in self.skills_data:
            QMessageBox.warning(
                self,
                "Errore di Salvataggio",
                "Seleziona prima un'abilità valida dalla tabella."
            )
            return
            
        try:
            # Aggiorna i dati in memoria
            skill_name = self.skill_name_edit.text()
            skill_level = self.skill_level_spin.value()
            
            # Aggiorna l'oggetto skills_data
            self.skills_data[skill_id]["name"] = skill_name
            self.skills_data[skill_id]["level"] = skill_level
            
            # Aggiorna la tabella
            for row in range(self.skills_table.rowCount()):
                if self.skills_table.item(row, 0).text() == skill_id:
                    self.skills_table.setItem(row, 1, QTableWidgetItem(skill_name))
                    self.skills_table.setItem(row, 2, QTableWidgetItem(str(skill_level)))
                    break
            
            # Aggiorna i dati del salvataggio
            if "dictionaryOfDictionaries" in self.save_data and "value" in self.save_data["dictionaryOfDictionaries"]:
                dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
                
                source_key = self.skills_data[skill_id]["source_key"]
                
                # Assicurati che il dizionario esista
                if source_key not in dict_of_dicts:
                    dict_of_dicts[source_key] = {}
                    
                # Aggiorna il livello dell'abilità
                dict_of_dicts[source_key][skill_id] = skill_level
                
                # Aggiorna anche il nome se possibile
                if "skillNames" in dict_of_dicts:
                    dict_of_dicts["skillNames"][skill_id] = skill_name
            
            QMessageBox.information(
                self,
                "Successo",
                "Modifiche salvate con successo!"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Errore di salvataggio",
                f"Si è verificato un errore durante il salvataggio: {str(e)}"
            )
        
    def update_data(self, data: Dict[str, Any]):
        """
        Aggiorna i dati delle abilità
        
        Args:
            data: Dati del salvataggio
        """
        try:
            self.save_data = data
            self.skills_data = {}
            
            # Pulisci la tabella
            self.skills_table.setRowCount(0)
            
            # Cerca i dati delle abilità nel salvataggio
            if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
                dict_of_dicts = data["dictionaryOfDictionaries"]["value"]
                
                # Cerca le chiavi relative alle abilità
                skill_keys = [key for key in dict_of_dicts.keys() if "skill" in key.lower() or "ability" in key.lower()]
                
                if skill_keys:
                    for key in skill_keys:
                        skills = dict_of_dicts[key]
                        for skill_id, skill_value in skills.items():
                            # Cerca informazioni aggiuntive sull'abilità
                            skill_name = f"Abilità {skill_id}"
                            skill_level = skill_value if isinstance(skill_value, int) else 1
                            
                            # Controlla se esiste un dizionario con i nomi delle abilità
                            if "skillNames" in dict_of_dicts and skill_id in dict_of_dicts["skillNames"]:
                                skill_name = dict_of_dicts["skillNames"][skill_id]
                            
                            # Salva i dati dell'abilità
                            self.skills_data[skill_id] = {
                                "name": skill_name,
                                "level": skill_level,
                                "source_key": key
                            }
                            
                            # Aggiungi alla tabella
                            self.add_skill_to_table(skill_id, skill_name, skill_level)
                else:
                    # Se non ci sono chiavi specifiche per le abilità, cerca altri elementi
                    # che potrebbero essere interpretati come abilità
                    
                    # Esempi di strutture che potrebbero contenere abilità:
                    general_skills = {}
                    
                    if "playerSkills" in dict_of_dicts:
                        general_skills.update(dict_of_dicts["playerSkills"])
                        
                    if "abilities" in dict_of_dicts:
                        general_skills.update(dict_of_dicts["abilities"])
                    
                    # Aggiungi le abilità trovate
                    for skill_id, skill_value in general_skills.items():
                        skill_name = f"Abilità {skill_id}"
                        skill_level = skill_value if isinstance(skill_value, int) else 1
                        
                        self.skills_data[skill_id] = {
                            "name": skill_name,
                            "level": skill_level,
                            "source_key": "generalSkills"
                        }
                        
                        # Aggiungi alla tabella
                        self.add_skill_to_table(skill_id, skill_name, skill_level)
                        
            # Se non ci sono abilità, mostra un messaggio
            if not self.skills_data:
                QMessageBox.information(
                    self,
                    "Nessuna abilità",
                    "Nessuna abilità trovata nel salvataggio o la struttura delle abilità non è supportata."
                )
                
        except Exception as e:
            QMessageBox.warning(
                self,
                "Errore di Aggiornamento",
                f"Impossibile aggiornare i dati delle abilità: {str(e)}"
            )
            
    def add_skill_to_table(self, skill_id, name, level):
        """
        Aggiunge un'abilità alla tabella
        
        Args:
            skill_id: ID dell'abilità
            name: Nome dell'abilità
            level: Livello dell'abilità
        """
        row = self.skills_table.rowCount()
        self.skills_table.insertRow(row)
        
        # Imposta i dati nelle celle
        self.skills_table.setItem(row, 0, QTableWidgetItem(str(skill_id)))
        self.skills_table.setItem(row, 1, QTableWidgetItem(str(name)))
        self.skills_table.setItem(row, 2, QTableWidgetItem(str(level)))
        
        # Pulsante azioni (opzionale)
        action_cell = QTableWidgetItem("Modifica")
        self.skills_table.setItem(row, 3, action_cell)

class MapTab(QWidget):
    """Tab per la visualizzazione e modifica della mappa"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.save_data = None
        self.map_areas = {}  # Dictionary of map areas {id: {name, status, coordinates}}
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Map viewer with selection area
        map_group = QGroupBox("Map View")
        map_layout = QVBoxLayout()
        
        # Map visualization
        self.map_view = QLabel()
        self.map_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.map_view.setMinimumHeight(300)
        self.map_view.setStyleSheet("background-color: #1a1a1a; border-radius: 5px;")
        map_layout.addWidget(self.map_view)
        
        # Areas table
        self.areas_table = QTableWidget()
        self.areas_table.setColumnCount(4)
        self.areas_table.setHorizontalHeaderLabels(["ID", "Name", "Status", "Actions"])
        self.areas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        map_layout.addWidget(self.areas_table)
        
        # Pannello di modifica delle aree
        area_group = QGroupBox("Modifica Area")
        area_layout = QFormLayout()
        
        self.area_id_edit = QLineEdit()
        self.area_id_edit.setReadOnly(True)
        area_layout.addRow("ID:", self.area_id_edit)
        
        self.area_name_edit = QLineEdit()
        area_layout.addRow("Name:", self.area_name_edit)
        
        self.area_status_combo = QComboBox()
        self.area_status_combo.addItems(["Locked", "Unlocked", "Completed"])
        area_layout.addRow("Status:", self.area_status_combo)
        
        # Area coordinates
        coords_layout = QHBoxLayout()
        
        self.area_x_spin = QSpinBox()
        self.area_x_spin.setRange(-1000, 1000)
        coords_layout.addWidget(QLabel("X:"))
        coords_layout.addWidget(self.area_x_spin)
        
        self.area_y_spin = QSpinBox()
        self.area_y_spin.setRange(-1000, 1000)
        coords_layout.addWidget(QLabel("Y:"))
        coords_layout.addWidget(self.area_y_spin)
        
        # Create a container widget for the coordinates layout
        coords_container = QWidget()
        coords_container.setLayout(coords_layout)
        
        area_layout.addRow("Coordinates:", coords_container)
        
        area_group.setLayout(area_layout)
        
        map_group.setLayout(map_layout)
        
        # Aggiungi gruppi al layout
        layout.addWidget(map_group)
        layout.addWidget(area_group)
        
        # Pulsanti
        buttons_layout = QHBoxLayout()
        
        self.unlock_button = QPushButton("Unlock Area")
        self.unlock_button.clicked.connect(self.unlock_area)
        buttons_layout.addWidget(self.unlock_button)
        
        self.reset_button = QPushButton("Reset Map")
        self.reset_button.clicked.connect(self.reset_map)
        buttons_layout.addWidget(self.reset_button)
        
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connetti segnali
        self.areas_table.itemSelectionChanged.connect(self.on_area_selected)
        
    def on_area_selected(self):
        """Gestisce la selezione di un'area della mappa"""
        selected_rows = self.areas_table.selectedItems()
        if not selected_rows:
            return
            
        # Ottieni la riga selezionata
        row = selected_rows[0].row()
        
        # Recupera i dati dell'area dalla tabella
        area_id = self.areas_table.item(row, 0).text()
        
        if area_id in self.map_areas:
            area_data = self.map_areas[area_id]
            
            # Aggiorna i campi di modifica
            self.area_id_edit.setText(area_id)
            self.area_name_edit.setText(area_data.get("name", f"Area {area_id}"))
            
            # Imposta lo stato
            status_text = "Locked"
            if area_data.get("status") == 1:
                status_text = "Unlocked"
            elif area_data.get("status") == 2:
                status_text = "Completed"
            self.area_status_combo.setCurrentText(status_text)
            
            # Imposta le coordinate
            coords = area_data.get("coordinates", (0, 0))
            self.area_x_spin.setValue(coords[0])
            self.area_y_spin.setValue(coords[1])
            
            # Evidenzia l'area sulla mappa
            self.highlight_area(area_id)
        
    def highlight_area(self, area_id):
        """Evidenzia un'area sulla mappa"""
        if not hasattr(self, 'map_pixmap') or not self.map_pixmap:
            return
            
        # Crea una copia modificabile della mappa
        highlighted = QPixmap(self.map_pixmap)
        painter = QPainter(highlighted)
        
        # Imposta parametri disegno
        pen = QPen(QColor(255, 165, 0))  # Arancione
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Disegna un cerchio attorno all'area selezionata
        if area_id in self.map_areas:
            coords = self.map_areas[area_id].get("coordinates", (0, 0))
            
            # Calcola la posizione relativa sulla mappa
            map_width = self.map_pixmap.width()
            map_height = self.map_pixmap.height()
            
            # Converti le coordinate del gioco in coordinate della mappa
            x = int((coords[0] + 1000) * map_width / 2000)
            y = int((coords[1] + 1000) * map_height / 2000)
            
            # Disegna un cerchio
            painter.drawEllipse(x - 15, y - 15, 30, 30)
        
        painter.end()
        
        # Aggiorna la visualizzazione
        self.map_view.setPixmap(highlighted.scaled(
            self.map_view.width(), 
            self.map_view.height(), 
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        
    def unlock_area(self):
        """Unlock a map area"""
        # Check if we have a valid ID
        area_id = self.area_id_edit.text()
        if not area_id or area_id not in self.map_areas:
            self.status_bar.showMessage("Error: Select a valid area from the table first")
            return
            
        # Set status to "Unlocked"
        self.area_status_combo.setCurrentText("Unlocked")
        
        # Update table
        for row in range(self.areas_table.rowCount()):
            if self.areas_table.item(row, 0).text() == area_id:
                self.areas_table.setItem(row, 2, QTableWidgetItem("Unlocked"))
                break
                
        # Update areas dictionary
        self.map_areas[area_id]["status"] = 1
        
        self.status_bar.showMessage(f"Area {area_id} unlocked successfully")
        
    def reset_map(self):
        """Reset all areas on the map"""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all map areas? This will set all areas as locked.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset all areas
            for area_id in self.map_areas:
                self.map_areas[area_id]["status"] = 0
                
            # Update table
            for row in range(self.areas_table.rowCount()):
                area_id = self.areas_table.item(row, 0).text()
                self.areas_table.setItem(row, 2, QTableWidgetItem("Locked"))
                
            # Update current selection
            if self.area_id_edit.text():
                self.area_status_combo.setCurrentText("Locked")
                
            self.status_bar.showMessage("All map areas have been reset")
        
    def save_changes(self):
        """Save map changes"""
        if not self.save_data:
            self.status_bar.showMessage("Error: No data loaded. Load a save file first")
            return
            
        # Check if we have a valid ID
        area_id = self.area_id_edit.text()
        if not area_id or area_id not in self.map_areas:
            self.status_bar.showMessage("Error: Select a valid area from the table first")
            return
            
        try:
            # Update area data
            self.map_areas[area_id]["name"] = self.area_name_edit.text()
            
            # Determine numeric status based on text
            status_text = self.area_status_combo.currentText()
            status_value = 0  # Locked by default
            if status_text == "Unlocked":
                status_value = 1
            elif status_text == "Completed":
                status_value = 2
            
            self.map_areas[area_id]["status"] = status_value
            
            # Update coordinates
            self.map_areas[area_id]["coordinates"] = (
                self.area_x_spin.value(),
                self.area_y_spin.value()
            )
            
            # Update table
            for row in range(self.areas_table.rowCount()):
                if self.areas_table.item(row, 0).text() == area_id:
                    self.areas_table.setItem(row, 1, QTableWidgetItem(self.area_name_edit.text()))
                    self.areas_table.setItem(row, 2, QTableWidgetItem(status_text))
                    break
            
            # Update save data
            if "dictionaryOfDictionaries" in self.save_data and "value" in self.save_data["dictionaryOfDictionaries"]:
                dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
                
                # Update area status and names
                if "mapAreas" in dict_of_dicts:
                    dict_of_dicts["mapAreas"][area_id] = status_value
                    
                if "mapAreaNames" in dict_of_dicts:
                    dict_of_dicts["mapAreaNames"][area_id] = self.area_name_edit.text()
                    
                if "mapAreaCoordinates" in dict_of_dicts:
                    coords = self.map_areas[area_id]["coordinates"]
                    dict_of_dicts["mapAreaCoordinates"][area_id] = {
                        "x": coords[0],
                        "y": coords[1]
                    }
            
            # Update map view
            self.highlight_area(area_id)
            
            self.status_bar.showMessage(f"Changes to area {area_id} saved successfully")
            
        except Exception as e:
            self.status_bar.showMessage(f"Error saving changes: {str(e)}")
    
    def update_data(self, data: Dict[str, Any]):
        """
        Update map data
        
        Args:
            data: Save data
        """
        try:
            self.save_data = data
            self.map_areas = {}
            
            # Clear table
            self.areas_table.setRowCount(0)
            
            # Check if there's map data
            if "dictionaryOfDictionaries" in data and "value" in data["dictionaryOfDictionaries"]:
                dict_of_dicts = data["dictionaryOfDictionaries"]["value"]
                
                # Look for map-related keys
                map_keys = ["mapAreas", "areas", "worldMap", "locations", "zones"]
                map_key = next((key for key in map_keys if key in dict_of_dicts), None)
                
                if map_key:
                    areas = dict_of_dicts[map_key]
                    
                    # Dictionaries for area names and coordinates
                    area_names = {}
                    area_coords = {}
                    
                    # Look for area names
                    if "mapAreaNames" in dict_of_dicts:
                        area_names = dict_of_dicts["mapAreaNames"]
                    elif "areaNames" in dict_of_dicts:
                        area_names = dict_of_dicts["areaNames"]
                        
                    # Look for area coordinates
                    if "mapAreaCoordinates" in dict_of_dicts:
                        area_coords = dict_of_dicts["mapAreaCoordinates"]
                    elif "areaCoordinates" in dict_of_dicts:
                        area_coords = dict_of_dicts["areaCoordinates"]
                        
                    # Process each area
                    for area_id, area_status in areas.items():
                        area_name = area_names.get(area_id, f"Area {area_id}")
                        
                        # Extract coordinates
                        coords = (0, 0)
                        if area_id in area_coords:
                            coords_data = area_coords[area_id]
                            if isinstance(coords_data, dict):
                                coords = (
                                    coords_data.get("x", 0),
                                    coords_data.get("y", 0)
                                )
                                
                        # Determine area status
                        status_value = 0
                        if isinstance(area_status, bool):
                            status_value = 1 if area_status else 0
                        elif isinstance(area_status, (int, float)):
                            status_value = int(area_status)
                            
                        # Save area data
                        self.map_areas[area_id] = {
                            "name": area_name,
                            "status": status_value,
                            "coordinates": coords
                        }
                        
                        # Determine status text
                        status_text = "Locked"
                        if status_value == 1:
                            status_text = "Unlocked"
                        elif status_value == 2:
                            status_text = "Completed"
                            
                        # Add to table
                        self.add_area_to_table(area_id, area_name, status_text)
                        
                # Load base map
                self.load_base_map()
                
                if self.map_areas:
                    self.status_bar.showMessage(f"Loaded {len(self.map_areas)} map areas")
                else:
                    self.status_bar.showMessage("No map areas found in save data")
                
        except Exception as e:
            self.status_bar.showMessage(f"Error updating map data: {str(e)}")
    
    def load_base_map(self):
        """Carica la mappa di base dal gioco o una immagine generica"""
        try:
            # Prova a caricare la mappa dal gioco
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            map_path = os.path.join(root_dir, "assets", "images", "world_map.png")
            
            if os.path.exists(map_path):
                self.map_pixmap = QPixmap(map_path)
            else:
                # Genera una mappa generica
                width = 500
                height = 400
                self.map_pixmap = QPixmap(width, height)
                self.map_pixmap.fill(QColor(30, 30, 40))
                
                # Disegna una griglia
                painter = QPainter(self.map_pixmap)
                painter.setPen(QPen(QColor(50, 50, 60)))
                
                # Disegna linee orizzontali
                for y in range(0, height, 50):
                    painter.drawLine(0, y, width, y)
                    
                # Disegna linee verticali
                for x in range(0, width, 50):
                    painter.drawLine(x, 0, x, height)
                    
                painter.end()
            
            # Disegna punti per ogni area
            painter = QPainter(self.map_pixmap)
            
            for area_id, area_data in self.map_areas.items():
                coords = area_data.get("coordinates", (0, 0))
                status = area_data.get("status", 0)
                
                # Calcola la posizione relativa sulla mappa
                map_width = self.map_pixmap.width()
                map_height = self.map_pixmap.height()
                
                # Converti le coordinate del gioco in coordinate della mappa
                x = int((coords[0] + 1000) * map_width / 2000)
                y = int((coords[1] + 1000) * map_height / 2000)
                
                # Scegli colore in base allo stato
                if status == 0:  # Bloccata
                    painter.setPen(QPen(QColor(255, 0, 0)))  # Rosso
                    painter.setBrush(QColor(255, 0, 0))
                elif status == 1:  # Sbloccata
                    painter.setPen(QPen(QColor(0, 255, 0)))  # Verde
                    painter.setBrush(QColor(0, 255, 0))
                else:  # Completata
                    painter.setPen(QPen(QColor(0, 0, 255)))  # Blu
                    painter.setBrush(QColor(0, 0, 255))
                    
                # Disegna un punto
                painter.drawEllipse(x - 5, y - 5, 10, 10)
                
            painter.end()
            
            # Mostra la mappa
            self.map_view.setPixmap(self.map_pixmap.scaled(
                self.map_view.width(), 
                self.map_view.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            
        except Exception as e:
            print(f"Errore durante il caricamento della mappa: {e}")
            self.map_view.setText("Errore caricamento mappa")
    
    def add_area_to_table(self, area_id, name, status):
        """
        Aggiunge un'area alla tabella
        
        Args:
            area_id: ID dell'area
            name: Nome dell'area
            status: Stato dell'area
        """
        row = self.areas_table.rowCount()
        self.areas_table.insertRow(row)
        
        # Imposta i dati nelle celle
        self.areas_table.setItem(row, 0, QTableWidgetItem(str(area_id)))
        self.areas_table.setItem(row, 1, QTableWidgetItem(str(name)))
        self.areas_table.setItem(row, 2, QTableWidgetItem(str(status)))
        
        # Pulsante azioni
        action_cell = QTableWidgetItem("Modifica")
        self.areas_table.setItem(row, 3, action_cell)

class SettingsTab(QWidget):
    """Tab per le impostazioni dell'editor"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_file = os.path.join(
            os.environ.get("REPO_SAVE_EDITOR_ROOT", 
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))),
            "settings.json"
        )
        self.settings = self.load_settings()
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # General settings
        general_group = QGroupBox("General Settings")
        general_layout = QFormLayout()
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        if "theme" in self.settings:
            self.theme_combo.setCurrentText(self.settings["theme"])
        general_layout.addRow("Theme:", self.theme_combo)
        
        # Language
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Italian"])
        if "language" in self.settings:
            self.language_combo.setCurrentText(self.settings["language"])
        general_layout.addRow("Language:", self.language_combo)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Backup settings
        backup_group = QGroupBox("Backup Settings")
        backup_layout = QFormLayout()
        
        # Backup folder
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setText(self.settings.get("backup_path", ""))
        
        backup_path_layout = QHBoxLayout()
        backup_path_layout.addWidget(self.backup_path_edit)
        
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_backup_folder)
        backup_path_layout.addWidget(browse_button)
        
        backup_layout.addRow("Backup Folder:", backup_path_layout)
        
        # Backup frequency
        self.backup_freq_combo = QComboBox()
        self.backup_freq_combo.addItems(["Never", "Hourly", "Daily", "Weekly"])
        if "backup_frequency" in self.settings:
            self.backup_freq_combo.setCurrentText(self.settings["backup_frequency"])
        backup_layout.addRow("Backup Frequency:", self.backup_freq_combo)
        
        # Maximum backups
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        self.max_backups_spin.setValue(self.settings.get("max_backups", 5))
        backup_layout.addRow("Max Backups:", self.max_backups_spin)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()
        
        # Developer mode
        self.dev_mode_check = QCheckBox()
        self.dev_mode_check.setChecked(self.settings.get("dev_mode", False))
        advanced_layout.addRow("Developer Mode:", self.dev_mode_check)
        
        # Cache size
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(10, 1000)
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.setValue(self.settings.get("cache_size", 100))
        advanced_layout.addRow("Cache Size:", self.cache_size_spin)
        
        # Network timeout
        self.network_timeout_spin = QSpinBox()
        self.network_timeout_spin.setRange(1, 60)
        self.network_timeout_spin.setSuffix(" sec")
        self.network_timeout_spin.setValue(self.settings.get("network_timeout", 10))
        advanced_layout.addRow("Network Timeout:", self.network_timeout_spin)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton("Reset Settings")
        self.reset_button.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def browse_backup_folder(self):
        """Open dialog to select the backup folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Backup Folder",
            self.backup_path_edit.text() or os.path.expanduser("~")
        )
        
        if folder:
            self.backup_path_edit.setText(folder)
    
    def load_settings(self):
        """Carica le impostazioni da file"""
        default_settings = {
            "theme": "Dark",
            "language": "English",
            "backup_path": "",
            "backup_frequency": "Never",
            "max_backups": 5,
            "dev_mode": False,
            "cache_size": 100,
            "network_timeout": 10
        }
        
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                return {**default_settings, **settings}
            else:
                return default_settings
        except Exception as e:
            print(f"Errore durante il caricamento delle impostazioni: {e}")
            return default_settings
        
    def save_settings(self):
        """Save current settings"""
        settings = {
            "theme": self.theme_combo.currentText(),
            "language": self.language_combo.currentText(),
            "backup_path": self.backup_path_edit.text(),
            "backup_frequency": self.backup_freq_combo.currentText(),
            "max_backups": self.max_backups_spin.value(),
            "dev_mode": self.dev_mode_check.isChecked(),
            "cache_size": self.cache_size_spin.value(),
            "network_timeout": self.network_timeout_spin.value()
        }
        
        try:
            # Make sure settings directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Save settings
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
                
            self.settings = settings
            
            self.status_bar.showMessage("Settings saved successfully")
            
            # Ask user if they want to restart the application
            if self.settings.get("theme") != settings["theme"] or self.settings.get("language") != settings["language"]:
                reply = QMessageBox.question(
                    self,
                    "Restart Required",
                    "Some changes require restarting the application to take effect. Do you want to restart now?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    # Restart the application
                    import sys
                    import subprocess
                    
                    # Restart process with the same arguments
                    python = sys.executable
                    os.execl(python, python, *sys.argv)
            
        except Exception as e:
            self.status_bar.showMessage(f"Error saving settings: {str(e)}")
        
    def reset_settings(self):
        """Reset settings to default values"""
        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset all settings to default values?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Default values
            default_settings = {
                "theme": "Dark",
                "language": "English",
                "backup_path": "",
                "backup_frequency": "Never",
                "max_backups": 5,
                "dev_mode": False,
                "cache_size": 100,
                "network_timeout": 10
            }
            
            # Aggiorna i controlli UI
            self.theme_combo.setCurrentText(default_settings["theme"])
            self.language_combo.setCurrentText(default_settings["language"])
            self.backup_path_edit.setText(default_settings["backup_path"])
            self.backup_freq_combo.setCurrentText(default_settings["backup_frequency"])
            self.max_backups_spin.setValue(default_settings["max_backups"])
            self.dev_mode_check.setChecked(default_settings["dev_mode"])
            self.cache_size_spin.setValue(default_settings["cache_size"])
            self.network_timeout_spin.setValue(default_settings["network_timeout"])
            
            # Save default settings
            self.settings = default_settings
            
            try:
                # Save to file
                with open(self.settings_file, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=4, ensure_ascii=False)
                
                self.status_bar.showMessage("Settings reset to default values")
                
            except Exception as e:
                self.status_bar.showMessage(f"Error resetting settings: {str(e)}")
    
    def apply_theme(self, theme):
        """Applica il tema selezionato all'applicazione"""
        if theme == "Dark":
            # Applica il tema scuro
            self.setStyleSheet("""
                QWidget { background-color: #2D2D30; color: #FFFFFF; }
                QGroupBox { border: 1px solid #3F3F46; border-radius: 4px; margin-top: 0.5em; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
                QPushButton { background-color: #0078D7; color: white; border-radius: 4px; padding: 5px; }
                QPushButton:hover { background-color: #1C97EA; }
                QLineEdit, QSpinBox, QComboBox { background-color: #333337; border: 1px solid #3F3F46; border-radius: 2px; padding: 3px; color: white; }
                QTabWidget::pane { border: 1px solid #3F3F46; }
                QTabBar::tab { background-color: #252526; color: #FFFFFF; padding: 8px 12px; }
                QTabBar::tab:selected { background-color: #007ACC; }
                QTabBar::tab:hover:!selected { background-color: #3E3E40; }
            """)
        elif theme == "Light":
            # Applica il tema chiaro
            self.setStyleSheet("""
                QWidget { background-color: #F0F0F0; color: #000000; }
                QGroupBox { border: 1px solid #CCCCCC; border-radius: 4px; margin-top: 0.5em; }
                QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px; }
                QPushButton { background-color: #0078D7; color: white; border-radius: 4px; padding: 5px; }
                QPushButton:hover { background-color: #1C97EA; }
                QLineEdit, QSpinBox, QComboBox { background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 2px; padding: 3px; color: black; }
                QTabWidget::pane { border: 1px solid #CCCCCC; }
                QTabBar::tab { background-color: #E1E1E1; color: #000000; padding: 8px 12px; }
                QTabBar::tab:selected { background-color: #007ACC; color: white; }
                QTabBar::tab:hover:!selected { background-color: #D1D1D1; }
            """)
        elif theme == "System":
            # Usa il tema di sistema (rimuove lo stylesheet personalizzato)
            self.setStyleSheet("")
        
        # Emetti un segnale per informare altre parti dell'applicazione del cambio di tema
        if hasattr(self, 'theme_changed') and callable(getattr(self, 'theme_changed', None)):
            self.theme_changed.emit(theme)