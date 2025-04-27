"""Tab dell'interfaccia principale"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QSpinBox, QDoubleSpinBox,
    QProgressBar, QScrollArea, QGroupBox, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
    QGridLayout, QCheckBox, QFileDialog, QTextEdit, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from typing import Dict, Any
import os
import json
import requests
from io import BytesIO
import re
import xml.etree.ElementTree as ElementTree
from pathlib import Path
import logging

from core.language_manager import tr, language_manager

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
        QMessageBox.critical(self, tr("general.error", "Errore"), message)
        
    def show_info(self, message):
        """Mostra un messaggio informativo"""
        QMessageBox.information(self, tr("general.info", "Informazione"), message)

class PlayerTab(QWidget):
    """Tab for player data management"""
    
    def __init__(self, save_data, parent=None):
        super().__init__(parent)
        self.save_data = save_data
        self.player_data = {}
        self.players = {}
        self.current_player_id = None
        self.status_bar = None
        self.init_ui()
        
        # Registra per gli aggiornamenti della lingua
        language_manager.add_observer(self.update_translations)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Selettore giocatore (partecipante)
        player_select_layout = QHBoxLayout()
        self.select_player_label = QLabel(tr("player_tab.select_player", "Seleziona Giocatore:"))
        player_select_layout.addWidget(self.select_player_label)
        
        self.player_selector = QComboBox()
        self.player_selector.currentIndexChanged.connect(self.on_player_changed)
        player_select_layout.addWidget(self.player_selector)
        
        # Aggiungi pulsante per nuovo giocatore
        self.add_player_button = QPushButton("+")
        self.add_player_button.setToolTip(tr("player_tab.add_player", "Aggiungi Nuovo Giocatore"))
        self.add_player_button.setFixedWidth(30)
        self.add_player_button.clicked.connect(self.add_new_player)
        player_select_layout.addWidget(self.add_player_button)
        
        layout.addLayout(player_select_layout)
        
        # Top section with player info and avatar
        top_layout = QHBoxLayout()
        
        # Player info form
        info_form = QFormLayout()
        
        self.player_name = QLineEdit()
        self.name_label = QLabel(tr("player_tab.player_name", "Nome:"))
        info_form.addRow(self.name_label, self.player_name)
        
        self.player_level = QSpinBox()
        self.player_level.setRange(1, 100)
        self.level_label = QLabel(tr("player_tab.level", "Level:"))
        info_form.addRow(self.level_label, self.player_level)
        
        self.player_health = QSpinBox()
        self.player_health.setRange(1, 10000)
        self.health_label = QLabel(tr("player_tab.health", "Health:"))
        info_form.addRow(self.health_label, self.player_health)
        
        self.player_money = QDoubleSpinBox()
        self.player_money.setRange(0, 1000000)
        self.player_money.setSingleStep(100)
        self.money_label = QLabel(tr("player_tab.money", "Money:"))
        info_form.addRow(self.money_label, self.player_money)
        
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
        self.steam_id_edit.setPlaceholderText(tr("player_tab.steam_id", "Steam ID (autodetection)"))
        self.steam_id_edit.setReadOnly(True)  # Steam ID non modificabile
        self.steam_id_edit.setStyleSheet("background-color: #2a2a2a;")
        steam_id_layout.addWidget(self.steam_id_edit)
        
        self.load_avatar_button = QPushButton(tr("player_tab.reload_avatar", "Reload Avatar"))
        self.load_avatar_button.clicked.connect(self.load_steam_avatar)
        steam_id_layout.addWidget(self.load_avatar_button)
        
        avatar_layout.addLayout(steam_id_layout)
        
        # Add info and avatar to top layout
        top_layout.addLayout(avatar_layout)
        top_layout.addWidget(info_widget, 1)  # 1 is the stretch factor
        
        layout.addLayout(top_layout)
        
        # Stats group
        self.stats_group = QGroupBox(tr("player_tab.player_stats", "Player Stats"))
        stats_layout = QFormLayout()
        
        self.player_strength = QSpinBox()
        self.player_strength.setRange(1, 100)
        self.strength_label = QLabel(tr("player_tab.strength", "Strength:"))
        stats_layout.addRow(self.strength_label, self.player_strength)
        
        self.player_agility = QSpinBox()
        self.player_agility.setRange(1, 100)
        self.agility_label = QLabel(tr("player_tab.agility", "Agility:"))
        stats_layout.addRow(self.agility_label, self.player_agility)
        

        self.player_endurance = QSpinBox()
        self.player_endurance.setRange(1, 100)
        self.endurance_label = QLabel(tr("player_tab.endurance", "Endurance:"))
        stats_layout.addRow(self.endurance_label, self.player_endurance)
        
        # Aggiungi nuovi campi per le statistiche aggiuntive
        self.player_extra_jump = QSpinBox()
        self.player_extra_jump.setRange(0, 10)
        self.extra_jump_label = QLabel(tr("player_tab.extra_jump", "Extra Jump:"))
        stats_layout.addRow(self.extra_jump_label, self.player_extra_jump)
        
        self.player_launch = QSpinBox()
        self.player_launch.setRange(0, 10)
        self.launch_label = QLabel(tr("player_tab.launch", "Launch:"))
        stats_layout.addRow(self.launch_label, self.player_launch)
        
        self.player_map_count = QSpinBox()
        self.player_map_count.setRange(0, 10)
        self.map_count_label = QLabel(tr("player_tab.map_count", "Map Count:"))
        stats_layout.addRow(self.map_count_label, self.player_map_count)
        
        self.player_speed = QSpinBox()
        self.player_speed.setRange(1, 100)
        self.speed_label = QLabel(tr("player_tab.speed", "Speed:"))
        stats_layout.addRow(self.speed_label, self.player_speed)
        
        self.player_range = QSpinBox()
        self.player_range.setRange(1, 100)
        self.range_label = QLabel(tr("player_tab.range", "Range:"))
        stats_layout.addRow(self.range_label, self.player_range)
        
        self.player_throw = QSpinBox()
        self.player_throw.setRange(1, 100)
        self.throw_label = QLabel(tr("player_tab.throw", "Throw:"))
        stats_layout.addRow(self.throw_label, self.player_throw)
        
        self.stats_group.setLayout(stats_layout)
        layout.addWidget(self.stats_group)
        
        self.setLayout(layout)
        
        # Carica l'avatar default quando il widget è mostrato
        self.show_default_avatar()
        
        # Connect signals
        self.player_name.textChanged.connect(self.on_player_name_changed)
        self.player_level.valueChanged.connect(self.on_player_level_changed)
        self.player_health.valueChanged.connect(self.on_player_health_changed)
        self.player_money.valueChanged.connect(self.on_player_money_changed)
        self.player_strength.valueChanged.connect(self.on_player_strength_changed)
        self.player_agility.valueChanged.connect(self.on_player_agility_changed)
        self.player_endurance.valueChanged.connect(self.on_player_endurance_changed)
        self.player_extra_jump.valueChanged.connect(self.on_player_extra_jump_changed)
        self.player_launch.valueChanged.connect(self.on_player_launch_changed)
        self.player_map_count.valueChanged.connect(self.on_player_map_count_changed)
        self.player_speed.valueChanged.connect(self.on_player_speed_changed)
        self.player_range.valueChanged.connect(self.on_player_range_changed)
        self.player_throw.valueChanged.connect(self.on_player_throw_changed)
        
    def update_translations(self):
        """Aggiorna le traduzioni dell'interfaccia quando cambia la lingua"""
        self.select_player_label.setText(tr("player_tab.select_player", "Seleziona Giocatore:"))
        self.add_player_button.setToolTip(tr("player_tab.add_player", "Aggiungi Nuovo Giocatore"))
        self.name_label.setText(tr("player_tab.player_name", "Nome:"))
        self.level_label.setText(tr("player_tab.level", "Level:"))
        self.health_label.setText(tr("player_tab.health", "Health:"))
        self.money_label.setText(tr("player_tab.money", "Money:"))
        self.steam_id_edit.setPlaceholderText(tr("player_tab.steam_id", "Steam ID (autodetection)"))
        self.load_avatar_button.setText(tr("player_tab.reload_avatar", "Reload Avatar"))
        self.stats_group.setTitle(tr("player_tab.player_stats", "Player Stats"))
        self.strength_label.setText(tr("player_tab.strength", "Strength:"))
        self.agility_label.setText(tr("player_tab.agility", "Agility:"))
        self.endurance_label.setText(tr("player_tab.endurance", "Endurance:"))
        self.extra_jump_label.setText(tr("player_tab.extra_jump", "Extra Jump:"))
        self.launch_label.setText(tr("player_tab.launch", "Launch:"))
        self.map_count_label.setText(tr("player_tab.map_count", "Map Count:"))
        self.speed_label.setText(tr("player_tab.speed", "Speed:"))
        self.range_label.setText(tr("player_tab.range", "Range:"))
        self.throw_label.setText(tr("player_tab.throw", "Throw:"))
        
    def add_new_player(self):
        """Aggiunge un nuovo giocatore al salvataggio"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                tr("player_tab.no_save_loaded", "Nessun salvataggio caricato"),
                tr("player_tab.load_save_first", "Carica prima un salvataggio per aggiungere un nuovo giocatore.")
            )
            return
            
        # Genera un nuovo ID univoco per il giocatore
        import uuid
        new_player_id = str(uuid.uuid4())
        
        # Chiedi il nome del nuovo giocatore
        player_name, ok = QInputDialog.getText(
            self,
            tr("player_tab.add_player_title", "Nuovo Giocatore"),
            tr("player_tab.add_player_prompt", "Inserisci il nome del nuovo giocatore:")
        )
        
        if ok and player_name:
            # Aggiungi il giocatore al salvataggio
            if "playerNames" not in self.save_data:
                self.save_data["playerNames"] = {}
                
            self.save_data["playerNames"][new_player_id] = player_name
            
            # Aggiungi il giocatore al selettore
            self.player_selector.addItem(player_name, new_player_id)
            
            # Seleziona il nuovo giocatore
            self.player_selector.setCurrentIndex(self.player_selector.count() - 1)
            
            # Aggiorna l'interfaccia
            self.update_player_data(new_player_id)
            
            # Mostra un messaggio di conferma
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("player_tab.player_added", "Giocatore aggiunto con successo!")
            )
        
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
                print(f"Statistics found for player {player_id}: {list(player_stats.keys())}")
                
                # Aggiorna i controlli UI con le statistiche del giocatore
                if "playerHealth" in player_stats:
                    health_value = self.extract_value(player_stats["playerHealth"], 100)
                    self.player_health.setValue(health_value)
                    
                # Correggo le assegnazioni per mappare correttamente i dati del server ai controlli UI
                if "playerUpgradeStamina" in player_stats:
                    # Stamina -> Agilità
                    self.player_agility.setValue(self.extract_value(player_stats.get("playerUpgradeStamina"), 10))
                
                if "playerUpgradeStrength" in player_stats:
                    # Forza -> Forza
                    self.player_strength.setValue(self.extract_value(player_stats.get("playerUpgradeStrength"), 10))
                
                if "playerUpgradeSpeed" in player_stats:
                    # Velocità -> Resistenza
                    self.player_endurance.setValue(self.extract_value(player_stats.get("playerUpgradeSpeed"), 10))
                
                # Aggiorna le statistiche aggiuntive
                if "playerUpgradeExtraJump" in player_stats:
                    self.player_extra_jump.setValue(self.extract_value(player_stats.get("playerUpgradeExtraJump"), 0))
                
                if "playerUpgradeLaunch" in player_stats:
                    self.player_launch.setValue(self.extract_value(player_stats.get("playerUpgradeLaunch"), 0))
                
                if "playerUpgradeMapPlayerCount" in player_stats:
                    self.player_map_count.setValue(self.extract_value(player_stats.get("playerUpgradeMapPlayerCount"), 0))
                
                if "playerUpgradeSpeed" in player_stats:
                    # Questo è duplicato, imposta il valore di Speed
                    self.player_speed.setValue(self.extract_value(player_stats.get("playerUpgradeSpeed"), 10))
                
                if "playerUpgradeRange" in player_stats:
                    self.player_range.setValue(self.extract_value(player_stats.get("playerUpgradeRange"), 10))
                
                if "playerUpgradeThrow" in player_stats:
                    self.player_throw.setValue(self.extract_value(player_stats.get("playerUpgradeThrow"), 10))
                
                # Aggiorna il livello da runStats
                if "runStats" in dict_data and "level" in dict_data["runStats"]:
                    self.player_level.setValue(self.extract_value(dict_data["runStats"]["level"], 1))
                    print(f"Player level set to: {self.player_level.value()}")
                
                if "runStats" in dict_data and "currency" in dict_data["runStats"]:
                    self.player_money.setValue(self.extract_value(dict_data["runStats"]["currency"], 0))
                    print(f"Money player set to: {self.player_money.value()}")
                
                # Memorizza i dati del giocatore per uso futuro
                self.player_data = player_stats
            
            # Cerca lo Steam ID e carica l'avatar
            self.find_and_set_steam_id(player_id)
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Error updating player data: {str(e)}\n{traceback_str}")
            QMessageBox.warning(
                self,
                tr("general.error", "Error"),
                tr("player_tab.update_error", f"Unable to update player data: {str(e)}")
            )
    
    def find_and_set_steam_id(self, player_id):
        """Cerca e imposta lo Steam ID per il giocatore specificato"""
        steam_id = None
        
        try:
            # Controlla se l'ID del giocatore è già un ID Steam (inizia con 7656119)
            if player_id and str(player_id).startswith("7656119") and len(str(player_id)) >= 17:
                print(f"Player ID {player_id} is already a Steam ID")
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
                if not pixmap.isNull():
                    # Scale to fit the label
                    pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    self.avatar_label.setPixmap(pixmap)
                    return
            
            # If file not found, use a placeholder
            self.avatar_label.setText("No Image")
            
        except Exception as e:
            print(f"Error loading default avatar: {str(e)}")
            self.avatar_label.setText("No Image")
            
    def load_steam_avatar(self):
        try:
            steam_id = self.current_player_id
            if not steam_id:
                self.avatar_label.setText("No Image")
                return
            url = f"https://steamcommunity.com/profiles/{steam_id}/?xml=1"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                import xml.etree.ElementTree as ET
                root = ET.fromstring(response.content)
                avatar_url = root.findtext("avatarFull")
                if avatar_url:
                    img_data = requests.get(avatar_url, timeout=5).content
                    pixmap = QPixmap()
                    if pixmap.loadFromData(img_data):
                        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.avatar_label.setPixmap(pixmap)
                        self.avatar_label.setText("")
                        return
            # Se qualcosa va storto, mostra placeholder
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText("No Image")
        except Exception as e:
            print(f"Errore caricamento avatar Steam: {e}")
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText("No Image")
        
    def _update_json_editor(self):
        mw = self.parent()
        if mw and hasattr(mw, 'advanced_tab'):
            mw.advanced_tab.update_json_from_ui()

    # --- Metodi di aggiornamento dati in tempo reale ---
    def on_player_name_changed(self, value):
        if self.save_data and self.current_player_id:
            self.save_data["playerNames"][self.current_player_id] = value
            from core.logger import logger
            logger.info(f"Nome giocatore aggiornato: {self.current_player_id} -> {value}")
            self._update_json_editor()

    def on_player_level_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "runStats" in d:
                d["runStats"]["level"] = value
                from core.logger import logger
                logger.info(f"Livello aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_health_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerHealth" in d:
                d["playerHealth"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Salute aggiornata: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_money_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "runStats" in d:
                d["runStats"]["currency"] = value
                from core.logger import logger
                logger.info(f"Soldi aggiornati: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_strength_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeStrength" in d:
                d["playerUpgradeStrength"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Forza aggiornata: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_agility_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeStamina" in d:
                d["playerUpgradeStamina"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Agilità aggiornata: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_endurance_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeSpeed" in d:
                d["playerUpgradeSpeed"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Resistenza aggiornata: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_extra_jump_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeExtraJump" in d:
                d["playerUpgradeExtraJump"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Extra Jump aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_launch_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeLaunch" in d:
                d["playerUpgradeLaunch"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Launch aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_map_count_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeMapPlayerCount" in d:
                d["playerUpgradeMapPlayerCount"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Map Count aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_speed_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeSpeed" in d:
                d["playerUpgradeSpeed"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Speed aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_range_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeRange" in d:
                d["playerUpgradeRange"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Range aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def on_player_throw_changed(self, value):
        if self.save_data and self.current_player_id:
            d = self.save_data.get("dictionaryOfDictionaries", {}).get("value", {})
            if "playerUpgradeThrow" in d:
                d["playerUpgradeThrow"][self.current_player_id] = value
                from core.logger import logger
                logger.info(f"Throw aggiornato: {self.current_player_id} -> {value}")
                self._update_json_editor()

    def refresh_ui_from_data(self):
        """Aggiorna l'interfaccia utente con i dati del salvataggio"""
        logger = logging.getLogger(__name__)
        logger.info("PlayerTab.refresh_ui_from_data - Aggiornamento UI dai dati salvati")
        
        if not self.save_data:
            logger.warning("PlayerTab.refresh_ui_from_data - Nessun dato disponibile")
            return
            
        try:
            # Pulisci il selector e i dati dei giocatori
            self.player_selector.clear()
            self.players = {}
            
            # Verifica la struttura dei dati
            if "playerNames" not in self.save_data:
                logger.warning("PlayerTab.refresh_ui_from_data - Structure data not valid: playerNames not found")
                return
                
            player_names_data = self.save_data.get("playerNames", {})
            if isinstance(player_names_data, dict) and "value" in player_names_data:
                player_names_data = player_names_data["value"]
                
            # Aggiungi i giocatori al selettore
            for player_id, player_name in player_names_data.items():
                try:
                    display_name = player_name
                    if not display_name:
                        display_name = f"Player {player_id}"
                    
                    self.players[player_id] = display_name
                    self.player_selector.addItem(display_name, player_id)
                    logger.info(f"PlayerTab.refresh_ui_from_data - Added player: {player_id} -> {display_name}")
                except Exception as e:
                    logger.error(f"PlayerTab.refresh_ui_from_data - Error adding player {player_id}: {str(e)}")
            
            # Seleziona il primo giocatore se disponibile
            if self.player_selector.count() > 0:
                logger.info("PlayerTab.refresh_ui_from_data - Selected first player")
                self.player_selector.setCurrentIndex(0)
                # L'aggiornamento avverrà tramite il signal del selettore
            else:
                logger.warning("PlayerTab.refresh_ui_from_data - No players found")
        except Exception as e:
            import traceback
            logger.error(f"PlayerTab.refresh_ui_from_data - Error: {str(e)}\n{traceback.format_exc()}")

    def extract_value(self, data_dict, default_value=0):
        """Estrae un valore da un dizionario, gestendo i casi in cui la chiave potrebbe non esistere
        
        Args:
            data_dict: Dizionario da cui estrarre il valore o valore diretto
            default_value: Valore predefinito da restituire se la chiave non esiste
            
        Returns:
            Valore estratto o default_value se la chiave non esiste
        """
        try:
            if isinstance(data_dict, dict) and self.current_player_id in data_dict:
                return data_dict[self.current_player_id]
            elif not isinstance(data_dict, dict):
                # Se non è un dizionario, restituisci il valore direttamente
                return data_dict
            return default_value
        except Exception as e:
            logging.getLogger(__name__).error(f"Error in extract_value: {e}")
            return default_value
            
    def extract_player_name(self, player_data, player_id):
        """Estrae il nome del giocatore dai dati forniti
        
        Args:
            player_data: Dati del giocatore, può essere un dizionario o un valore diretto
            player_id: ID del giocatore, usato come fallback se non è possibile estrarre un nome
            
        Returns:
            Nome del giocatore o player_id come fallback
        """
        try:
            logger = logging.getLogger(__name__)
            
            # Se player_data è una stringa, usala direttamente
            if isinstance(player_data, str):
                logger.debug(f"Player name found directly: {player_data}")
                return player_data
                
            # Se player_data è un dizionario, cerca di estrarre il nome
            elif isinstance(player_data, dict):
                # Cerca chiavi comuni per i nomi
                for key in ["name", "displayName", "username", "value"]:
                    if key in player_data and player_data[key]:
                        logger.debug(f"Player name found in key '{key}': {player_data[key]}")
                        return str(player_data[key])
                
                # Se c'è un valore diretto per l'ID del giocatore
                if player_id in player_data:
                    value = player_data[player_id]
                    logger.debug(f"Player name found for ID '{player_id}': {value}")
                    return str(value)
            
            # Fallback: usa l'ID del giocatore come nome
            logger.warning(f"Impossible to extract player name, using ID as fallback: {player_id}")
            return str(player_id)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error during player name extraction: {str(e)}")
            return str(player_id)

class InventoryTab(QWidget):
    """Tab for inventory management"""
    
    def __init__(self, save_data, parent=None):
        super().__init__(parent)
        self.save_data = save_data
        self.inventory_data = {}
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
        # Registra per gli aggiornamenti della lingua
        language_manager.add_observer(self.update_translations)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels([
            tr("inventory_tab.id", "ID"), 
            tr("inventory_tab.name", "Name"), 
            tr("inventory_tab.quantity", "Quantity"), 
            tr("inventory_tab.description", "Description")
        ])
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.inventory_table)
        
        # Edit panel
        self.edit_group = QGroupBox(tr("inventory_tab.edit_item", "Edit Item"))
        edit_layout = QFormLayout()
        
        self.item_id_edit = QLineEdit()
        self.item_id_edit.setReadOnly(True)
        self.id_label = QLabel(tr("inventory_tab.id", "ID:"))
        edit_layout.addRow(self.id_label, self.item_id_edit)
        
        self.item_name_edit = QLineEdit()
        self.name_label = QLabel(tr("inventory_tab.name", "Name:"))
        edit_layout.addRow(self.name_label, self.item_name_edit)
        
        self.item_quantity_spin = QSpinBox()
        self.item_quantity_spin.setRange(0, 9999)
        self.quantity_label = QLabel(tr("inventory_tab.quantity", "Quantity:"))
        edit_layout.addRow(self.quantity_label, self.item_quantity_spin)
        
        self.item_description_edit = QLineEdit()
        self.description_label = QLabel(tr("inventory_tab.description", "Description:"))
        edit_layout.addRow(self.description_label, self.item_description_edit)
        
        self.edit_group.setLayout(edit_layout)
        layout.addWidget(self.edit_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.add_button = QPushButton(tr("inventory_tab.add_item", "Add Item"))
        self.add_button.clicked.connect(self.add_item)
        buttons_layout.addWidget(self.add_button)
        
        self.update_button = QPushButton(tr("inventory_tab.update_item", "Update Item"))
        self.update_button.setVisible(False)  # Nascondi il pulsante update
        self.remove_button = QPushButton(tr("inventory_tab.remove_item", "Remove Item"))
        self.remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.remove_button)
        
        self.save_button = QPushButton(tr("inventory_tab.save_changes", "Save Changes"))
        self.save_button.setVisible(False)  # Nascondi il pulsante save
        buttons_layout.addWidget(self.save_button)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Connect signals
        self.inventory_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # --- Aggiornamento in tempo reale ---
        self.item_name_edit.textChanged.connect(self.on_item_field_changed)
        self.item_quantity_spin.valueChanged.connect(self.on_item_field_changed)
        self.item_description_edit.textChanged.connect(self.on_item_field_changed)
        
    def update_translations(self):
        """Aggiorna le traduzioni dell'interfaccia quando cambia la lingua"""
        # Aggiorna le intestazioni della tabella
        self.inventory_table.setHorizontalHeaderLabels([
            tr("inventory_tab.id", "ID"), 
            tr("inventory_tab.name", "Name"), 
            tr("inventory_tab.quantity", "Quantity"), 
            tr("inventory_tab.description", "Description")
        ])
        
        # Aggiorna le etichette del form di modifica
        self.edit_group.setTitle(tr("inventory_tab.edit_item", "Edit Item"))
        self.id_label.setText(tr("inventory_tab.id", "ID:"))
        self.name_label.setText(tr("inventory_tab.name", "Name:"))
        self.quantity_label.setText(tr("inventory_tab.quantity", "Quantity:"))
        self.description_label.setText(tr("inventory_tab.description", "Description:"))
        
        # Aggiorna i pulsanti
        self.add_button.setText(tr("inventory_tab.add_item", "Add Item"))
        self.update_button.setText(tr("inventory_tab.update_item", "Update Item"))
        self.remove_button.setText(tr("inventory_tab.remove_item", "Remove Item"))
        self.save_button.setText(tr("inventory_tab.save_changes", "Save Changes"))
        
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
        if data is None:
            return
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
                            # Estrai i dati dell'oggetto
                            item_name = item_id
                            item_quantity = 1
                            item_description = ""
                            
                            # Prova a estrarre il nome e la quantità
                            if isinstance(item_value, dict):
                                if "name" in item_value:
                                    item_name = item_value["name"]
                                elif "value" in item_value and isinstance(item_value["value"], dict) and "name" in item_value["value"]:
                                    item_name = item_value["value"]["name"]
                                    
                                if "quantity" in item_value:
                                    item_quantity = item_value["quantity"]
                                elif "count" in item_value:
                                    item_quantity = item_value["count"]
                                elif "value" in item_value and isinstance(item_value["value"], dict):
                                    if "quantity" in item_value["value"]:
                                        item_quantity = item_value["value"]["quantity"]
                                    elif "count" in item_value["value"]:
                                        item_quantity = item_value["value"]["count"]
                                        
                                if "description" in item_value:
                                    item_description = item_value["description"]
                                elif "value" in item_value and isinstance(item_value["value"], dict) and "description" in item_value["value"]:
                                    item_description = item_value["value"]["description"]
                            
                            # Converti i valori in stringhe
                            item_name = str(item_name)
                            item_quantity = int(item_quantity) if isinstance(item_quantity, (int, float, str)) and str(item_quantity).isdigit() else 1
                            item_description = str(item_description)
                            
                            # Aggiungi l'oggetto alla tabella
                            row = self.inventory_table.rowCount()
                            self.inventory_table.insertRow(row)
                            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                            self.inventory_table.setItem(row, 1, QTableWidgetItem(item_name))
                            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item_quantity)))
                            self.inventory_table.setItem(row, 3, QTableWidgetItem(item_description))
                            
                            # Memorizza i dati dell'oggetto
                            self.inventory_data[item_id] = {
                                "name": item_name,
                                "quantity": item_quantity,
                                "description": item_description,
                                "key": key  # Memorizza la chiave dell'inventario
                            }
                
                # Se non ci sono oggetti, mostra un messaggio
                if self.inventory_table.rowCount() == 0:
                    QMessageBox.information(
                        self,
                        tr("general.info", "Informazione"),
                        tr("inventory_tab.no_items", "No items found in the save or the inventory structure is not supported.")
                    )
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante l'aggiornamento dei dati dell'inventario: {str(e)}\n{traceback_str}")
            QMessageBox.warning(
                self,
                tr("general.error", "Errore"),
                tr("inventory_tab.update_error", f"Failed to update inventory data: {str(e)}")
            )
            
    def add_item(self):
        """Aggiunge un nuovo oggetto all'inventario"""
        if not self.save_data:
            QMessageBox.warning(
                self,
                tr("general.warning", "Attenzione"),
                tr("inventory_tab.no_save_loaded", "Please load a save file first.")
            )
            return
            
        # Chiedi l'ID del nuovo oggetto
        item_id, ok = QInputDialog.getText(
            self,
            tr("inventory_tab.add_item_title", "New Item"),
            tr("inventory_tab.add_item_prompt", "Enter the ID of the new item:")
        )
        
        if ok and item_id:
            # Verifica se l'ID esiste già
            if item_id in self.inventory_data:
                QMessageBox.warning(
                    self,
                    tr("general.warning", "Attenzione"),
                    tr("inventory_tab.duplicate_id", "An item with this ID already exists.")
                )
                return
                
            # Aggiungi l'oggetto alla tabella
            row = self.inventory_table.rowCount()
            self.inventory_table.insertRow(row)
            self.inventory_table.setItem(row, 0, QTableWidgetItem(item_id))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(item_id))  # Nome uguale all'ID per default
            self.inventory_table.setItem(row, 2, QTableWidgetItem("1"))  # Quantità 1 per default
            self.inventory_table.setItem(row, 3, QTableWidgetItem(""))  # Descrizione vuota per default
            
            # Seleziona la riga appena aggiunta
            self.inventory_table.selectRow(row)
            
            # Aggiorna i campi di modifica
            self.item_id_edit.setText(item_id)
            self.item_name_edit.setText(item_id)
            self.item_quantity_spin.setValue(1)
            self.item_description_edit.setText("")
            
            # Memorizza i dati dell'oggetto
            # Usa la prima chiave dell'inventario trovata o crea una nuova
            inventory_key = None
            if "dictionaryOfDictionaries" in self.save_data and "value" in self.save_data["dictionaryOfDictionaries"]:
                dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
                inventory_keys = [key for key in dict_of_dicts.keys() if "inventory" in key.lower() or "item" in key.lower()]
                if inventory_keys:
                    inventory_key = inventory_keys[0]
                else:
                    inventory_key = "playerInventory"
                    dict_of_dicts[inventory_key] = {}
            else:
                if "dictionaryOfDictionaries" not in self.save_data:
                    self.save_data["dictionaryOfDictionaries"] = {"value": {}}
                elif "value" not in self.save_data["dictionaryOfDictionaries"]:
                    self.save_data["dictionaryOfDictionaries"]["value"] = {}
                    
                inventory_key = "playerInventory"
                self.save_data["dictionaryOfDictionaries"]["value"][inventory_key] = {}
                
            self.inventory_data[item_id] = {
                "name": item_id,
                "quantity": 1,
                "description": "",
                "key": inventory_key
            }
            
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("inventory_tab.item_added", "Item added successfully. Edit the details and save.")
            )
            
    def update_item(self):
        """Aggiorna i dati dell'oggetto selezionato"""
        selected_rows = self.inventory_table.selectedItems()
        if not selected_rows:
            return
            
        # Prendi la prima riga selezionata
        row = selected_rows[0].row()
        
        # Recupera l'ID dell'oggetto
        item_id = self.inventory_table.item(row, 0).text()
        
        # Aggiorna i dati nella tabella
        self.inventory_table.item(row, 1).setText(self.item_name_edit.text())
        self.inventory_table.item(row, 2).setText(str(self.item_quantity_spin.value()))
        self.inventory_table.item(row, 3).setText(self.item_description_edit.text())
        
        # Aggiorna i dati in memoria
        if item_id in self.inventory_data:
            self.inventory_data[item_id]["name"] = self.item_name_edit.text()
            self.inventory_data[item_id]["quantity"] = self.item_quantity_spin.value()
            self.inventory_data[item_id]["description"] = self.item_description_edit.text()
            self._update_json_editor()
        
        QMessageBox.information(
            self,
            tr("general.success", "Successo"),
            tr("inventory_tab.item_updated", "Item updated successfully.")
        )
        
    def remove_item(self):
        """Rimuove l'oggetto selezionato"""
        selected_rows = self.inventory_table.selectedItems()
        if not selected_rows:
            return
            
        # Prendi la prima riga selezionata
        row = selected_rows[0].row()
        
        # Recupera l'ID dell'oggetto
        item_id = self.inventory_table.item(row, 0).text()
        
        # Chiedi conferma
        reply = QMessageBox.question(
            self,
            tr("general.warning", "Attenzione"),
            tr("inventory_tab.confirm_remove", "Are you sure you want to remove this item?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Rimuovi l'oggetto dalla tabella
            self.inventory_table.removeRow(row)
            
            # Rimuovi l'oggetto dai dati in memoria
            if item_id in self.inventory_data:
                del self.inventory_data[item_id]
                
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("inventory_tab.item_removed", "Item removed successfully.")
            )
            
    def _update_json_editor(self):
        mw = self.parent()
        if mw and hasattr(mw, 'advanced_tab'):
            mw.advanced_tab.update_json_from_ui()

    def on_item_field_changed(self, *args):
        row = self.inventory_table.currentRow()
        if row < 0:
            return
        item_id = self.item_id_edit.text()
        if not item_id or item_id not in self.inventory_data:
            return
        self.inventory_data[item_id]["name"] = self.item_name_edit.text()
        self.inventory_data[item_id]["quantity"] = self.item_quantity_spin.value()
        self.inventory_data[item_id]["description"] = self.item_description_edit.text()
        # Aggiorna la tabella
        self.inventory_table.item(row, 1).setText(self.item_name_edit.text())
        self.inventory_table.item(row, 2).setText(str(self.item_quantity_spin.value()))
        self.inventory_table.item(row, 3).setText(self.item_description_edit.text())
        # Aggiorna il JSON editor
        self._update_json_editor()
        from core.logger import logger
        logger.info(f"Inventario aggiornato: {item_id} -> {self.inventory_data[item_id]}")
        
        # Aggiorna il JSON in tempo reale
        self.update_json_from_ui()
        
    def update_json_from_ui(self):
        """Aggiorna il JSON con i dati modificati nell'interfaccia utente"""
        try:
            if not self.save_data:
                return
                
            # Verifica che i dati abbiano la struttura attesa
            if "dictionaryOfDictionaries" not in self.save_data:
                self.save_data["dictionaryOfDictionaries"] = {"value": {}}
            elif "value" not in self.save_data["dictionaryOfDictionaries"]:
                self.save_data["dictionaryOfDictionaries"]["value"] = {}
                
            dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
            
            # Aggiorna i dati degli oggetti nel JSON
            for item_id, item_data in self.inventory_data.items():
                key = item_data["key"]
                
                # Assicurati che la chiave dell'inventario esista
                if key not in dict_of_dicts:
                    dict_of_dicts[key] = {}
                    
                # Imposta o aggiorna l'oggetto con le modifiche
                if isinstance(dict_of_dicts[key].get(item_id), dict):
                    # Se l'oggetto esisteva già come dizionario, aggiorna i campi
                    if "name" in dict_of_dicts[key][item_id]:
                        dict_of_dicts[key][item_id]["name"] = item_data["name"]
                    elif "value" in dict_of_dicts[key][item_id] and isinstance(dict_of_dicts[key][item_id]["value"], dict):
                        if "name" in dict_of_dicts[key][item_id]["value"]:
                            dict_of_dicts[key][item_id]["value"]["name"] = item_data["name"]
                            
                    if "quantity" in dict_of_dicts[key][item_id]:
                        dict_of_dicts[key][item_id]["quantity"] = item_data["quantity"]
                    elif "count" in dict_of_dicts[key][item_id]:
                        dict_of_dicts[key][item_id]["count"] = item_data["quantity"]
                    elif "value" in dict_of_dicts[key][item_id] and isinstance(dict_of_dicts[key][item_id]["value"], dict):
                        if "quantity" in dict_of_dicts[key][item_id]["value"]:
                            dict_of_dicts[key][item_id]["value"]["quantity"] = item_data["quantity"]
                        elif "count" in dict_of_dicts[key][item_id]["value"]:
                            dict_of_dicts[key][item_id]["value"]["count"] = item_data["quantity"]
                            
                    if "description" in dict_of_dicts[key][item_id]:
                        dict_of_dicts[key][item_id]["description"] = item_data["description"]
                    elif "value" in dict_of_dicts[key][item_id] and isinstance(dict_of_dicts[key][item_id]["value"], dict):
                        if "description" in dict_of_dicts[key][item_id]["value"]:
                            dict_of_dicts[key][item_id]["value"]["description"] = item_data["description"]
                else:
                    # Se l'oggetto non esisteva, crealo come nuova voce diretta
                    dict_of_dicts[key][item_id] = item_data["quantity"]
                    
            # Se c'è un parent con l'advanced tab, aggiorna l'editor JSON
            self._update_json_editor()
            
            from core.logger import logger
            logger.info("Inventario JSON aggiornato con i dati dell'interfaccia")
            
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Errore nell'aggiornamento del JSON dall'inventario: {str(e)}\n{traceback.format_exc()}")

    def refresh_ui_from_data(self):
        """Aggiorna l'interfaccia utente con i dati del salvataggio"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("InventoryTab.refresh_ui_from_data - Aggiornamento UI dai dati salvati")
        
        if not self.save_data:
            logger.warning("InventoryTab.refresh_ui_from_data - Nessun dato disponibile")
            return
            
        try:
            # Pulisci la tabella e i dati dell'inventario
            self.inventory_table.setRowCount(0)
            self.inventory_data = {}
            
            # Verifica che i dati abbiano la struttura attesa
            if "dictionaryOfDictionaries" not in self.save_data or "value" not in self.save_data["dictionaryOfDictionaries"]:
                logger.warning("InventoryTab.refresh_ui_from_data - Struttura dati non valida")
                return
                
            dict_of_dicts = self.save_data["dictionaryOfDictionaries"]["value"]
            inventory_keys = [key for key in dict_of_dicts.keys() if "inventory" in key.lower() or "item" in key.lower()]
            
            if not inventory_keys:
                logger.warning("InventoryTab.refresh_ui_from_data - Nessuna chiave di inventario trovata")
                return
                
            # Popola la tabella con gli oggetti dell'inventario
            for key in inventory_keys:
                items = dict_of_dicts[key]
                logger.info(f"InventoryTab.refresh_ui_from_data - Processando la chiave di inventario: {key} con {len(items)} elementi")
                
                for item_id, item_value in items.items():
                    try:
                        # Estrai i dati dell'oggetto
                        item_name = item_id
                        item_quantity = 1
                        item_description = ""
                        
                        if isinstance(item_value, dict):
                            if "name" in item_value:
                                item_name = item_value["name"]
                            elif "value" in item_value and isinstance(item_value["value"], dict) and "name" in item_value["value"]:
                                item_name = item_value["value"]["name"]
                                
                            if "quantity" in item_value:
                                item_quantity = item_value["quantity"]
                            elif "count" in item_value:
                                item_quantity = item_value["count"]
                            elif "value" in item_value and isinstance(item_value["value"], dict):
                                if "quantity" in item_value["value"]:
                                    item_quantity = item_value["value"]["quantity"]
                                elif "count" in item_value["value"]:
                                    item_quantity = item_value["value"]["count"]
                                    
                            if "description" in item_value:
                                item_description = item_value["description"]
                            elif "value" in item_value and isinstance(item_value["value"], dict) and "description" in item_value["value"]:
                                item_description = item_value["value"]["description"]
                        
                        # Normalizza i valori
                        item_name = str(item_name)
                        item_quantity = int(item_quantity) if isinstance(item_quantity, (int, float, str)) and str(item_quantity).isdigit() else 1
                        item_description = str(item_description)
                        
                        # Aggiungi l'oggetto alla tabella
                        row = self.inventory_table.rowCount()
                        self.inventory_table.insertRow(row)
                        self.inventory_table.setItem(row, 0, QTableWidgetItem(str(item_id)))
                        self.inventory_table.setItem(row, 1, QTableWidgetItem(item_name))
                        self.inventory_table.setItem(row, 2, QTableWidgetItem(str(item_quantity)))
                        self.inventory_table.setItem(row, 3, QTableWidgetItem(item_description))
                        
                        # Memorizza i dati per riferimento futuro
                        self.inventory_data[item_id] = {
                            "name": item_name,
                            "quantity": item_quantity,
                            "description": item_description,
                            "key": key
                        }
                        
                        logger.info(f"InventoryTab.refresh_ui_from_data - Aggiunto oggetto: {item_id} -> {item_name} (quantità: {item_quantity})")
                    except Exception as e:
                        logger.error(f"InventoryTab.refresh_ui_from_data - Errore elaborazione oggetto {item_id}: {str(e)}")
            
            logger.info(f"InventoryTab.refresh_ui_from_data - Completato con {self.inventory_table.rowCount()} oggetti")
        except Exception as e:
            import traceback
            logger.error(f"InventoryTab.refresh_ui_from_data - Errore: {str(e)}\n{traceback.format_exc()}")

class SettingsTab(QWidget):
    """Tab for application settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_bar = None  # Will be set by the main window
        self.init_ui()
        
        # Registra per gli aggiornamenti della lingua
        language_manager.add_observer(self.update_translations)
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # General settings
        self.general_group = QGroupBox(tr("settings_tab.general_settings", "General Settings"))
        general_layout = QFormLayout()
        
        # Theme
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Dark")
        self.theme_combo.addItem("Light")
        self.theme_label = QLabel(tr("settings_tab.theme", "Theme:"))
        general_layout.addRow(self.theme_label, self.theme_combo)
        
        # Language
        self.language_combo = QComboBox()
        self.language_label = QLabel(tr("settings_tab.language", "Language:"))
        general_layout.addRow(self.language_label, self.language_combo)
        
        # Auto backup
        self.auto_backup_check = QCheckBox(tr("settings_tab.enable", "Enable"))
        self.auto_backup_label = QLabel(tr("settings_tab.auto_backup", "Auto Backup:"))
        general_layout.addRow(self.auto_backup_label, self.auto_backup_check)
        
        # Backup folder
        backup_folder_layout = QHBoxLayout()
        self.backup_folder_edit = QLineEdit()
        self.backup_folder_edit.setReadOnly(True)
        self.backup_folder_button = QPushButton(tr("settings_tab.browse", "Browse"))
        self.backup_folder_button.clicked.connect(self.browse_backup_folder)
        backup_folder_layout.addWidget(self.backup_folder_edit)
        backup_folder_layout.addWidget(self.backup_folder_button)
        self.backup_folder_label = QLabel(tr("settings_tab.backup_folder", "Backup Folder:"))
        general_layout.addRow(self.backup_folder_label, backup_folder_layout)
        
        self.general_group.setLayout(general_layout)
        layout.addWidget(self.general_group)
        
        # Advanced settings
        self.advanced_group = QGroupBox(tr("settings_tab.advanced_settings", "Advanced Settings"))
        advanced_layout = QFormLayout()
        
        # Backup count
        self.backup_count_spin = QSpinBox()
        self.backup_count_spin.setRange(1, 100)
        self.backup_count_spin.setValue(5)
        self.backup_count_label = QLabel(tr("settings_tab.backup_count", "Number of backups to keep:"))
        advanced_layout.addRow(self.backup_count_label, self.backup_count_spin)
        
        # Backup interval
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(1, 60)
        self.backup_interval_spin.setValue(5)
        self.backup_interval_label = QLabel(tr("settings_tab.backup_interval", "Auto backup interval:"))
        advanced_layout.addRow(self.backup_interval_label, self.backup_interval_spin)
        
        self.advanced_group.setLayout(advanced_layout)
        layout.addWidget(self.advanced_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton(tr("settings_tab.save_settings", "Save Settings"))
        self.save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.save_button)
        
        self.reset_button = QPushButton(tr("settings_tab.reset_defaults", "Reset Defaults"))
        self.reset_button.clicked.connect(self.reset_defaults)
        buttons_layout.addWidget(self.reset_button)
        
        layout.addLayout(buttons_layout)
        
        # Info label
        self.info_label = QLabel(tr("settings_tab.settings_info", "Settings are automatically saved when the application is closed."))
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
        # Carica le lingue disponibili
        self.load_languages()
        
        # Carica le impostazioni
        self.load_settings()
        
    def update_translations(self):
        """Aggiorna le traduzioni dell'interfaccia quando cambia la lingua"""
        self.general_group.setTitle(tr("settings_tab.general_settings", "General Settings"))
        self.theme_label.setText(tr("settings_tab.theme", "Theme:"))
        self.language_label.setText(tr("settings_tab.language", "Language:"))
        self.auto_backup_label.setText(tr("settings_tab.auto_backup", "Auto Backup:"))
        self.auto_backup_check.setText(tr("settings_tab.enable", "Enable"))
        self.backup_folder_label.setText(tr("settings_tab.backup_folder", "Backup Folder:"))
        self.backup_folder_button.setText(tr("settings_tab.browse", "Browse"))
        self.advanced_group.setTitle(tr("settings_tab.advanced_settings", "Advanced Settings"))
        self.backup_count_label.setText(tr("settings_tab.backup_count", "Number of backups to keep:"))
        self.backup_interval_label.setText(tr("settings_tab.backup_interval", "Auto backup interval:"))
        self.save_button.setText(tr("settings_tab.save_settings", "Save Settings"))
        self.reset_button.setText(tr("settings_tab.reset_defaults", "Reset Defaults"))
        self.info_label.setText(tr("settings_tab.settings_info", "Settings are automatically saved when the application is closed."))
        
    def load_languages(self):
        """Carica le lingue disponibili"""
        try:
            # Ottieni le lingue disponibili
            languages = language_manager.get_available_languages()
            
            # Pulisci il combo box
            self.language_combo.clear()
            
            # Aggiungi le lingue
            for code, name in languages.items():
                self.language_combo.addItem(name, code)
                
            # Seleziona la lingua corrente
            current_lang = language_manager.get_current_language()
            for i in range(self.language_combo.count()):
                if self.language_combo.itemData(i) == current_lang:
                    self.language_combo.setCurrentIndex(i)
                    break
                    
            # Connetti il segnale per il cambio di lingua
            self.language_combo.currentIndexChanged.connect(self.on_language_changed)
            
        except Exception as e:
            print(f"Errore durante il caricamento delle lingue: {str(e)}")
            
    def on_language_changed(self, index):
        """Gestisce il cambio di lingua"""
        if index < 0:
            return
            
        # Ottieni il codice della lingua selezionata
        lang_code = self.language_combo.itemData(index)
        
        # Imposta la lingua
        language_manager.set_language(lang_code)
        
    def load_settings(self):
        """Carica le impostazioni"""
        try:
            # Trova il percorso del file settings.json
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            settings_path = os.path.join(root_dir, "settings.json")
            
            if os.path.exists(settings_path):
                with open(settings_path, "r") as f:
                    settings = json.load(f)
                    
                # Imposta il tema
                if "theme" in settings:
                    theme_index = 0 if settings["theme"] == "dark" else 1
                    self.theme_combo.setCurrentIndex(theme_index)
                    
                # Imposta il backup automatico
                if "auto_backup" in settings:
                    self.auto_backup_check.setChecked(settings["auto_backup"])
                    
                # Imposta la cartella di backup
                if "backup_path" in settings:
                    self.backup_folder_edit.setText(settings["backup_path"])
                    
                # Imposta il numero di backup
                if "backup_count" in settings:
                    self.backup_count_spin.setValue(settings["backup_count"])
                    
                # Imposta l'intervallo di backup
                if "backup_interval" in settings:
                    self.backup_interval_spin.setValue(settings["backup_interval"])
            else:
                # Impostazioni predefinite
                self.theme_combo.setCurrentIndex(0)  # Dark
                self.auto_backup_check.setChecked(True)
                self.backup_folder_edit.setText(os.path.join(root_dir, "backups"))
                self.backup_count_spin.setValue(5)
                self.backup_interval_spin.setValue(5)
                
        except Exception as e:
            print(f"Errore durante il caricamento delle impostazioni: {str(e)}")
            
    def browse_backup_folder(self):
        """Apre il dialogo per selezionare la cartella di backup"""
        folder = QFileDialog.getExistingDirectory(
            self,
            tr("settings_tab.select_backup_folder", "Select Backup Folder"),
            self.backup_folder_edit.text()
        )
        
        if folder:
            self.backup_folder_edit.setText(folder)
            
    def save_settings(self):
        """Salva le impostazioni"""
        try:
            # Trova il percorso del file settings.json
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            settings_path = os.path.join(root_dir, "settings.json")
            
            # Crea le impostazioni
            settings = {
                "theme": "dark" if self.theme_combo.currentIndex() == 0 else "light",
                "language": self.language_combo.itemData(self.language_combo.currentIndex()),
                "auto_backup": self.auto_backup_check.isChecked(),
                "backup_path": self.backup_folder_edit.text(),
                "backup_count": self.backup_count_spin.value(),
                "backup_interval": self.backup_interval_spin.value()
            }
            
            # Salva le impostazioni
            with open(settings_path, "w") as f:
                json.dump(settings, f, indent=4)
                
            # Aggiorna le impostazioni del backup manager
            from core.backup import backup_manager
            backup_manager.update_settings(settings)
                
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("settings_tab.settings_saved", "Settings have been saved successfully.")
            )
            
        except Exception as e:
            print(f"Errore durante il salvataggio delle impostazioni: {str(e)}")
            QMessageBox.critical(
                self,
                tr("general.error", "Errore"),
                tr("settings_tab.save_error", f"An error occurred while saving settings: {str(e)}")
            )
            
    def reset_defaults(self):
        """Ripristina le impostazioni predefinite"""
        try:
            # Impostazioni predefinite
            self.theme_combo.setCurrentIndex(0)  # Dark
            self.auto_backup_check.setChecked(True)
            
            # Trova il percorso della cartella backups
            root_dir = os.environ.get("REPO_SAVE_EDITOR_ROOT", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            self.backup_folder_edit.setText(os.path.join(root_dir, "backups"))
            
            self.backup_count_spin.setValue(5)
            self.backup_interval_spin.setValue(5)
            
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("settings_tab.settings_reset", "Settings have been reset to default values.")
            )
            
        except Exception as e:
            print(f"Errore durante il ripristino delle impostazioni predefinite: {str(e)}")
            QMessageBox.critical(
                self,
                tr("general.error", "Errore"),
                tr("settings_tab.reset_error", f"An error occurred while resetting settings: {str(e)}")
            )

class JsonSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for JSON"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#ce9178"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#b5cea8"))
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
        
        # Boolean format
        boolean_format = QTextCharFormat()
        boolean_format.setForeground(QColor("#569cd6"))
        self.highlighting_rules.append((re.compile(r'\b(true|false|null)\b'), boolean_format))
        
        # Bracket format
        bracket_format = QTextCharFormat()
        bracket_format.setForeground(QColor("#d4d4d4"))
        self.highlighting_rules.append((re.compile(r'[\[\]{}]'), bracket_format))
        
        # Comma format
        comma_format = QTextCharFormat()
        comma_format.setForeground(QColor("#d4d4d4"))
        self.highlighting_rules.append((re.compile(r','), comma_format))
        
        # Colon format
        colon_format = QTextCharFormat()
        colon_format.setForeground(QColor("#d4d4d4"))
        self.highlighting_rules.append((re.compile(r':'), colon_format))
        
    def highlightBlock(self, text):
        """Highlight the block of text"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class AdvancedTab(QWidget):
    """Tab for advanced editing of save data"""
    
    def __init__(self, save_data, parent=None):
        super().__init__(parent)
        self.save_data = save_data
        self.status_bar = None
        self.init_ui()
        language_manager.add_observer(self.update_translations)
        # Sincronizzazione bidirezionale
        self.json_editor.textChanged.connect(self.on_json_edit)
        self._block_json_update = False

    def on_json_edit(self):
        if self._block_json_update:
            return
        try:
            new_data = json.loads(self.json_editor.toPlainText())
            self.save_data.clear()
            self.save_data.update(new_data)
            # Aggiorna tutti i tab (player, inventory, ecc.)
            mw = self.parent()
            if mw and hasattr(mw, 'player_tab'):
                mw.player_tab.update_data(self.save_data)
            if mw and hasattr(mw, 'inventory_tab'):
                mw.inventory_tab.update_data(self.save_data)
            # Aggiorna la struttura
            self.update_structure_viewer(self.save_data)
        except Exception:
            pass

    def update_json_from_ui(self):
        self._block_json_update = True
        try:
            self.json_editor.setText(json.dumps(self.save_data, indent=4))
        finally:
            self._block_json_update = False

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Splitter per dividere l'editor JSON e la struttura
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Editor JSON
        json_layout = QVBoxLayout()
        self.json_label = QLabel(tr("advanced_tab.json_editor", "JSON Editor"))
        json_layout.addWidget(self.json_label)
        
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Courier New", 10))
        self.json_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Syntax highlighter
        self.highlighter = JsonSyntaxHighlighter(self.json_editor.document())
        
        json_layout.addWidget(self.json_editor)
        
        # Buttons for JSON editor
        json_buttons_layout = QHBoxLayout()
        
        self.format_button = QPushButton(tr("advanced_tab.format_json", "Format JSON"))
        self.format_button.clicked.connect(self.format_json)
        json_buttons_layout.addWidget(self.format_button)
        
        self.validate_button = QPushButton(tr("advanced_tab.validate_json", "Validate JSON"))
        self.validate_button.clicked.connect(self.validate_json)
        json_buttons_layout.addWidget(self.validate_button)
        
        self.apply_button = QPushButton(tr("advanced_tab.apply_changes", "Apply Changes"))
        self.apply_button.clicked.connect(self.apply_changes)
        json_buttons_layout.addWidget(self.apply_button)
        
        json_layout.addLayout(json_buttons_layout)
        
        # Warning label
        self.warning_label = QLabel(tr("advanced_tab.warning", "Warning: direct editing of JSON can cause compatibility issues with the game. Use with caution."))
        self.warning_label.setStyleSheet("color: #f0a30a; font-style: italic;")
        self.warning_label.setWordWrap(True)
        json_layout.addWidget(self.warning_label)
        
        json_widget = QWidget()
        json_widget.setLayout(json_layout)
        splitter.addWidget(json_widget)
        
        # JSON structure viewer
        structure_layout = QVBoxLayout()
        self.structure_label = QLabel(tr("advanced_tab.json_structure", "JSON Structure"))
        structure_layout.addWidget(self.structure_label)
        
        self.structure_viewer = QTextEdit()
        self.structure_viewer.setReadOnly(True)
        self.structure_viewer.setFont(QFont("Courier New", 10))
        structure_layout.addWidget(self.structure_viewer)
        
        structure_widget = QWidget()
        structure_widget.setLayout(structure_layout)
        splitter.addWidget(structure_widget)
        
        # Set initial sizes
        splitter.setSizes([500, 300])
        
        layout.addWidget(splitter)
        
        self.setLayout(layout)
        
    def update_translations(self):
        """Aggiorna le traduzioni dell'interfaccia quando cambia la lingua"""
        self.json_label.setText(tr("advanced_tab.json_editor", "JSON Editor"))
        self.structure_label.setText(tr("advanced_tab.json_structure", "JSON Structure"))
        self.format_button.setText(tr("advanced_tab.format_json", "Format JSON"))
        self.validate_button.setText(tr("advanced_tab.validate_json", "Validate JSON"))
        self.apply_button.setText(tr("advanced_tab.apply_changes", "Apply Changes"))
        self.warning_label.setText(tr("advanced_tab.warning", "Warning: direct editing of JSON can cause compatibility issues with the game. Use with caution."))
        
    def update_data(self, data: Dict[str, Any]):
        """
        Update the tab with save data
        
        Args:
            data: Save data
        """
        try:
            self.save_data = data
            
            # Format and display the JSON
            json_str = json.dumps(data, indent=4)
            self.json_editor.setText(json_str)
            
            # Update the structure viewer
            self.update_structure_viewer(data)
            
        except Exception as e:
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Errore durante l'aggiornamento dei dati avanzati: {str(e)}\n{traceback_str}")
            QMessageBox.warning(
                self,
                tr("general.error", "Errore"),
                tr("advanced_tab.update_error", f"Failed to update advanced data: {str(e)}")
            )
            
    def update_structure_viewer(self, data: Dict[str, Any], prefix=""):
        """
        Update the structure viewer with a simplified view of the JSON structure
        
        Args:
            data: Data to display
            prefix: Prefix for nested structures
        """
        try:
            structure_text = ""
            
            def add_structure(obj, prefix="", max_depth=3, current_depth=0):
                nonlocal structure_text
                
                if current_depth > max_depth:
                    structure_text += f"{prefix}...\n"
                    return
                    
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if isinstance(value, dict):
                            structure_text += f"{prefix}{key}: {{\n"
                            add_structure(value, prefix + "  ", max_depth, current_depth + 1)
                            structure_text += f"{prefix}}}\n"
                        elif isinstance(value, list):
                            structure_text += f"{prefix}{key}: [\n"
                            if len(value) > 0:
                                if isinstance(value[0], (dict, list)):
                                    add_structure(value[0], prefix + "  ", max_depth, current_depth + 1)
                                else:
                                    structure_text += f"{prefix}  {type(value[0]).__name__}[{len(value)}]\n"
                            structure_text += f"{prefix}]\n"
                        else:
                            value_type = type(value).__name__
                            value_preview = str(value)
                            if len(value_preview) > 50:
                                value_preview = value_preview[:47] + "..."
                            structure_text += f"{prefix}{key}: {value_type} = {value_preview}\n"
                elif isinstance(obj, list):
                    if len(obj) > 0:
                        structure_text += f"{prefix}[\n"
                        if isinstance(obj[0], (dict, list)):
                            add_structure(obj[0], prefix + "  ", max_depth, current_depth + 1)
                        else:
                            structure_text += f"{prefix}  {type(obj[0]).__name__}[{len(obj)}]\n"
                        structure_text += f"{prefix}]\n"
                    else:
                        structure_text += f"{prefix}[]\n"
                else:
                    value_type = type(obj).__name__
                    value_preview = str(obj)
                    if len(value_preview) > 50:
                        value_preview = value_preview[:47] + "..."
                    structure_text += f"{prefix}{value_type} = {value_preview}\n"
                    
            add_structure(data, prefix)
            self.structure_viewer.setText(structure_text)
            
        except Exception as e:
            print(f"Errore durante l'aggiornamento della struttura: {str(e)}")
            self.structure_viewer.setText(f"Error: {str(e)}")
            
    def format_json(self):
        """Format the JSON in the editor"""
        try:
            # Get the current text
            json_text = self.json_editor.toPlainText()
            
            # Parse and format
            data = json.loads(json_text)
            formatted_json = json.dumps(data, indent=4)
            
            # Update the editor
            self.json_editor.setText(formatted_json)
            
            # Update the status bar
            if self.status_bar:
                self.status_bar.showMessage(tr("advanced_tab.json_formatted", "JSON formatted successfully."))
                
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("general.error", "Errore"),
                tr("advanced_tab.json_invalid", f"JSON is not valid: {str(e)}")
            )
            
    def validate_json(self):
        """Validate the JSON in the editor"""
        try:
            # Get the current text
            json_text = self.json_editor.toPlainText()
            
            # Parse to validate
            json.loads(json_text)
            
            # Update the status bar
            if self.status_bar:
                self.status_bar.showMessage(tr("advanced_tab.json_valid", "JSON is syntactically valid."))
                
            QMessageBox.information(
                self,
                tr("general.success", "Successo"),
                tr("advanced_tab.json_valid", "JSON is syntactically valid.")
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("general.error", "Errore"),
                tr("advanced_tab.json_invalid", f"JSON is not valid: {str(e)}")
            )
            
    def apply_changes(self):
        """Apply the changes to the save data"""
        try:
            # Get the current text
            json_text = self.json_editor.toPlainText()
            
            # Parse to validate
            new_data = json.loads(json_text)
            
            # Confirm changes
            reply = QMessageBox.question(
                self,
                tr("general.warning", "Attenzione"),
                tr("advanced_tab.confirm_changes", "Are you sure you want to apply the changes to the JSON? This could cause compatibility issues with the game."),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Update the save data
                self.save_data = new_data
                
                # Update the structure viewer
                self.update_structure_viewer(new_data)
                
                # Update the status bar
                if self.status_bar:
                    self.status_bar.showMessage(tr("advanced_tab.changes_applied", "JSON changes have been applied successfully."))
                    
                QMessageBox.information(
                    self,
                    tr("general.success", "Successo"),
                    tr("advanced_tab.changes_applied", "JSON changes have been applied successfully.")
                )
                
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("general.error", "Errore"),
                tr("advanced_tab.json_invalid", f"JSON is not valid: {str(e)}")
            )

    def refresh_ui_from_data(self):
        """Aggiorna l'interfaccia utente con i dati del salvataggio"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("AdvancedTab.refresh_ui_from_data - Aggiornamento UI dai dati salvati")
        
        if not self.save_data:
            logger.warning("AdvancedTab.refresh_ui_from_data - Nessun dato disponibile")
            return
            
        try:
            # Formatta e visualizza il JSON
            json_str = json.dumps(self.save_data, indent=4)
            self.json_editor.setText(json_str)
            
            # Aggiorna la visualizzazione della struttura
            self.update_structure_viewer(self.save_data)
            
            logger.info("AdvancedTab.refresh_ui_from_data - Completato con successo")
        except Exception as e:
            import traceback
            logger.error(f"AdvancedTab.refresh_ui_from_data - Errore: {str(e)}\n{traceback.format_exc()}")
