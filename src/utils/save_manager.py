"""
Modulo di gestione dei salvataggi per R.E.P.O Save Editor
Gestisce l'apertura, la decodifica, la modifica e il salvataggio dei file di gioco
"""

import json
import re
import requests
import webbrowser
import os
import logging
from datetime import datetime
from xml.etree import ElementTree
from PIL import Image
from pathlib import Path
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from core.decrypt import decrypt_es3
from core.encrypt import encrypt_es3

# Configurazione del logging
DEBUGLEVEL = None

if DEBUGLEVEL:
    logging.basicConfig(level=DEBUGLEVEL)
    ui_logger = logging.getLogger("PyQt6")
    ui_logger.setLevel(DEBUGLEVEL)
    logger = logging.getLogger(__name__)
    logger.setLevel(DEBUGLEVEL)

# Creare la directory cache se non esiste
CACHE_DIR = Path.home() / ".cache" / "noedl.xyz"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

if DEBUGLEVEL:
    logger.info("Cache directory created.")

version = "1.0.0"
json_data = {}
savefile_dir = Path.home() / "AppData" / "LocalLow" / "semiwork" / "Repo" / "saves"
savefilename = None
players = []
player_entries = {}

if DEBUGLEVEL:
    logger.info("Save file directory set. Path: " + str(savefile_dir))

class SaveManager:
    """Classe per gestire i file di salvataggio del gioco R.E.P.O"""
    
    def __init__(self):
        """Inizializza il gestore dei salvataggi"""
        self.json_data = json_data  # Usa la variabile globale
        self.savefile_dir = savefile_dir  # Usa la variabile globale
        self.savefilename = None
        self.version = version  # Usa la variabile globale
        self.current_file = None
        self.save_data = {}  # Alias per json_data
        self.save_dir = self.savefile_dir  # Alias per compatibilità
        self.cache_dir = CACHE_DIR
        
        if DEBUGLEVEL:
            logger.info(f"SaveManager inizializzato. Directory predefinita: {self.savefile_dir}")
    
    def create_entry(self, label, parent, color, update_callback=None, tooltip=None):
        """Funzione di compatibilità per creare campi di input
        
        Questa funzione è mantenuta per compatibilità con il codice originale,
        ma andrà implementata nell'interfaccia UI.
        """
        if DEBUGLEVEL:
            ui_logger.info(f"Creating entry field for: {label}")
        
        # Per compatibilità con il codice originale customtkinter
        return None
    
    def highlight_json(self, textbox=None):
        """Evidenzia la sintassi JSON nel widget di testo
        
        Questa funzione è mantenuta per compatibilità con il codice originale
        ma andrà implementata nell'interfaccia UI.
        """
        if DEBUGLEVEL:
            ui_logger.info("JSON syntax highlighted.")
        
        # Per compatibilità con il codice originale customtkinter
        return None
    
    def update_json_data(self, event=None, entries=None):
        """Aggiorna i dati JSON con i valori inseriti nei campi
        
        Args:
            event: Evento che ha innescato l'aggiornamento (per compatibilità)
            entries: Dizionario con i campi da aggiornare
            
        Returns:
            dict: Dati JSON aggiornati
        """
        global json_data
        
        if entries:
            try:
                if 'level' in entries and entries['level'] is not None:
                    json_data['dictionaryOfDictionaries']['value']['runStats']['level'] = int(entries['level'])
                
                if 'currency' in entries and entries['currency'] is not None:
                    json_data['dictionaryOfDictionaries']['value']['runStats']['currency'] = int(entries['currency'])
                
                if 'lives' in entries and entries['lives'] is not None:
                    json_data['dictionaryOfDictionaries']['value']['runStats']['lives'] = int(entries['lives'])
                
                if 'charging' in entries and entries['charging'] is not None:
                    json_data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'] = int(entries['charging'])
                
                if 'haul' in entries and entries['haul'] is not None:
                    json_data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'] = int(entries['haul'])
                
                if 'teamname' in entries and entries['teamname'] is not None:
                    json_data['teamName']['value'] = entries['teamname']
                
                if 'players' in entries and entries['players'] is not None:
                    for player in entries['players']:
                        player_id = player['id']
                        player_health = player['health']
                        json_data['dictionaryOfDictionaries']['value']['playerHealth'][player_id] = player_health
                
                self.json_data = json_data
                self.save_data = json_data
                
                if DEBUGLEVEL:
                    logger.info("JSON data updated.")
            except (ValueError, KeyError) as e:
                if DEBUGLEVEL:
                    logger.error(f"Error updating JSON data: {e}")
        
        return json_data
    
    def on_json_edit(self, json_text):
        """Aggiorna i campi dell'interfaccia quando il testo JSON viene modificato
        
        Args:
            json_text: Testo JSON modificato
            
        Returns:
            dict: Dizionario con i dati estratti dal JSON, o None se il JSON non è valido
        """
        global json_data
        
        try:
            updated_data = json.loads(json_text)
            json_data = updated_data
            self.json_data = updated_data
            self.save_data = updated_data
            
            if DEBUGLEVEL:
                logger.info("JSON data updated from editor.")
                
            # Estrai i dati da fornire all'UI
            extracted_data = {
                'level': updated_data['dictionaryOfDictionaries']['value']['runStats']['level'],
                'currency': updated_data['dictionaryOfDictionaries']['value']['runStats']['currency'],
                'lives': updated_data['dictionaryOfDictionaries']['value']['runStats']['lives'],
                'charging': updated_data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'],
                'haul': updated_data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'],
                'teamname': updated_data['teamName']['value'],
                'player_health': {}
            }
            
            for player_id in updated_data['dictionaryOfDictionaries']['value']['playerHealth']:
                extracted_data['player_health'][player_id] = updated_data['dictionaryOfDictionaries']['value']['playerHealth'][player_id]
            
            return extracted_data
        except json.JSONDecodeError:
            if DEBUGLEVEL:
                logger.error("Failed to update JSON data from editor.")
            return None
    
    def open_file(self, file_path):
        """Apre un file di salvataggio del gioco
        
        Args:
            file_path: percorso del file da aprire
            
        Returns:
            tuple: (bool, str) dove bool indica se il file è stato aperto con successo e str è un messaggio
        """
        global json_data, savefilename
            
        try:
            decrypted_data = decrypt_es3(file_path, "Why would you want to cheat?... :o It's no fun. :') :'D")
            json_data = json.loads(decrypted_data)
            savefilename = Path(file_path).name
            self.json_data = json_data
            self.save_data = json_data
            self.savefilename = savefilename
            self.current_file = Path(file_path)
            
            if DEBUGLEVEL:
                logger.info(f"File aperto con successo: {file_path}")
                
            return True, f"File aperto: {file_path}"
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'apertura del file: {e}")
                
            return False, str(e)
    
    def save_file(self, file_path):
        """Salva i dati modificati in un file di salvataggio
        
        Args:
            file_path: percorso dove salvare il file
            
        Returns:
            tuple: (bool, str) dove bool indica se il file è stato salvato con successo e str è un messaggio
        """
        global json_data, savefilename
        
        if not json_data:
            if DEBUGLEVEL:
                logger.error("Nessun dato da salvare.")
                
            return False, "Nessun dato da salvare."
        
        try:
            # Converti il JSON in stringa formattata
            json_str = json.dumps(json_data, indent=4)
            
            # Cripta i dati
            success = encrypt_es3(json_str, file_path, "Why would you want to cheat?... :o It's no fun. :') :'D")
            
            if success:
                self.current_file = Path(file_path)
                self.savefilename = Path(file_path).name
                
                if DEBUGLEVEL:
                    logger.info(f"File salvato con successo: {file_path}")
                
                return True, f"File salvato: {file_path}"
            else:
                if DEBUGLEVEL:
                    logger.error(f"Errore nel salvataggio del file: {file_path}")
                
                return False, f"Errore nel salvataggio del file"
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nel salvataggio del file: {e}")
            
            return False, str(e)
    
    def save_data(self, parent=None, file_path=None):
        """Alias per save_file per compatibilità con il codice originale"""
        return self.save_file(file_path)
    
    def fetch_steam_profile_picture(self, player_id):
        """Recupera e memorizza nella cache l'immagine profilo di Steam
        
        Args:
            player_id: ID Steam del giocatore
            
        Returns:
            str: Percorso dell'immagine, o None se non è stato possibile recuperarla
        """
        cached_image_path = self.cache_dir / f"{player_id}.png"
        if cached_image_path.exists():
            return str(cached_image_path)

        try:
            url = f"https://steamcommunity.com/profiles/{player_id}/?xml=1"
            response = requests.get(url)
            
            if response.status_code == 200:
                tree = ElementTree.fromstring(response.content)
                avatar_icon = tree.find('avatarIcon')
                
                if avatar_icon is not None:
                    img_url = avatar_icon.text
                    img_data = requests.get(img_url).content
                    
                    with open(cached_image_path, 'wb') as file:
                        file.write(img_data)
                        
                    if DEBUGLEVEL:
                        logger.info(f"Immagine profilo Steam per ID giocatore: {player_id} recuperata e memorizzata nella cache.")
                        
                    return str(cached_image_path)
            
            if DEBUGLEVEL:
                logger.error(f"Failed to fetch Steam profile picture for player ID: {player_id}")
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nel recupero dell'immagine profilo Steam per ID giocatore: {player_id}, Errore: {e}")

        # Immagine predefinita se non è stato possibile recuperare l'immagine profilo
        default_icon = Path(__file__).parent.parent / "icon.ico"
        if default_icon.exists():
            return str(default_icon)
        
        return None
    
    def update_ui_from_json(self, data):
        """Estrai i dati dal JSON per aggiornare l'interfaccia utente
        
        Args:
            data: Dati JSON da elaborare
        
        Returns:
            dict: Dati estratti pronti per l'UI
        """
        global json_data, players, player_entries
        players.clear()
        player_entries.clear()
        
        extracted_data = {
            'world_data': {
                'level': data['dictionaryOfDictionaries']['value']['runStats']['level'],
                'currency': data['dictionaryOfDictionaries']['value']['runStats']['currency'],
                'lives': data['dictionaryOfDictionaries']['value']['runStats']['lives'],
                'charging': data['dictionaryOfDictionaries']['value']['runStats']['chargingStationCharge'],
                'haul': data['dictionaryOfDictionaries']['value']['runStats']['totalHaul'],
                'teamname': data['teamName']['value']
            },
            'players': []
        }
        
        # Estrai dati dei giocatori
        for player_id, player_name in data["playerNames"]["value"].items():
            player_health = data["dictionaryOfDictionaries"]["value"]["playerHealth"][player_id]
            
            # Raccogli gli upgrade del giocatore
            player_upgrades = {
                'health': data['dictionaryOfDictionaries']['value']['playerUpgradeHealth'][player_id],
                'stamina': data['dictionaryOfDictionaries']['value']['playerUpgradeStamina'][player_id],
                'extra_jump': data['dictionaryOfDictionaries']['value']['playerUpgradeExtraJump'][player_id],
                'launch': data['dictionaryOfDictionaries']['value']['playerUpgradeLaunch'][player_id],
                'map_player_count': data['dictionaryOfDictionaries']['value']['playerUpgradeMapPlayerCount'][player_id],
                'speed': data['dictionaryOfDictionaries']['value']['playerUpgradeSpeed'][player_id],
                'strength': data['dictionaryOfDictionaries']['value']['playerUpgradeStrength'][player_id],
                'range': data['dictionaryOfDictionaries']['value']['playerUpgradeRange'][player_id],
                'throw': data['dictionaryOfDictionaries']['value']['playerUpgradeThrow'][player_id]
            }
            
            player_data = {
                'id': player_id,
                'name': player_name,
                'health': player_health,
                'upgrades': player_upgrades,
                'avatar': self.fetch_steam_profile_picture(player_id)
            }
            
            # Aggiungi il giocatore alla lista principale
            players.append({"id": player_id, "name": player_name, "health": player_health})
            
            # Aggiungi il giocatore ai dati estratti
            extracted_data['players'].append(player_data)
        
        # Salva i dati JSON
        json_data = data
        self.json_data = data
        self.save_data = data
        
        if DEBUGLEVEL:
            logger.info("UI data extracted from JSON.")
        
        return extracted_data
    
    def get_latest_version(self):
        """Ottiene l'ultima versione da GitHub
        
        Returns:
            str: Versione più recente o "Unknown" in caso di errore
        """
        try:
            response = requests.get(f"https://api.github.com/repos/seregonwar/R.E.P.O-Save-Editor/releases/latest", timeout=5)
            data = response.json()
            if DEBUGLEVEL:
                logger.info("Latest version fetched from GitHub API. Version: " + data.get("tag_name", "Unknown"))
            return data.get("tag_name", "Unknown")
        except requests.exceptions.RequestException:
            if DEBUGLEVEL:
                logger.error("Failed to fetch latest version from GitHub API.")
            return "Unknown"
    
    def get_player_list(self):
        """Ottiene la lista dei giocatori dal file di salvataggio
        
        Returns:
            list: Lista di dizionari contenenti informazioni sui giocatori
        """
        global players
        
        if not self.json_data or "playerNames" not in self.json_data:
            return []
            
        try:
            players = []
            
            for player_id, player_name in self.json_data["playerNames"]["value"].items():
                if "dictionaryOfDictionaries" in self.json_data and "value" in self.json_data["dictionaryOfDictionaries"]:
                    player_data = self.json_data["dictionaryOfDictionaries"]["value"]
                    
                    # Valori predefiniti
                    health = 100
                    if "playerHealth" in player_data and player_id in player_data["playerHealth"]:
                        health = player_data["playerHealth"][player_id]
                    
                    # Raccogli tutti gli upgrade disponibili per il giocatore
                    upgrades = {}
                    for upgrade_type in ["playerUpgradeHealth", "playerUpgradeStamina", 
                                        "playerUpgradeExtraJump", "playerUpgradeLaunch",
                                        "playerUpgradeMapPlayerCount", "playerUpgradeSpeed",
                                        "playerUpgradeStrength", "playerUpgradeRange",
                                        "playerUpgradeThrow"]:
                        if upgrade_type in player_data and player_id in player_data[upgrade_type]:
                            upgrades[upgrade_type.replace("playerUpgrade", "").lower()] = player_data[upgrade_type][player_id]
                    
                    player_info = {
                        "id": player_id,
                        "name": player_name,
                        "health": health,
                        "upgrades": upgrades
                    }
                    
                    players.append(player_info)
            
            if DEBUGLEVEL:
                logger.info(f"Ottenuti {len(players)} giocatori dal file di salvataggio.")
                
            return players
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'ottenere la lista dei giocatori: {e}")
            return []
    
    def extract_player_data(self):
        """Alias di get_player_list per compatibilità con il codice esistente
        
        Returns:
            list: Lista di dizionari contenenti informazioni sui giocatori
        """
        return self.get_player_list()
    
    def update_player_data(self, player_id, field, value):
        """Aggiorna i dati di un giocatore
        
        Args:
            player_id: ID del giocatore
            field: Campo da aggiornare (health, upgrade.health, ecc.)
            value: Nuovo valore
            
        Returns:
            bool: True se l'aggiornamento è riuscito, False altrimenti
        """
        global json_data
        
        try:
            if not json_data or "dictionaryOfDictionaries" not in json_data:
                return False
                
            data = json_data["dictionaryOfDictionaries"]["value"]
            
            # Gestisci i diversi campi
            if field == "health":
                if "playerHealth" not in data:
                    data["playerHealth"] = {}
                data["playerHealth"][player_id] = value
            elif field.startswith("upgrade_"):
                upgrade_type = field.split("_")[1]
                # Gestisci la capitalizzazione delle prime lettere delle parole in camelCase
                if upgrade_type == "extraJump" or upgrade_type == "mapPlayerCount":
                    # Mantieni la capitalizzazione originale per campi specifici
                    upgrade_key = f"playerUpgrade{upgrade_type}"
                elif upgrade_type == "agility":
                    # Caso speciale: agility viene mappato su stamina
                    upgrade_key = "playerUpgradeStamina"
                elif upgrade_type == "intelligence":
                    # Caso speciale: intelligence viene mappato su range
                    upgrade_key = "playerUpgradeRange"
                elif upgrade_type == "endurance":
                    # Caso speciale: endurance viene mappato su health
                    upgrade_key = "playerUpgradeHealth"
                else:
                    # Capitalizza solo la prima lettera per gli altri campi
                    upgrade_key = f"playerUpgrade{upgrade_type.capitalize()}"

                if upgrade_key not in data:
                    data[upgrade_key] = {}
                data[upgrade_key][player_id] = value
            
            # Aggiorna il riferimento a json_data
            self.json_data = json_data
            self.save_data = json_data
            
            if DEBUGLEVEL:
                logger.info(f"Aggiornato {field} per il giocatore {player_id} a {value}")
                
            return True
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'aggiornamento dei dati del giocatore: {e}")
            return False
    
    def update_game_stat(self, stat_name, value):
        """Aggiorna una statistica di gioco
        
        Args:
            stat_name: Nome della statistica
            value: Nuovo valore
            
        Returns:
            bool: True se l'aggiornamento è riuscito, False altrimenti
        """
        global json_data
        
        try:
            if not json_data or "dictionaryOfDictionaries" not in json_data:
                return False
                
            data = json_data["dictionaryOfDictionaries"]["value"]
            
            if "runStats" not in data:
                data["runStats"] = {}
                
            data["runStats"][stat_name] = value
            
            # Aggiorna il riferimento a json_data
            self.json_data = json_data
            self.save_data = json_data
            
            if DEBUGLEVEL:
                logger.info(f"Aggiornata statistica {stat_name} a {value}")
                
            return True
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'aggiornamento della statistica: {e}")
            return False
    
    def update_game_data(self, field, value):
        """Aggiorna i dati di gioco generali
        
        Args:
            field: Nome del campo da aggiornare
            value: Nuovo valore
            
        Returns:
            bool: True se l'aggiornamento è riuscito, False altrimenti
        """
        return self.update_game_stat(field, value)
    
    def get_game_data(self):
        """Alias di get_game_stats per compatibilità con il codice esistente
        
        Returns:
            dict: Statistiche di gioco
        """
        return self.get_game_stats()
    
    def update_team_name(self, name):
        """Aggiorna il nome del team
        
        Args:
            name: Nuovo nome del team
            
        Returns:
            bool: True se l'aggiornamento è riuscito, False altrimenti
        """
        global json_data
        
        try:
            if not json_data:
                return False
                
            json_data["teamName"] = {"value": name}
            
            # Aggiorna il riferimento a json_data
            self.json_data = json_data
            self.save_data = json_data
            
            if DEBUGLEVEL:
                logger.info(f"Aggiornato nome del team: {name}")
                
            return True
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'aggiornamento del nome del team: {e}")
            return False
    
    def get_game_stats(self):
        """Ottiene le statistiche di gioco
        
        Returns:
            dict: Dizionario contenente le statistiche di gioco
        """
        try:
            if not self.json_data or "dictionaryOfDictionaries" not in self.json_data:
                return {}
                
            data = self.json_data["dictionaryOfDictionaries"]["value"]
            
            if "runStats" not in data:
                return {}
                
            stats = data["runStats"]
            
            if DEBUGLEVEL:
                logger.info(f"Statistiche di gioco ottenute: {len(stats)} elementi")
                
            return stats
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'ottenere le statistiche di gioco: {e}")
            return {}
    
    def get_team_name(self):
        """Ottiene il nome del team
        
        Returns:
            str: Nome del team
        """
        try:
            if not self.json_data or "teamName" not in self.json_data:
                return ""
                
            return self.json_data["teamName"].get("value", "")
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'ottenere il nome del team: {e}")
            return ""
    
    def get_json_data(self):
        """Ottiene i dati JSON completi
        
        Returns:
            dict: Dati JSON completi
        """
        global json_data
        return json_data
    
    def update_json_data(self, new_data):
        """Aggiorna i dati JSON completi
        
        Args:
            new_data: Nuovi dati JSON
            
        Returns:
            bool: True se l'aggiornamento è riuscito, False altrimenti
        """
        global json_data
        
        try:
            json_data = new_data
            self.json_data = new_data
            self.save_data = new_data
            
            if DEBUGLEVEL:
                logger.info("Dati JSON aggiornati completamente")
                
            return True
            
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'aggiornamento dei dati JSON: {e}")
            return False
    
    def extract_player_upgrades(self, player_id):
        """Estrae tutti gli upgrade di un giocatore dal salvataggio
        
        Args:
            player_id: ID del giocatore
            
        Returns:
            dict: Dizionario con gli upgrade del giocatore
        """
        global json_data
        
        upgrades = {}
        
        if not json_data or "dictionaryOfDictionaries" not in json_data:
            return upgrades
            
        data = json_data["dictionaryOfDictionaries"]["value"]
        
        # Mappa degli upgrade e relativi campi
        upgrade_mapping = {
            "strength": "playerUpgradeStrength",
            "agility": "playerUpgradeStamina",  # Stamina è mappata su agility nell'UI
            "intelligence": "playerUpgradeRange",  # Range è mappato su intelligence nell'UI
            "endurance": "playerUpgradeHealth",  # Health è mappato su endurance nell'UI
            "extra_jump": "playerUpgradeExtraJump",
            "launch": "playerUpgradeLaunch",
            "map_count": "playerUpgradeMapPlayerCount",
            "speed": "playerUpgradeSpeed",
            "range": "playerUpgradeRange",
            "throw": "playerUpgradeThrow"
        }
        
        # Estrai tutti gli upgrade disponibili
        for ui_field, data_field in upgrade_mapping.items():
            if data_field in data and player_id in data[data_field]:
                upgrades[ui_field] = data[data_field][player_id]
            else:
                upgrades[ui_field] = 0
        
        return upgrades
    
    def save_player_changes(self, player_id, data):
        """Salva le modifiche ai dati del giocatore
        
        Args:
            player_id: ID del giocatore
            data: Dizionario con i dati da aggiornare (health, upgrades, ecc.)
            
        Returns:
            bool: True se le modifiche sono state salvate con successo
        """
        global json_data
        
        try:
            if not json_data or "dictionaryOfDictionaries" not in json_data:
                if DEBUGLEVEL:
                    logger.error("Nessun dato JSON valido disponibile")
                return False
            
            # Aggiorna la salute del giocatore
            if 'health' in data:
                self.update_player_data(player_id, "health", data['health'])
            
            # Aggiorna gli upgrade del giocatore
            if 'upgrades' in data:
                for upgrade_key, value in data['upgrades'].items():
                    self.update_player_data(player_id, f"upgrade_{upgrade_key}", value)
            
            # Aggiorna i dati di gioco generali
            if 'game_data' in data:
                for stat_key, value in data['game_data'].items():
                    self.update_game_data(stat_key, value)
            
            # Aggiorna il nome del team
            if 'team_name' in data:
                self.update_team_name(data['team_name'])
                
            if DEBUGLEVEL:
                logger.info(f"Dati del giocatore {player_id} aggiornati con successo")
                
            return True
        except Exception as e:
            if DEBUGLEVEL:
                logger.error(f"Errore nell'aggiornamento dei dati del giocatore: {e}")
            return False


