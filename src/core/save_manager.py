import json
import requests
from pathlib import Path
from datetime import datetime
from xml.etree import ElementTree
from typing import Dict, List, Optional, Tuple
from .decrypt import decrypt_es3
from .encrypt import encrypt_es3
from .logger import logger

class SaveManager:

        
    

    def open_file(self, file_path: str) -> Tuple[bool, str]:
        logger.info(f"Avvio caricamento file: {file_path}")
        """Apre e decodifica un file di salvataggio."""
        try:
            decrypted_data = decrypt_es3(
                file_path,
                "Why would you want to cheat?... :o It's no fun. :') :'D"
            )
            self.json_data = json.loads(decrypted_data)
            logger.info(f"File caricato e decifrato correttamente: {file_path}")
            return True, "File aperto con successo"
        except Exception as e:
            logger.error(f"Errore nell'apertura del file {file_path}: {str(e)}")
            return False, f"Errore nell'apertura del file: {str(e)}"

    def save_file(self, file_path: str) -> Tuple[bool, str]:
        logger.info(f"Avvio salvataggio file: {file_path}")
        """Salva e codifica i dati nel file di salvataggio."""
        if not self.json_data:
            logger.error("Nessun dato da salvare.")
            return False, "Nessun dato da salvare"
            
        try:
            encrypted_data = encrypt_es3(
                json.dumps(self.json_data, indent=4).encode('utf-8'),
                "Why would you want to cheat?... :o It's no fun. :') :'D"
            )
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            logger.info(f"File salvato correttamente: {file_path}")
            return True, "File salvato con successo"
        except Exception as e:
            logger.error(f"Errore nel salvataggio del file {file_path}: {str(e)}")
            return False, f"Errore nel salvataggio del file: {str(e)}"

   
    def get_player_data(self) -> List[Dict]:
        """Ottiene i dati dei giocatori dal salvataggio."""
        players = []
        if not self.json_data:
            return players
            
        for player_id, player_name in self.json_data["playerNames"]["value"].items():
            player_health = self.json_data["dictionaryOfDictionaries"]["value"]["playerHealth"][player_id]
            players.append({
                "id": player_id,
                "name": player_name,
                "health": player_health,
                "upgrades": {
                    "health": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeHealth"][player_id],
                    "stamina": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStamina"][player_id],
                    "extra_jump": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeExtraJump"][player_id],
                    "launch": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeLaunch"][player_id],
                    "map_player_count": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeMapPlayerCount"][player_id],
                    "speed": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeSpeed"][player_id],
                    "strength": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStrength"][player_id],
                    "range": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeRange"][player_id],
                    "throw": self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeThrow"][player_id]
                }
            })
        return players

    def get_world_data(self) -> Dict:
        """Ottiene i dati del mondo dal salvataggio."""
        if not self.json_data:
            return {}
            
        return {
            "level": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["level"],
            "currency": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["currency"],
            "lives": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["lives"],
            "charging_station": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["chargingStationCharge"],
            "total_haul": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["totalHaul"],
            "team_name": self.json_data["teamName"]["value"]
        }

    def update_player_data(self, player_id: str, health: int, upgrades: Dict) -> None:
        """Aggiorna i dati di un giocatore."""
        if not self.json_data:
            return
            
        self.json_data["dictionaryOfDictionaries"]["value"]["playerHealth"][player_id] = health
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeHealth"][player_id] = upgrades["health"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStamina"][player_id] = upgrades["stamina"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeExtraJump"][player_id] = upgrades["extra_jump"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeLaunch"][player_id] = upgrades["launch"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeMapPlayerCount"][player_id] = upgrades["map_player_count"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeSpeed"][player_id] = upgrades["speed"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeStrength"][player_id] = upgrades["strength"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeRange"][player_id] = upgrades["range"]
        self.json_data["dictionaryOfDictionaries"]["value"]["playerUpgradeThrow"][player_id] = upgrades["throw"]

    def update_world_data(self, data: Dict) -> None:
        """Aggiorna i dati del mondo."""
        if not self.json_data:
            return
            
        self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["level"] = data["level"]
        self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["currency"] = data["currency"]
        self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["lives"] = data["lives"]
        self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["chargingStationCharge"] = data["charging_station"]
        self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["totalHaul"] = data["total_haul"]
        self.json_data["teamName"]["value"] = data["team_name"]

    def get_raw_json(self) -> str:
        """Ottiene il JSON grezzo del salvataggio."""
        return json.dumps(self.json_data, indent=4) if self.json_data else ""

    def update_from_raw_json(self, json_str: str) -> Tuple[bool, str]:
        """Aggiorna i dati dal JSON grezzo."""
        try:
            self.json_data = json.loads(json_str)
            return True, "JSON aggiornato con successo"
        except json.JSONDecodeError as e:
            return False, f"Errore nel parsing del JSON: {str(e)}"
            
    def is_file_loaded(self) -> bool:
        """Verifica se un file è stato caricato."""
        return bool(self.json_data)
        
    def get_file_info(self) -> Dict:
        """Ottiene informazioni sul file caricato."""
        if not self.json_data:
            return {}
            
        return {
            "team_name": self.json_data["teamName"]["value"],
            "player_count": len(self.json_data["playerNames"]["value"]),
            "level": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["level"],
            "currency": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["currency"],
            "lives": self.json_data["dictionaryOfDictionaries"]["value"]["runStats"]["lives"]
        }
        
    def validate_player_data(self, player_id: str, health: int, upgrades: Dict) -> Tuple[bool, str]:
        """Valida i dati di un giocatore prima dell'aggiornamento."""
        if not self.json_data:
            return False, "Nessun file caricato"
            
        if player_id not in self.json_data["playerNames"]["value"]:
            return False, f"ID giocatore non valido: {player_id}"
            
        if not isinstance(health, int) or health < 0 or health > 200:
            return False, "La salute deve essere un numero intero tra 0 e 200"
            
        for key, value in upgrades.items():
            if not isinstance(value, int) or value < 0:
                return False, f"L'upgrade {key} deve essere un numero intero non negativo"
                
        return True, "Dati validi"
        
    def validate_world_data(self, data: Dict) -> Tuple[bool, str]:
        """Valida i dati del mondo prima dell'aggiornamento."""
        if not self.json_data:
            return False, "Nessun file caricato"
            
        required_fields = ["level", "currency", "lives", "charging_station", "total_haul", "team_name"]
        for field in required_fields:
            if field not in data:
                return False, f"Campo mancante: {field}"
                
        if not isinstance(data["level"], int) or data["level"] < 1:
            return False, "Il livello deve essere un numero intero positivo"
            
        if not isinstance(data["currency"], int) or data["currency"] < 0:
            return False, "La valuta deve essere un numero intero non negativo"
            
        if not isinstance(data["lives"], int) or data["lives"] < 0:
            return False, "Le vite devono essere un numero intero non negativo"
            
        if not isinstance(data["charging_station"], int) or data["charging_station"] < 0:
            return False, "La carica della stazione deve essere un numero intero non negativo"
            
        if not isinstance(data["total_haul"], int) or data["total_haul"] < 0:
            return False, "Il totale del carico deve essere un numero intero non negativo"
            
        if not isinstance(data["team_name"], str) or not data["team_name"]:
            return False, "Il nome della squadra non può essere vuoto"
            
        return True, "Dati validi" 