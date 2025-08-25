"""
Script de test pour les fonctionnalités de gestion de compte et de sauvegarde
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_account_management():
    """Test des fonctionnalités de gestion de compte"""
    print("🧪 Test de gestion des comptes...")
    
    # Test d'inscription
    print("📝 Test d'inscription...")
    register_data = {
        "username": f"testuser_{datetime.now().strftime('%H%M%S')}",
        "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
        "password": "testpassword123"
    }
    
    response = requests.post(f"{BASE_URL}/api/register", json=register_data)
    print(f"Inscription: {response.status_code} - {response.json()}")
    
    if response.status_code == 200 and response.json().get('success'):
        print("✅ Inscription réussie")
        username = register_data["username"]
        password = register_data["password"]
        
        # Test de déconnexion
        print("🚪 Test de déconnexion...")
        response = requests.post(f"{BASE_URL}/api/logout")
        print(f"Déconnexion: {response.status_code} - {response.json()}")
        
        # Test de connexion
        print("🔐 Test de connexion...")
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(f"{BASE_URL}/api/login", json=login_data)
        print(f"Connexion: {response.status_code} - {response.json()}")
        
        if response.status_code == 200 and response.json().get('success'):
            print("✅ Connexion réussie")
            
            # Test de profil
            print("👤 Test de récupération du profil...")
            response = requests.get(f"{BASE_URL}/api/profile")
            print(f"Profil: {response.status_code} - {response.json()}")
            
            return True
        else:
            print("❌ Échec de connexion")
            return False
    else:
        print("❌ Échec d'inscription")
        return False

def test_game_management():
    """Test des fonctionnalités de sauvegarde"""
    print("\n🎮 Test de gestion des parties...")
    
    # Créer une nouvelle partie
    print("🆕 Création d'une nouvelle partie...")
    response = requests.post(f"{BASE_URL}/api/start_game")
    game_data = response.json()
    print(f"Nouvelle partie: {response.status_code} - {game_data}")
    
    if response.status_code == 200 and game_data.get('success'):
        session_id = game_data['session_id']
        print(f"✅ Partie créée avec session: {session_id}")
        
        # Test de sauvegarde
        print("💾 Test de sauvegarde...")
        save_data = {
            "game_name": f"Test partie {datetime.now().strftime('%H:%M:%S')}"
        }
        response = requests.post(f"{BASE_URL}/api/save_game", json=save_data)
        save_result = response.json()
        print(f"Sauvegarde: {response.status_code} - {save_result}")
        
        if response.status_code == 200 and save_result.get('success'):
            save_id = save_result['save_id']
            print(f"✅ Partie sauvegardée avec ID: {save_id}")
            
            # Test de liste des sauvegardes
            print("📋 Test de liste des sauvegardes...")
            response = requests.get(f"{BASE_URL}/api/saves")
            print(f"Liste sauvegardes: {response.status_code} - {len(response.json().get('saves', []))} sauvegardes")
            
            # Test de chargement
            print("📂 Test de chargement de sauvegarde...")
            response = requests.get(f"{BASE_URL}/api/load_game/{save_id}")
            print(f"Chargement: {response.status_code} - {response.json()}")
            
            # Test de suppression
            print("🗑️ Test de suppression de sauvegarde...")
            response = requests.delete(f"{BASE_URL}/api/delete_save/{save_id}")
            print(f"Suppression: {response.status_code} - {response.json()}")
            
            return True
        else:
            print("❌ Échec de sauvegarde")
            return False
    else:
        print("❌ Échec de création de partie")
        return False

def test_statistics():
    """Test des fonctionnalités de statistiques"""
    print("\n📊 Test des statistiques...")
    
    # Test de récupération des stats
    response = requests.get(f"{BASE_URL}/api/stats")
    stats_data = response.json()
    print(f"Statistiques: {response.status_code} - {stats_data}")
    
    # Test de sauvegarde de stats de partie
    print("💾 Test de sauvegarde de statistiques...")
    stats = {
        "tour_final": 10,
        "elixir_total_gagne": 50,
        "cartes_achetees": 15,
        "fusions_effectuees": 5,
        "cartes_vendues": 2,
        "bonus_familles_utilises": ["Noble", "Clan"],
        "leader_utilise": "Leader de test",
        "modificateur_utilise": "Test modificateur",
        "victoire": True,
        "troupes_adverses_restantes": 0,
        "duree_partie_minutes": 15.5
    }
    
    response = requests.post(f"{BASE_URL}/api/save_game_stats", json=stats)
    print(f"Sauvegarde stats: {response.status_code} - {response.json()}")
    
    if response.status_code == 200:
        # Recharger les stats pour voir les changements
        response = requests.get(f"{BASE_URL}/api/stats")
        new_stats = response.json()
        print(f"Nouvelles statistiques: {new_stats}")
        return True
    else:
        print("❌ Échec de sauvegarde des statistiques")
        return False

def test_apis():
    """Test des APIs de base"""
    print("\n🔧 Test des APIs de base...")
    
    # Test bibliothèque de cartes
    response = requests.get(f"{BASE_URL}/api/cards")
    print(f"Cartes: {response.status_code} - {len(response.json().get('cards', {}))} cartes")
    
    # Test modificateurs
    response = requests.get(f"{BASE_URL}/api/modificateurs")
    print(f"Modificateurs: {response.status_code} - {len(response.json().get('modificateurs', {}))} modificateurs")
    
    # Test leaders
    response = requests.get(f"{BASE_URL}/api/leaders")
    print(f"Leaders: {response.status_code} - {len(response.json().get('leaders', {}))} leaders")
    
    print("✅ APIs de base testées")

if __name__ == "__main__":
    print("🚀 Lancement des tests de l'application Clash Royale Merge Tactics Assistant")
    print("="*70)
    
    try:
        # Test des APIs de base d'abord
        test_apis()
        
        # Test de gestion des comptes
        if test_account_management():
            # Test de gestion des parties (nécessite une connexion)
            test_game_management()
            
            # Test des statistiques (nécessite une connexion)
            test_statistics()
        
        print("\n" + "="*70)
        print("✅ Tests terminés ! Vérifiez les résultats ci-dessus.")
        print("🌐 L'application devrait être accessible sur http://localhost:5000")
        
    except requests.exceptions.ConnectionError:
        print("❌ Erreur : Impossible de se connecter au serveur")
        print("💡 Assurez-vous que le serveur Flask est démarré avec : python app.py")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")
