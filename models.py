"""
Modèles de données pour la gestion des comptes et historique des parties
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import uuid

@dataclass
class PlayerAccount:
    """Modèle représentant un compte joueur"""
    username: str
    email: str
    password_hash: str
    created_at: str
    total_games: int = 0
    total_wins: int = 0
    total_losses: int = 0
    best_tour: int = 0
    favorite_leader: str = ""
    favorite_modificateur: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)

@dataclass
class GameStats:
    """Statistiques détaillées d'une partie"""
    tour_final: int
    elixir_total_gagne: int
    cartes_achetees: int
    fusions_effectuees: int
    cartes_vendues: int
    bonus_familles_utilises: List[str]
    leader_utilise: str
    modificateur_utilise: str
    victoire: bool
    troupes_adverses_restantes: int = 0
    duree_partie_minutes: float = 0.0

@dataclass
class SavedGame:
    """Modèle représentant une partie sauvegardée"""
    save_id: str
    username: str
    game_state: Dict
    created_at: str
    last_modified: str
    game_name: str
    tour: int
    elixir: int
    hp: int
    is_completed: bool = False
    stats: Optional[GameStats] = None
    
    def to_dict(self):
        data = asdict(self)
        if self.stats:
            data['stats'] = asdict(self.stats)
        return data
    
    @classmethod
    def from_dict(cls, data):
        stats = None
        if data.get('stats'):
            stats = GameStats(**data['stats'])
        
        return cls(
            save_id=data['save_id'],
            username=data['username'],
            game_state=data['game_state'],
            created_at=data['created_at'],
            last_modified=data['last_modified'],
            game_name=data['game_name'],
            tour=data['tour'],
            elixir=data['elixir'],
            hp=data['hp'],
            is_completed=data.get('is_completed', False),
            stats=stats
        )

class DatabaseManager:
    """Gestionnaire de base de données JSON simple"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.ensure_data_directory()
        
        # Fichiers de données
        self.accounts_file = os.path.join(data_dir, "accounts.json")
        self.games_file = os.path.join(data_dir, "saved_games.json")
        self.stats_file = os.path.join(data_dir, "game_stats.json")
        
        # Initialiser les fichiers s'ils n'existent pas
        self.initialize_files()
    
    def ensure_data_directory(self):
        """Créer le dossier data s'il n'existe pas"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def initialize_files(self):
        """Initialiser les fichiers JSON s'ils n'existent pas"""
        files = [self.accounts_file, self.games_file, self.stats_file]
        for file_path in files:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump({}, f)
    
    def load_json(self, file_path):
        """Charger un fichier JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_json(self, file_path, data):
        """Sauvegarder des données en JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # === GESTION DES COMPTES ===
    
    def create_account(self, username: str, email: str, password: str) -> bool:
        """Créer un nouveau compte"""
        accounts = self.load_json(self.accounts_file)
        
        # Vérifier si le nom d'utilisateur existe déjà
        if username in accounts:
            return False
        
        # Vérifier si l'email existe déjà
        for acc_data in accounts.values():
            if acc_data.get('email') == email:
                return False
        
        # Hasher le mot de passe
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Créer le compte
        account = PlayerAccount(
            username=username,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now().isoformat()
        )
        
        accounts[username] = account.to_dict()
        self.save_json(self.accounts_file, accounts)
        return True
    
    def authenticate(self, username: str, password: str) -> bool:
        """Authentifier un utilisateur"""
        accounts = self.load_json(self.accounts_file)
        
        if username not in accounts:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return accounts[username]['password_hash'] == password_hash
    
    def get_account(self, username: str) -> Optional[PlayerAccount]:
        """Récupérer un compte"""
        accounts = self.load_json(self.accounts_file)
        
        if username not in accounts:
            return None
        
        return PlayerAccount.from_dict(accounts[username])
    
    def update_account_stats(self, username: str, stats: GameStats):
        """Mettre à jour les statistiques d'un compte"""
        accounts = self.load_json(self.accounts_file)
        
        if username not in accounts:
            return False
        
        account_data = accounts[username]
        account_data['total_games'] += 1
        
        if stats.victoire:
            account_data['total_wins'] += 1
        else:
            account_data['total_losses'] += 1
        
        account_data['best_tour'] = max(account_data.get('best_tour', 0), stats.tour_final)
        account_data['favorite_leader'] = stats.leader_utilise
        account_data['favorite_modificateur'] = stats.modificateur_utilise
        
        accounts[username] = account_data
        self.save_json(self.accounts_file, accounts)
        return True
    
    # === GESTION DES SAUVEGARDES ===
    
    def save_game(self, username: str, game_session, game_name: str = None) -> str:
        """Sauvegarder une partie"""
        games = self.load_json(self.games_file)
        
        save_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        if not game_name:
            game_name = f"Partie du {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        
        # Sérialiser l'état du jeu
        game_state = {
            'tour': game_session.tour,
            'elixir': game_session.etat.elixir,
            'hp': game_session.etat.hp,
            'main': [{'nom': c.nom, 'niveau': c.niveau, 'traits': c.traits, 'cout': c.cout} for c in game_session.etat.main],
            'bench': [{'nom': c.nom, 'niveau': c.niveau, 'traits': c.traits, 'cout': c.cout} for c in game_session.etat.bench],
            'modificateurs_actifs': game_session.modificateurs_actifs,
            'leader_choisi': game_session.leader_choisi,
            'bonus_familles_actifs': game_session.bonus_familles_actifs
        }
        
        saved_game = SavedGame(
            save_id=save_id,
            username=username,
            game_state=game_state,
            created_at=current_time,
            last_modified=current_time,
            game_name=game_name,
            tour=game_session.tour,
            elixir=game_session.etat.elixir,
            hp=game_session.etat.hp
        )
        
        games[save_id] = saved_game.to_dict()
        self.save_json(self.games_file, games)
        
        return save_id
    
    def load_game(self, save_id: str) -> Optional[SavedGame]:
        """Charger une partie sauvegardée"""
        games = self.load_json(self.games_file)
        
        if save_id not in games:
            return None
        
        return SavedGame.from_dict(games[save_id])
    
    def get_user_saves(self, username: str) -> List[SavedGame]:
        """Récupérer toutes les sauvegardes d'un utilisateur"""
        games = self.load_json(self.games_file)
        user_saves = []
        
        for save_data in games.values():
            if save_data['username'] == username:
                user_saves.append(SavedGame.from_dict(save_data))
        
        # Trier par date de modification (plus récent en premier)
        user_saves.sort(key=lambda x: x.last_modified, reverse=True)
        return user_saves
    
    def delete_save(self, save_id: str, username: str) -> bool:
        """Supprimer une sauvegarde (seulement si elle appartient à l'utilisateur)"""
        games = self.load_json(self.games_file)
        
        if save_id not in games:
            return False
        
        if games[save_id]['username'] != username:
            return False
        
        del games[save_id]
        self.save_json(self.games_file, games)
        return True
    
    def update_save(self, save_id: str, game_session, username: str) -> bool:
        """Mettre à jour une sauvegarde existante"""
        games = self.load_json(self.games_file)
        
        if save_id not in games:
            return False
        
        if games[save_id]['username'] != username:
            return False
        
        # Mettre à jour l'état du jeu
        game_state = {
            'tour': game_session.tour,
            'elixir': game_session.etat.elixir,
            'hp': game_session.etat.hp,
            'main': [{'nom': c.nom, 'niveau': c.niveau, 'traits': c.traits, 'cout': c.cout} for c in game_session.etat.main],
            'bench': [{'nom': c.nom, 'niveau': c.niveau, 'traits': c.traits, 'cout': c.cout} for c in game_session.etat.bench],
            'modificateurs_actifs': game_session.modificateurs_actifs,
            'leader_choisi': game_session.leader_choisi,
            'bonus_familles_actifs': game_session.bonus_familles_actifs
        }
        
        games[save_id]['game_state'] = game_state
        games[save_id]['last_modified'] = datetime.now().isoformat()
        games[save_id]['tour'] = game_session.tour
        games[save_id]['elixir'] = game_session.etat.elixir
        games[save_id]['hp'] = game_session.etat.hp
        
        self.save_json(self.games_file, games)
        return True
    
    # === GESTION DES STATISTIQUES ===
    
    def save_game_stats(self, username: str, stats: GameStats):
        """Sauvegarder les statistiques d'une partie"""
        all_stats = self.load_json(self.stats_file)
        
        if username not in all_stats:
            all_stats[username] = []
        
        stats_dict = asdict(stats)
        stats_dict['date'] = datetime.now().isoformat()
        
        all_stats[username].append(stats_dict)
        self.save_json(self.stats_file, all_stats)
        
        # Mettre à jour les stats du compte
        self.update_account_stats(username, stats)
    
    def get_user_stats(self, username: str) -> Dict:
        """Récupérer les statistiques d'un utilisateur"""
        all_stats = self.load_json(self.stats_file)
        user_stats = all_stats.get(username, [])
        
        if not user_stats:
            return {
                'total_games': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'average_tour': 0,
                'best_tour': 0,
                'total_elixir': 0,
                'total_fusions': 0,
                'favorite_leader': '',
                'favorite_modificateur': '',
                'recent_games': []
            }
        
        # Calculer les statistiques
        total_games = len(user_stats)
        wins = sum(1 for stat in user_stats if stat['victoire'])
        losses = total_games - wins
        win_rate = (wins / total_games * 100) if total_games > 0 else 0
        
        tours = [stat['tour_final'] for stat in user_stats]
        average_tour = sum(tours) / len(tours) if tours else 0
        best_tour = max(tours) if tours else 0
        
        total_elixir = sum(stat['elixir_total_gagne'] for stat in user_stats)
        total_fusions = sum(stat['fusions_effectuees'] for stat in user_stats)
        
        # Leaders et modificateurs les plus utilisés
        leaders = [stat['leader_utilise'] for stat in user_stats if stat['leader_utilise']]
        modificateurs = [stat['modificateur_utilise'] for stat in user_stats if stat['modificateur_utilise']]
        
        favorite_leader = max(set(leaders), key=leaders.count) if leaders else ''
        favorite_modificateur = max(set(modificateurs), key=modificateurs.count) if modificateurs else ''
        
        # Parties récentes (10 dernières)
        recent_games = sorted(user_stats, key=lambda x: x['date'], reverse=True)[:10]
        
        return {
            'total_games': total_games,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 1),
            'average_tour': round(average_tour, 1),
            'best_tour': best_tour,
            'total_elixir': total_elixir,
            'total_fusions': total_fusions,
            'favorite_leader': favorite_leader,
            'favorite_modificateur': favorite_modificateur,
            'recent_games': recent_games
        }

# Instance globale du gestionnaire de base de données
db = DatabaseManager()
