import json
from typing import Dict, Any, Optional

class GameData:
    def __init__(self, json_data: Dict[str, Any]):
        self.json_data = json_data
        self._validate_data()

    def _validate_data(self):
        """Valida la struttura dei dati del gioco"""
        if 'dictionaryOfDictionaries' not in self.json_data:
            raise ValueError("Invalid save file: missing dictionaryOfDictionaries")
        
        if 'value' not in self.json_data['dictionaryOfDictionaries']:
            raise ValueError("Invalid save file: missing value in dictionaryOfDictionaries")
        
        if 'runStats' not in self.json_data['dictionaryOfDictionaries']['value']:
            raise ValueError("Invalid save file: missing runStats")

    @property
    def world_data(self) -> Dict[str, Any]:
        """Restituisce i dati del mondo"""
        return self.json_data['dictionaryOfDictionaries']['value']['runStats']

    @property
    def player_data(self) -> Dict[str, Any]:
        """Restituisce i dati dei giocatori"""
        return self.json_data['dictionaryOfDictionaries']['value'].get('playerHealth', {})

    @property
    def game_settings(self) -> Dict[str, Any]:
        """Restituisce le impostazioni del gioco"""
        return self.json_data['dictionaryOfDictionaries']['value'].get('gameSettings', {})

    def update_world_data(self, data: Dict[str, Any]):
        """Aggiorna i dati del mondo"""
        self.world_data.update(data)

    def update_player_data(self, player_id: str, health: int):
        """Aggiorna i dati di un giocatore"""
        if 'playerHealth' not in self.json_data['dictionaryOfDictionaries']['value']:
            self.json_data['dictionaryOfDictionaries']['value']['playerHealth'] = {}
        self.json_data['dictionaryOfDictionaries']['value']['playerHealth'][player_id] = health

    def update_game_settings(self, settings: Dict[str, Any]):
        """Aggiorna le impostazioni del gioco"""
        if 'gameSettings' not in self.json_data['dictionaryOfDictionaries']['value']:
            self.json_data['dictionaryOfDictionaries']['value']['gameSettings'] = {}
        self.json_data['dictionaryOfDictionaries']['value']['gameSettings'].update(settings)

    def get_player_name(self, player_id: str) -> Optional[str]:
        """Restituisce il nome di un giocatore dato il suo ID"""
        player_names = self.json_data.get('playerNames', {}).get('value', {})
        return player_names.get(player_id)

    def get_player_id(self, player_name: str) -> Optional[str]:
        """Restituisce l'ID di un giocatore dato il suo nome"""
        player_names = self.json_data.get('playerNames', {}).get('value', {})
        return next((k for k, v in player_names.items() if v == player_name), None)

    def to_json(self) -> str:
        """Converte i dati in formato JSON"""
        return json.dumps(self.json_data, indent=4) 