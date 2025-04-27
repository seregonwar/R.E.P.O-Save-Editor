from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QFrame, QTabWidget, QComboBox,
                            QSpinBox, QCheckBox, QGroupBox, QProgressBar)
from .modern_widgets import ModernLineEdit, ModernLabel

# Definizione degli stili
WIDGET_STYLES = {
    "QGroupBox": """
        QGroupBox {
            font-weight: bold;
            border: 1px solid #2c3e50;
            border-radius: 5px;
            margin-top: 15px;
            padding-top: 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
        }
    """,
    "QScrollArea": """
        QScrollArea {
            border: none;
            background-color: transparent;
        }
    """,
    "QComboBox": """
        QComboBox {
            border: 1px solid #2c3e50;
            border-radius: 3px;
            padding: 3px;
            min-width: 6em;
            background-color: #34495e;
            color: white;
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 15px;
            border-left-width: 1px;
            border-left-color: #2c3e50;
            border-left-style: solid;
        }
    """,
    "QSpinBox": """
        QSpinBox {
            border: 1px solid #2c3e50;
            border-radius: 3px;
            padding: 3px;
            background-color: #34495e;
            color: white;
        }
    """,
    "QCheckBox": """
        QCheckBox {
            color: white;
        }
        QCheckBox::indicator {
            width: 15px;
            height: 15px;
        }
    """
}

TEXT_COLOR = "#ecf0f1"  # Colore bianco per il testo

class WorldTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Progress bar per il livello
        level_group = QGroupBox("Progresso")
        level_group.setStyleSheet(WIDGET_STYLES["QGroupBox"])
        level_layout = QVBoxLayout(level_group)
        
        self.level_progress = QProgressBar()
        self.level_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                text-align: center;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        level_layout.addWidget(self.level_progress)
        self.layout.addWidget(level_group)
        
        # Statistiche del mondo
        stats_group = QGroupBox("Statistiche")
        stats_group.setStyleSheet(WIDGET_STYLES["QGroupBox"])
        stats_layout = QVBoxLayout(stats_group)
        
        self.fields = {}
        for label, placeholder in [
            ("Level", "Enter level"),
            ("Currency", "Enter currency amount"),
            ("Lives", "Enter number of lives"),
            ("Charging Station", "Enter charging station level"),
            ("Total Haul", "Enter total haul"),
            ("Team Name", "Enter team name")
        ]:
            container = QFrame()
            container.setStyleSheet("background-color: transparent;")
            h_layout = QHBoxLayout(container)
            h_layout.setContentsMargins(0, 0, 0, 0)
            
            label_widget = ModernLabel(label + ":")
            label_widget.setFixedWidth(150)
            
            input_field = ModernLineEdit(placeholder)
            self.fields[label.lower().replace(" ", "_")] = input_field
            
            h_layout.addWidget(label_widget)
            h_layout.addWidget(input_field)
            stats_layout.addWidget(container)
        
        self.layout.addWidget(stats_group)
        self.layout.addStretch()

class PlayerTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Statistiche dei giocatori
        players_group = QGroupBox("Statistiche Giocatori")
        players_group.setStyleSheet(WIDGET_STYLES["QGroupBox"])
        players_layout = QVBoxLayout(players_group)
        
        scroll = QScrollArea()
        scroll.setStyleSheet(WIDGET_STYLES["QScrollArea"])
        scroll.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.scroll_content)
        players_layout.addWidget(scroll)
        
        self.layout.addWidget(players_group)
        
        self.player_entries = {}

    def add_player_entry(self, player_name, health):
        container = QFrame()
        container.setStyleSheet("background-color: transparent;")
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        label = ModernLabel(f"{player_name}:")
        label.setFixedWidth(150)
        
        # Barra della salute
        health_bar = QProgressBar()
        health_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #2c3e50;
                border-radius: 5px;
                text-align: center;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 3px;
            }
        """)
        health_bar.setValue(health)
        health_bar.setMaximum(100)
        
        input_field = ModernLineEdit("Enter health")
        input_field.setText(str(health))
        input_field.textChanged.connect(lambda: self._update_health_bar(health_bar, input_field))
        
        h_layout.addWidget(label)
        h_layout.addWidget(health_bar)
        h_layout.addWidget(input_field)
        self.scroll_layout.addWidget(container)
        
        self.player_entries[player_name] = input_field
        return input_field

    def _update_health_bar(self, health_bar, input_field):
        try:
            health = int(input_field.text() or 0)
            health_bar.setValue(health)
        except ValueError:
            health_bar.setValue(0)

    def clear_entries(self):
        for i in reversed(range(self.scroll_layout.count())):
            self.scroll_layout.itemAt(i).widget().setParent(None)
        self.player_entries.clear()

class AdvancedTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Game Settings Group
        game_settings = QGroupBox("Impostazioni di Gioco")
        game_settings.setStyleSheet(WIDGET_STYLES["QGroupBox"])
        game_layout = QVBoxLayout(game_settings)
        
        # Difficulty
        diff_container = QFrame()
        diff_container.setStyleSheet("background-color: transparent;")
        diff_layout = QHBoxLayout(diff_container)
        diff_layout.setContentsMargins(0, 0, 0, 0)
        
        diff_label = ModernLabel("Difficoltà:")
        diff_label.setFixedWidth(150)
        
        self.difficulty = QComboBox()
        self.difficulty.addItems(["Facile", "Normale", "Difficile", "Esperto"])
        self.difficulty.setStyleSheet(WIDGET_STYLES["QComboBox"])
        
        diff_layout.addWidget(diff_label)
        diff_layout.addWidget(self.difficulty)
        game_layout.addWidget(diff_container)
        
        # Game Speed
        speed_container = QFrame()
        speed_container.setStyleSheet("background-color: transparent;")
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        
        speed_label = ModernLabel("Velocità di Gioco:")
        speed_label.setFixedWidth(150)
        
        self.game_speed = QSpinBox()
        self.game_speed.setRange(1, 10)
        self.game_speed.setStyleSheet(WIDGET_STYLES["QSpinBox"])
        
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.game_speed)
        game_layout.addWidget(speed_container)
        
        # Cheats Group
        cheats = QGroupBox("Cheat")
        cheats.setStyleSheet(WIDGET_STYLES["QGroupBox"])
        cheats_layout = QVBoxLayout(cheats)
        
        # God Mode
        self.god_mode = QCheckBox("God Mode")
        self.god_mode.setStyleSheet(WIDGET_STYLES["QCheckBox"])
        cheats_layout.addWidget(self.god_mode)
        
        # Infinite Money
        self.infinite_money = QCheckBox("Soldi Infiniti")
        self.infinite_money.setStyleSheet(WIDGET_STYLES["QCheckBox"])
        cheats_layout.addWidget(self.infinite_money)
        
        # Unlock All
        self.unlock_all = QCheckBox("Sblocca Tutto")
        self.unlock_all.setStyleSheet(WIDGET_STYLES["QCheckBox"])
        cheats_layout.addWidget(self.unlock_all)
        
        # Max Stats
        self.max_stats = QCheckBox("Statistiche al Massimo")
        self.max_stats.setStyleSheet(WIDGET_STYLES["QCheckBox"])
        cheats_layout.addWidget(self.max_stats)
        
        # Add groups to layout
        self.layout.addWidget(game_settings)
        self.layout.addWidget(cheats)
        self.layout.addStretch() 