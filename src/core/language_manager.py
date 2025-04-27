"""
Modulo che responsabile della gestione delle traduzioni.
Questo file serve come ponte tra le vecchie implementazioni che importano language_manager
e il nuovo modulo language.py che contiene l'implementazione effettiva.
"""

from core.language import LanguageManager, tr, language_manager

# Definisco una funzione di debug
def debug_state():
    """Stampa informazioni di debug sullo stato del language_manager"""
    print("\n--- DEBUG LANGUAGE MANAGER ---")
    print(f"Current language: {language_manager.get_current_language()} - {language_manager.get_current_language_name()}")
    print(f"Available languages: {language_manager.get_available_languages()}")
    print(f"Number of observers registered: {len(language_manager.observers)}")
    print("---------------------------\n")

# Definisco una funzione di set_language avanzata
def set_language_with_debug(lang_code):
    """Imposta la lingua con debug aggiuntivo"""
    print(f"\nSetting language: {lang_code}")
    debug_state()
    result = language_manager.set_language(lang_code)
    print("\nLanguage set, new state:")
    debug_state()
    return result

# Reesposizione delle funzioni
get_translation = language_manager.get_translation
get_available_languages = language_manager.get_available_languages
get_language_info = language_manager.get_language_info
get_current_language = language_manager.get_current_language
get_current_language_name = language_manager.get_current_language_name
set_language = set_language_with_debug  # Usiamo la versione con debug
reload_languages = language_manager.reload_languages
load_languages = language_manager.load_languages
add_observer = language_manager.add_observer
remove_observer = language_manager.remove_observer

# Esporta tutti i simboli necessari per retrocompatibilità
__all__ = [
    'language_manager', 'tr', 'LanguageManager',
    'get_translation', 'get_available_languages', 'get_language_info',
    'get_current_language', 'get_current_language_name', 'set_language',
    'reload_languages', 'load_languages', 'add_observer', 'remove_observer',
    'debug_state'
] 