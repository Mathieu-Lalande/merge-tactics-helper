from dataclasses import dataclass
from typing import List, Dict, Optional
import json
import os

@dataclass
class Carte:
    nom: str
    cout: int
    traits: List[str]
    niveau: int  # étoiles : 1, 2, 3...
    
    def __str__(self):
        return f"{self.nom} (Coût: {self.cout}, Traits: {', '.join(self.traits)}, Niveau: {self.niveau})"

@dataclass
class EtatJeu:
    elixir: int
    main: List[Carte]
    bench: List[Carte]
    historique_pool: Dict[str, int]
    max_cartes_plateau: int = 2  # Limite de cartes sur le plateau
    hp: int = 10  # Points de vie (HP), on perd à 0

# Bibliothèque des cartes Merge Tactics
BIBLIOTHEQUE_CARTES = {
    # Coût 2 - Merge Tactics
    "Chevalier": Carte("Chevalier", 2, ["Noble", "Colosse"], 1),
    "Archères": Carte("Archères", 2, ["Clan", "Guetteur"], 1),
    "Gobelins": Carte("Gobelins", 2, ["Gobelin", "Assassin"], 1),
    "Gobelins à lances": Carte("Gobelins à lances", 2, ["Gobelin", "Lanceur"], 1),
    "Bombardier": Carte("Bombardier", 2, ["Revenant", "Lanceur"], 1),
    "Barbares": Carte("Barbares", 2, ["Clan", "Bagarreur"], 1),

    # Coût 3 - Merge Tactics
    "Valkyrie": Carte("Valkyrie", 3, ["Clan", "Vengeuse"], 1),
    "P.E.K.K.A": Carte("P.E.K.K.A", 3, ["Ace", "Colosse"], 1),
    "Prince": Carte("Prince", 3, ["Noble", "Bagarreur"], 1),
    "Squelette géant": Carte("Squelette géant", 3, ["Revenant", "Bagarreur"], 1),
    "Gobelin à sarbacane": Carte("Gobelin à sarbacane", 3, ["Gobelin", "Guetteur"], 1),
    "Bourreau": Carte("Bourreau", 3, ["Ace", "Lanceur"], 1),

    # Coût 4 - Merge Tactics
    "Princesse": Carte("Princesse", 4, ["Noble", "Guetteur"], 1),
    "Mega chevalier": Carte("Mega chevalier", 4, ["Ace", "Bagarreur"], 1),
    "Fantome royal": Carte("Fantome royal", 4, ["Revenant", "Assassin"], 1),
    "Voleuse": Carte("Voleuse", 4, ["Ace", "Vengeuse"], 1),
    "Machine gobeline": Carte("Machine gobeline", 4, ["Gobelin", "Colosse"], 1),

    # Coût 5 - Merge Tactics
    "Roi squelette": Carte("Roi squelette", 5, ["Revenant", "Colosse"], 1),
    "Chevalier d'or": Carte("Chevalier d'or", 5, ["Noble", "Assassin"], 1),
    "Reine": Carte("Reine", 5, ["Clan", "Vengeuse"], 1),
}

# Modificateurs de partie (27 modificateurs + 1 aléatoire)
MODIFICATEURS_PARTIE = {
    "plein_les_poches": "Tous les leaders commencent avec +5 élixir",
    "plus_on_est_de_fous": "Taille de l'équipe augmentée de 1 (jusqu'à 7 cartes)",
    "heritage": "Gagnez +5 élixirs à la mort d'un leader adverse",
    "la_fete": "La taille de l'equipe est toujours de 6",
    "etoile_rare": "Commencez avec une troupe 2 étoiles à 2 élixirs",
    "etoile_epique": "Commencez avec une troupe 2 étoiles à 3 élixirs",
    "etoile_légendaire": "Commencez avec une troupe 2 étoiles à 4 élixirs",
    "etoile_de_champion": "Commencez avec une troupe aléatoire à 5 élixirs",
    "de_plus_en_plus_riche": "Tous les 2 élixirs, vous gagnez +1 élixir d'interêt au prochain round",
    "fievre_du_fight": "Les troupes gagnent +100% de vitesse de frappe pendant 6s après avoir éliminé un ennemi",
    "moins_cest_mieux": "Si vous avez moins de troupes, votre équipe gagne +25% de PV et de vitesse de frappe",
    "aie": "Début: les troupes sur la première lignes d'hexas renvoient 40% des dégâts subis",
    "tu_es_a_moi": "Vous gagnez une copie 1 étoile de la première troupe ennemie éliminée",
    "extracteur_elixir": "Recevez un extracteur d'élixir qui génère 2 élixirs par round, stockés jusqu'à vente de l'extracteur",
    "cadeau_de_la_maison": "La première troupe achetée à chaque round est gratuite",
    "4_etoiles": "La sélection de troupes est doublée, plus de troupes sont disponibles dans le magasin",
    "miroir_magique": "Chaque round, gagnez une copie 1 étoile de la troupe la plus à droite de votre banc",
    "banc_de_pandore": "Chaque round, la troupe la plus à droite de votre banc est remplacée par une nouvelle troupe aléatoire du même coût",
    "rester_en_vie": "Commencez avec un mannequin et gagnez +1 élixir s'il survit au round",
    "mannequin_special": "Commencez avec un mannequin qui possède 2 attributs aléatoires",
    "cheaté": "Chaque round, gagnez une troupe utile pour votre équipe",
    "offre_a_saisir": "Chaque fois que le magasin est réinitialisé, une troupe au hasard coûte 1 élixir de moins",
    "clairvoyance": "Si votre banc est vide, gagnez +2 élixirs au prochain round",
    "promotion": "Chaque round, la troupe la plus à droite de votre banc se transforme en une troupe aléatoire qui vaut 1 élixir de plus",
    "bonne_affaire": "Pour chaque troupe que vous vendez, gagnez +1 élixir au prochain round",
    "ascension": "Au round 3, la troupe la plus à droite de votre banc devient une puissante troupe 3 étoiles",
    "premier_choix": "La première troupe achetée à chaque tour est une 2 étoiles",
    # + 1 modificateur aléatoire généré par le jeu
}

# Bonus des familles/traits (2 cartes = bonus 1, 4 cartes = bonus 2)
BONUS_FAMILLES = {
    "Noble": {
        2: "Les troupes au front subissent moins de dégâts et les troupes sur la ligne arrière gagnent des dégâts bonus [2]: 20%.",
        4: "40%."
    },
    "Clan": {
        2: "Soins rapides et bonus de vitesse de Frappe à 50 % des PV pour les Clans (une Fois par round) : [2] +30% de PV max et vitesse de frappe.",
        4: "+60% de PV max et vitesse de frappe pour les Clans, +30% pour l'équipe."
    },
    "Gobelin": {
        2: "gobelin bonus aléatoire gratuit au prochain round. [2]: Gobelin bonus de 2 élixirs",
        4: "+60% de chances de gagner un gobelin à 3 ou 4 élixirs"
    },
    "Revenant": {
        2: "Début : l'ennemi avec le plus de PV est maudit et vos Revenants gagnent 30 % de dégâts bonus quand cet ennemi est vaincu. [2]: Maudit 2 ennemis, PV Max réduits de 25%.",
        4: "Maudit 3 ennemis, PV Max réduits de 50%."
    },
    "Ace": {
        2: "Démarrage: l'unité avec la plus haute niveau de fusion devient capitaine. Quand il élimine des troupes, l'équipe gagne +20% de vitesse de frappes (4s) [2]: capitaine; +30% de dégâts bonus",
        4: "Capitaine: +60% de degats bonus et +30% de PV des dégats infligés"
    },
    "Colosse": {
        2: "Début: les Colosses et les troupes placées derrières gagnent un bouclier de 12s. [2]: +30% de bouclier bonus",
        4: "+60% de bouclier bonus pour les Colosses."
    },
    "Assassin": {
        3: "Démarrage: les assassins sautent les les troupes de la ligne arrière adverse. [3]: +35% de chances critiques et dégâts critiques",
    },
    "Guetteur": {
        3: "Les guetteurs gagnent de la vitesse de frappe à chaque attaque, jusqu'à 15x. [3]: +15% de vitesse de frappe.",
    },
    "Bagarreur": {
        2: "+40% de PV maximum",
        4: "+80% PV pour les Bagarreurs, +30% pour l'équipe entière",
    },
    "Vengeuse": {
        3: "Les Vengeuses gagnent des dégats bonus, et la dernière devbout gagne le double de dégats [3]: +30%"
    },
    "Lanceur": {
        3: "Les Lanceurs gagnent +1 de portée d'attaque et infligent plus de dégâts aux cibles éloignées. [3]: +10% de dégâts par hexagone.",
    }
}

# Suppression du mode normal - Merge Tactics seulement
class GameSession:
    def __init__(self):
        self.etat = EtatJeu(
            elixir=4,  # Base Merge Tactics
            main=[],
            bench=[],
            historique_pool={},
            max_cartes_plateau=2,  # Initialisation explicite
            hp=10  # Points de vie initiaux
        )
        self.weights = {
            "traits": 2.0,
            "merge": 2.0,
            "fusion_sell": 3.0,
            "disruption": 1.0,
            "cost": 1.0
        }
        self.tour = 1
        self.elixir_par_tour = 4
        self.cartes_initiales = 1
        self.choix_par_tour = 3
        self.modificateurs_actifs = []
        self.bonus_familles_actifs = {}
        
        # Système de leaders
        self.leader_choisi = None
        self.leaders_disponibles = {
            "Impératrice": {
                "nom": "Impératrice",
                "description": "Gagne +1 élixir à chaque fusion réussie",
                "bonus_merge": 1,
                "bonus_defeat": 0,
                "icone": "👑"
            },
            "Roi Royal": {
                "nom": "Roi Royal", 
                "description": "Gagne +4 élixir à chaque défaite",
                "bonus_merge": 0,
                "bonus_defeat": 4,
                "icone": "🤴"
            }
        }
        
        # Variables pour modificateurs spéciaux
        self.taille_equipe_max = 6
        self.taille_equipe_fixe = False
        self.modificateur_etoile_debut = None
        self.extracteur_actif = False
        self.extracteur_stock = 0
        self.premiere_carte_gratuite = False
        self.mannequin_actif = False
    
    def calculer_max_cartes_plateau(self):
        """Calcule la limite de cartes sur le plateau selon le tour et les modificateurs"""
        # Base : 2 au tour 1, puis +1 par tour (max 6)
        base_max = min(2 + (self.tour - 1), 6)
        
        # Modificateur "plus_on_est_de_fous" : +1 carte (max 7)
        if "plus_on_est_de_fous" in self.modificateurs_actifs:
            base_max = min(base_max + 1, 7)
        
        # Modificateur "la_fete" : toujours 6 cartes
        if "la_fete" in self.modificateurs_actifs:
            base_max = 6
        
        self.etat.max_cartes_plateau = base_max
        return base_max
    
    def gerer_resultat_bataille(self, victoire=True, troupes_adverses_restantes=0):
        """Gère le résultat d'une bataille (victoire ou défaite) et avance le tour"""
        elixir_gagne = 0
        hp_perdus = 0
        message = ""
        game_over = False
        
        if victoire:
            message = "🎉 Victoire ! Bien joué !"
            # Pas de bonus d'élixir pour les victoires actuellement
        else:
            # Calcul des dégâts : -1 HP (défaite) + nombre de troupes adverses restantes
            hp_perdus = 1 + troupes_adverses_restantes
            self.etat.hp -= hp_perdus
            
            message = f"💀 Défaite... -{hp_perdus} HP ({1} défaite + {troupes_adverses_restantes} troupes adverses)"
            
            # Vérifier si le joueur est éliminé
            if self.etat.hp <= 0:
                self.etat.hp = 0
                game_over = True
                message += " 💥 GAME OVER ! Vous êtes éliminé !"
            
            # Appliquer bonus du leader pour défaite
            if self.leader_choisi and self.leader_choisi['bonus_defeat'] > 0:
                elixir_leader = self.leader_choisi['bonus_defeat']
                elixir_gagne += elixir_leader
                self.etat.elixir += elixir_leader
                message += f" +{elixir_leader} élixir (Leader: {self.leader_choisi['nom']})"
        
        # Avancer le tour si le jeu n'est pas terminé
        if not game_over:
            self.tour += 1
            elixir_tour = self.elixir_par_tour
            elixir_gagne += elixir_tour
            self.etat.elixir += elixir_tour
            message += f" → Tour {self.tour} | +{elixir_tour} élixir"
        
        return {
            'elixir_gagne': elixir_gagne,
            'hp_perdus': hp_perdus,
            'message': message,
            'victoire': victoire,
            'game_over': game_over,
            'hp_restants': self.etat.hp,
            'tour': self.tour
        }
    
    def choisir_leader(self):
        """Permet de choisir un leader avec des bonus spéciaux"""
        print("\n=== CHOIX DU LEADER ===")
        print("Choisissez votre leader pour cette partie :")
        print()
        
        leaders_list = list(self.leaders_disponibles.items())
        for i, (key, leader) in enumerate(leaders_list):
            print(f"{i+1}. {leader['icone']} {leader['nom']}")
            print(f"   {leader['description']}")
            print()
        
        while True:
            try:
                choix = int(input("Votre choix (1-2): ")) - 1
                if 0 <= choix < len(leaders_list):
                    leader_key = leaders_list[choix][0]
                    self.leader_choisi = self.leaders_disponibles[leader_key]
                    print(f"\n✅ {self.leader_choisi['icone']} {self.leader_choisi['nom']} sélectionné !")
                    break
                else:
                    print("Choix invalide. Veuillez choisir 1 ou 2.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
    
    def appliquer_bonus_leader(self, type_bonus, details=""):
        """Applique les bonus du leader selon l'événement"""
        if not self.leader_choisi:
            return 0
        
        bonus_gagne = 0
        
        if type_bonus == "merge" and self.leader_choisi["bonus_merge"] > 0:
            bonus_gagne = self.leader_choisi["bonus_merge"]
            self.etat.elixir += bonus_gagne
            # print(f"🎉 {self.leader_choisi['icone']} {self.leader_choisi['nom']}: +{bonus_gagne} élixir pour la fusion ! {details}")
        
        elif type_bonus == "defeat" and self.leader_choisi["bonus_defeat"] > 0:
            bonus_gagne = self.leader_choisi["bonus_defeat"]
            self.etat.elixir += bonus_gagne
            # print(f"💪 {self.leader_choisi['icone']} {self.leader_choisi['nom']}: +{bonus_gagne} élixir pour la perte ! {details}")
        
        return bonus_gagne
    
    def configuration_modificateurs(self):
        print("\n=== CONFIGURATION DES MODIFICATEURS ===")
        print("Configurons les modificateurs actifs pour cette partie...")
        print("Vous avez normalement 27 modificateurs + 1 aléatoire par le jeu.")
        
        while True:
            try:
                nb_mods = int(input("Combien de modificateurs voulez-vous configurer? (0-28): "))
                if 0 <= nb_mods <= 28:
                    break
                else:
                    print("Veuillez entrer un nombre entre 0 et 28.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        if nb_mods > 0:
            print("\nModificateurs disponibles:")
            mods_list = list(MODIFICATEURS_PARTIE.items())
            for i, (key, desc) in enumerate(mods_list):
                print(f"{i+1}. {key}: {desc}")
            
            print(f"\nSélectionnez {nb_mods} modificateur(s) (tapez les numéros séparés par des espaces):")
            print("Ou tapez 'auto' pour sélection automatique des plus impactants:")
            
            choix = input("> ").strip()
            
            if choix.lower() == 'auto':
                # Sélection automatique des modificateurs les plus impactants
                mods_importants = ["elixir_bonus", "trait_boost", "double_merge", "fast_game", "cost_reduction"]
                self.modificateurs_actifs = mods_importants[:nb_mods]
            else:
                try:
                    indices = [int(x) - 1 for x in choix.split()]
                    self.modificateurs_actifs = [list(MODIFICATEURS_PARTIE.keys())[i] for i in indices if 0 <= i < len(MODIFICATEURS_PARTIE)]
                    self.modificateurs_actifs = self.modificateurs_actifs[:nb_mods]  # Limiter au nombre demandé
                except:
                    print("Erreur dans la sélection, aucun modificateur appliqué.")
                    self.modificateurs_actifs = []
        
        # Appliquer les modificateurs à l'état initial
        self.appliquer_modificateurs()
        
        if self.modificateurs_actifs:
            print(f"\n✅ Modificateurs actifs: {', '.join(self.modificateurs_actifs)}")
        else:
            print("\n🔸 Aucun modificateur actif.")
    
    def appliquer_modificateurs(self):
        """Applique les effets des modificateurs sur l'état initial"""
        for mod in self.modificateurs_actifs:
            if mod == "plein_les_poches":
                self.etat.elixir += 5
                print(f"🪙 Modificateur {mod}: +5 élixir de départ appliqué!")
            elif mod == "plus_on_est_de_fous":
                self.taille_equipe_max = 7
                print(f"👥 Modificateur {mod}: Taille d'équipe augmentée à 7!")
            elif mod == "la_fete":
                self.taille_equipe_max = 6
                self.taille_equipe_fixe = True
                print(f"🎉 Modificateur {mod}: Taille d'équipe fixée à 6!")
            elif mod in ["etoile_rare", "etoile_epique", "etoile_légendaire", "etoile_de_champion"]:
                self.modificateur_etoile_debut = mod
                print(f"⭐ Modificateur {mod}: Carte améliorée au début configurée!")
            elif mod == "extracteur_elixir":
                self.extracteur_actif = True
                self.extracteur_stock = 0
                print(f"⚡ Modificateur {mod}: Extracteur d'élixir activé!")
            elif mod == "4_etoiles":
                self.choix_par_tour = 6  # Double sélection
                print(f"🌟 Modificateur {mod}: Sélection doublée (6 choix)!")
    
    def gerer_modificateurs_debut_tour(self):
        """Gère les effets des modificateurs en début de tour"""
        # Miroir magique
        if "miroir_magique" in self.modificateurs_actifs and self.etat.bench:
            carte_droite = self.etat.bench[-1]
            copie = Carte(carte_droite.nom, carte_droite.cout, carte_droite.traits, 1)
            self.etat.bench.append(copie)
            print(f"🪞 Miroir magique: Copie 1⭐ de {carte_droite.nom} ajoutée au banc!")
        
        # Banc de Pandore
        if "banc_de_pandore" in self.modificateurs_actifs and self.etat.bench:
            print(f"📦 Banc de Pandore: Troupe la plus à droite remplacée!")
            print("Quelle nouvelle troupe du même coût avez-vous reçue?")
            ancienne_carte = self.etat.bench[0]
            nouvelle_carte = self.selectionner_carte(f"Nouvelle troupe (coût {ancienne_carte.cout}):")
            if nouvelle_carte:
                self.etat.bench[0] = nouvelle_carte
        
        # Promotion (transformation en coût +1)
        if "promotion" in self.modificateurs_actifs and self.etat.bench:
            print(f"⬆️ Promotion: Troupe la plus à droite transformée!")
            ancienne_carte = self.etat.bench[-1]
            nouveau_cout = ancienne_carte.cout + 1
            print(f"Quelle troupe à {nouveau_cout} élixir avez-vous reçue?")
            nouvelle_carte = self.selectionner_carte(f"Nouvelle troupe (coût {nouveau_cout}):")
            if nouvelle_carte:
                self.etat.bench[-1] = nouvelle_carte
        
        # Clairvoyance
        if "clairvoyance" in self.modificateurs_actifs and len(self.etat.bench) == 0:
            self.etat.elixir += 2
            print(f"🔮 Clairvoyance: Banc vide, +2 élixir!")
        
        # Cheaté
        if "cheaté" in self.modificateurs_actifs:
            print(f"🎲 Cheaté: Troupe utile reçue!")
            troupe_utile = self.selectionner_carte("Quelle troupe utile avez-vous reçue?")
            if troupe_utile:
                self.etat.bench.append(troupe_utile)
        
        # Ascension (round 3 spécifiquement)
        if "ascension" in self.modificateurs_actifs and self.tour == 3 and self.etat.bench:
            carte_droite = self.etat.bench[-1]
            carte_droite.niveau = 3
            print(f"🚀 Ascension: {carte_droite.nom} transformé en 3⭐!")
    
    def gerer_modificateurs_fin_tour(self):
        """Gère les effets des modificateurs en fin de tour et questions post-round"""
        
        # Questions liées aux modificateurs
        questions_modificateurs = []
        
        if "heritage" in self.modificateurs_actifs:
            questions_modificateurs.append("heritage")
        if "tu_es_a_moi" in self.modificateurs_actifs:
            questions_modificateurs.append("copie_ennemi")
        if "rester_en_vie" in self.modificateurs_actifs:
            questions_modificateurs.append("mannequin_survie")
        if "bonne_affaire" in self.modificateurs_actifs:
            questions_modificateurs.append("ventes")
        if "offre_a_saisir" in self.modificateurs_actifs:
            questions_modificateurs.append("magasin_reset")
        
        # Questions liées aux bonus de familles actifs
        if "Gobelin" in self.bonus_familles_actifs:
            questions_modificateurs.append("bonus_gobelin")
        if "Ace" in self.bonus_familles_actifs:
            questions_modificateurs.append("bonus_ace")
        
        # Poser les questions selon les modificateurs actifs
        for question in questions_modificateurs:
            self.poser_question_modificateur(question)
        
        # De plus en plus riche (calcul d'intérêts)
        if "de_plus_en_plus_riche" in self.modificateurs_actifs:
            interets = self.etat.elixir // 2
            if interets > 0:
                print(f"💎 De plus en plus riche: +{interets} élixir d'intérêt au prochain round!")
                # On stocke pour l'appliquer au début du prochain tour
                if not hasattr(self, 'interets_stockes'):
                    self.interets_stockes = 0
                self.interets_stockes += interets
    
    def poser_question_modificateur(self, type_question):
        """Pose des questions spécifiques selon les modificateurs"""
        if type_question == "heritage":
            reponse = input("💀 Héritage: Un leader adverse est-il mort ce round? (o/n): ").strip().lower()
            if reponse in ['o', 'oui', 'y', 'yes']:
                self.etat.elixir += 5
                print("💰 +5 élixir grâce à l'héritage!")
        
        elif type_question == "copie_ennemi":
            if not hasattr(self, 'copie_ennemi_prise'):
                reponse = input("⚔️ Tu es à moi: Première troupe ennemie éliminée? (nom ou 'non'): ").strip()
                if reponse.lower() not in ['non', 'n', 'no']:
                    troupe_copiee = self.selectionner_carte(f"Quelle troupe ennemie avez-vous copiée?")
                    if troupe_copiee:
                        copie = Carte(troupe_copiee.nom, troupe_copiee.cout, troupe_copiee.traits, 1)
                        self.etat.bench.append(copie)
                        print(f"📋 Copie 1⭐ de {troupe_copiee.nom} ajoutée!")
                        self.copie_ennemi_prise = True
        
        elif type_question == "mannequin_survie":
            reponse = input("🎭 Mannequin: Votre mannequin a-t-il survécu? (o/n): ").strip().lower()
            if reponse in ['o', 'oui', 'y', 'yes']:
                self.etat.elixir += 1
                print("💰 +1 élixir pour la survie du mannequin!")
        
        elif type_question == "ventes":
            reponse = input("💸 Bonne affaire: Combien de troupes avez-vous vendues? (nombre): ").strip()
            try:
                nb_ventes = int(reponse)
                if nb_ventes > 0:
                    if not hasattr(self, 'bonus_ventes'):
                        self.bonus_ventes = 0
                    self.bonus_ventes += nb_ventes
                    print(f"💰 +{nb_ventes} élixir au prochain round grâce aux ventes!")
            except ValueError:
                pass
        
        elif type_question == "magasin_reset":
            reponse = input("🔄 Offre à saisir: Avez-vous reset le magasin? (o/n): ").strip().lower()
            if reponse in ['o', 'oui', 'y', 'yes']:
                print("💰 Une troupe coûte 1 élixir de moins dans cette sélection!")
        
        elif type_question == "bonus_gobelin":
            niveau_bonus = self.bonus_familles_actifs.get("Gobelin", 0)
            if niveau_bonus == 2:
                print("🟢 Bonus Gobelin (2): Gobelin bonus de 2 élixirs au prochain round!")
                if not hasattr(self, 'gobelin_bonus_elixir'):
                    self.gobelin_bonus_elixir = 0
                self.gobelin_bonus_elixir += 2
                
                reponse = input("🎲 Avez-vous reçu un Gobelin bonus aléatoire gratuit? (nom ou 'non'): ").strip()
                if reponse.lower() not in ['non', 'n', 'no']:
                    gobelin_bonus = self.selectionner_carte("Quel Gobelin bonus avez-vous reçu?")
                    if gobelin_bonus and "Gobelin" in gobelin_bonus.traits:
                        self.etat.bench.append(gobelin_bonus)
                        print(f"🎁 {gobelin_bonus.nom} gratuit ajouté au banc!")
            
            elif niveau_bonus == 4:
                reponse = input("🟢 Bonus Gobelin (4): Avez-vous gagné un Gobelin 3-4 élixir? (60% de chances) (o/n): ").strip().lower()
                if reponse in ['o', 'oui', 'y', 'yes']:
                    gobelin_bonus = self.selectionner_carte("Quel Gobelin 3-4 élixir avez-vous reçu?")
                    if gobelin_bonus and "Gobelin" in gobelin_bonus.traits and gobelin_bonus.cout in [3, 4]:
                        self.etat.bench.append(gobelin_bonus)
                        print(f"🎁 {gobelin_bonus.nom} bonus ajouté au banc!")
        
        elif type_question == "bonus_ace":
            niveau_bonus = self.bonus_familles_actifs.get("Ace", 0)
            if niveau_bonus in [2, 4]:
                if not hasattr(self, 'capitaine_ace'):
                    # Première fois qu'on active le bonus Ace, sélectionner le capitaine
                    print("👑 Bonus Ace: Sélection du capitaine (unité avec le plus haut niveau de fusion)")
                    if self.etat.main:
                        cartes_ace = [c for c in self.etat.main if "Ace" in c.traits]
                        if cartes_ace:
                            # Trouver le niveau le plus haut
                            niveau_max = max(c.niveau for c in cartes_ace)
                            capitaines_possibles = [c for c in cartes_ace if c.niveau == niveau_max]
                            
                            if len(capitaines_possibles) == 1:
                                self.capitaine_ace = capitaines_possibles[0].nom
                                print(f"👑 {self.capitaine_ace} est devenu capitaine!")
                            else:
                                print("Capitaines possibles:")
                                for i, c in enumerate(capitaines_possibles):
                                    print(f"{i+1}. {c}")
                                while True:
                                    try:
                                        choix = int(input("Quel Ace est devenu capitaine? (numéro): ")) - 1
                                        if 0 <= choix < len(capitaines_possibles):
                                            self.capitaine_ace = capitaines_possibles[choix].nom
                                            print(f"👑 {self.capitaine_ace} est devenu capitaine!")
                                            break
                                    except ValueError:
                                        pass
                
                # Questions sur les éliminations du capitaine
                if hasattr(self, 'capitaine_ace'):
                    eliminations = input(f"👑 Votre capitaine {self.capitaine_ace} a-t-il éliminé des troupes ce round? (nombre ou 0): ").strip()
                    try:
                        nb_eliminations = int(eliminations)
                        if nb_eliminations > 0:
                            print(f"⚡ Équipe: +{20 if niveau_bonus == 2 else 30}% vitesse de frappe pendant 4s!")
                    except ValueError:
                        pass
        
        # Questions supplémentaires pour l'extracteur
        if self.extracteur_actif and self.extracteur_stock > 0:
            reponse = input(f"⚡ Extracteur: Voulez-vous vendre l'extracteur? ({self.extracteur_stock} élixir stocké) (o/n): ").strip().lower()
            if reponse in ['o', 'oui', 'y', 'yes']:
                self.etat.elixir += self.extracteur_stock
                print(f"💰 +{self.extracteur_stock} élixir récupéré de l'extracteur!")
                self.extracteur_actif = False
                self.extracteur_stock = 0
    
    def calculer_bonus_familles(self):
        """Calcule les bonus de familles actifs selon les cartes sur le plateau"""
        familles_count = {}
        
        # Grouper d'abord par nom de carte (deux cartes identiques = 1 unité pour les bonus)
        cartes_uniques = {}
        for carte in self.etat.main:
            cartes_uniques[carte.nom] = carte  # Garde seulement une instance de chaque nom
        
        # Compter les familles basées sur les cartes uniques
        for nom_carte, carte in cartes_uniques.items():
            for trait in carte.traits:
                if trait in BONUS_FAMILLES:
                    familles_count[trait] = familles_count.get(trait, 0) + 1
        
        # Déterminer les bonus actifs selon les seuils de chaque famille
        self.bonus_familles_actifs = {}
        for famille, count in familles_count.items():
            bonus_niveaux = BONUS_FAMILLES[famille]
            
            # Familles qui activent à 3 cartes uniquement
            if famille in ["Assassin", "Guetteur", "Vengeuse", "Lanceur"]:
                if count >= 3:
                    self.bonus_familles_actifs[famille] = 3
            
            # Familles qui activent à 2 et 4 cartes
            elif famille in ["Noble", "Clan", "Gobelin", "Revenant", "Ace", "Colosse", "Bagarreur"]:
                if count >= 4:
                    self.bonus_familles_actifs[famille] = 4
                elif count >= 2:
                    self.bonus_familles_actifs[famille] = 2
    
    def afficher_bonus_familles(self):
        """Affiche les bonus de familles actifs"""
        if self.bonus_familles_actifs:
            print("\n🎯 BONUS DE FAMILLES ACTIFS:")
            for famille, niveau in self.bonus_familles_actifs.items():
                bonus_desc = BONUS_FAMILLES[famille][niveau]
                print(f"  • {famille} ({niveau}): {bonus_desc}")
        else:
            print("\n🔸 Aucun bonus de famille actif pour le moment.")
    
    def choisir_mode(self):
        # Simplification : plus de choix de mode, directement Merge Tactics
        print("🎮 MODE MERGE TACTICS SÉLECTIONNÉ")
        self.bibliotheque_cartes = BIBLIOTHEQUE_CARTES
        
    def afficher_bibliotheque(self):
        print(f"\n=== BIBLIOTHÈQUE DES CARTES MERGE TACTICS ===")
        cartes_par_cout = {}
        for nom, carte in self.bibliotheque_cartes.items():
            if carte.cout not in cartes_par_cout:
                cartes_par_cout[carte.cout] = []
            cartes_par_cout[carte.cout].append((nom, carte))
        
        for cout in sorted(cartes_par_cout.keys()):
            print(f"\n--- Coût {cout} ---")
            for i, (nom, carte) in enumerate(cartes_par_cout[cout]):
                print(f"{i+1}. {carte}")
    
    def selectionner_carte(self, prompt: str) -> Optional[Carte]:
        while True:
            print(f"\n{prompt}")
            print("Tapez le nom de la carte, son numéro, ou 'list' pour voir la bibliothèque:")
            
            # Afficher les cartes avec numéros pour sélection rapide
            cartes_par_cout = {}
            for nom, carte in self.bibliotheque_cartes.items():
                if carte.cout not in cartes_par_cout:
                    cartes_par_cout[carte.cout] = []
                cartes_par_cout[carte.cout].append((nom, carte))
            
            # Créer une liste numérotée de toutes les cartes
            liste_cartes = []
            print("\nCartes disponibles:")
            for cout in sorted(cartes_par_cout.keys()):
                print(f"\n--- Coût {cout} ---")
                for nom, carte in cartes_par_cout[cout]:
                    liste_cartes.append((nom, carte))
                    print(f"{len(liste_cartes)}. {carte}")
            
            choix = input("\n> ").strip()
            
            if choix.lower() == 'list':
                self.afficher_bibliotheque()
                continue
            elif choix.lower() == 'quit' or choix.lower() == 'exit':
                return None
            elif choix.isdigit():
                # Sélection par numéro
                try:
                    index = int(choix) - 1
                    if 0 <= index < len(liste_cartes):
                        return liste_cartes[index][1]
                    else:
                        print(f"Numéro invalide. Choisissez entre 1 et {len(liste_cartes)}.")
                except ValueError:
                    print("Numéro invalide.")
            elif choix in self.bibliotheque_cartes:
                return self.bibliotheque_cartes[choix]
            else:
                # Recherche approximative
                matches = [nom for nom in self.bibliotheque_cartes.keys() 
                          if choix.lower() in nom.lower()]
                if len(matches) == 1:
                    return self.bibliotheque_cartes[matches[0]]
                elif len(matches) > 1:
                    print(f"Plusieurs correspondances trouvées: {', '.join(matches)}")
                else:
                    print("Carte non trouvée. Tapez 'list' pour voir toutes les cartes.")
    
    def afficher_etat(self):
        print(f"\n=== TOUR {self.tour} - MERGE TACTICS ===")
        print(f"Élixir: {self.etat.elixir}")
        
        # Affichage des modificateurs actifs
        if self.modificateurs_actifs:
            print(f"🎮 Modificateurs actifs: {', '.join(self.modificateurs_actifs[:3])}{'...' if len(self.modificateurs_actifs) > 3 else ''}")
        
        # Affichage des ressources spéciales
        if self.extracteur_actif:
            print(f"⚡ Extracteur d'élixir: {self.extracteur_stock} stocké")
        
        if hasattr(self, 'interets_stockes') and self.interets_stockes > 0:
            print(f"💎 Intérêts en attente: +{self.interets_stockes} au prochain tour")
        
        if hasattr(self, 'bonus_ventes') and self.bonus_ventes > 0:
            print(f"💸 Bonus ventes en attente: +{self.bonus_ventes} au prochain tour")
        
        if hasattr(self, 'gobelin_bonus_elixir') and self.gobelin_bonus_elixir > 0:
            print(f"🟢 Bonus Gobelin en attente: +{self.gobelin_bonus_elixir} au prochain tour")
        
        if self.tour > 1:
            print(f"(+{self.elixir_par_tour} élixir par tour)")
        
        print(f"Plateau ({len(self.etat.main)} cartes):")
        if self.etat.main:
            for i, carte in enumerate(self.etat.main):
                print(f"  {i+1}. {carte}")
        else:
            print("  (Aucune carte sur le plateau)")
        
        if self.mannequin_actif:
            if hasattr(self, 'mannequin_special') and self.mannequin_special:
                print("  🎭✨ Mannequin spécial (2 attributs)")
            else:
                print("  🎭 Mannequin")
        
        # Calcul et affichage des bonus de familles
        self.calculer_bonus_familles()
        self.afficher_bonus_familles()
        
        if self.etat.bench:
            print(f"Banc ({len(self.etat.bench)} cartes):")
            for i, carte in enumerate(self.etat.bench):
                print(f"  {i+1}. {carte}")
        
        if self.etat.historique_pool:
            print("Historique du pool:")
            for nom, count in self.etat.historique_pool.items():
                print(f"  {nom}: {count} fois")
    
    def configuration_initiale(self):
        print("=== CONFIGURATION INITIALE ===")
        print("Configurons votre setup de départ pour Merge Tactics...")
        
        # Gestion des modificateurs spéciaux au début
        if self.modificateur_etoile_debut:
            print(f"\n⭐ Modificateur {self.modificateur_etoile_debut} actif!")
            carte_speciale = self.configurer_carte_etoile_debut()
            if carte_speciale:
                self.etat.main.append(carte_speciale)
                self.cartes_initiales = 0  # Déjà configuré avec le modificateur
        
        if "rester_en_vie" in self.modificateurs_actifs:
            print("\n🎭 Modificateur 'Rester en vie': Mannequin ajouté!")
            self.mannequin_actif = True
        
        if "mannequin_special" in self.modificateurs_actifs:
            print("\n🎭✨ Modificateur 'Mannequin spécial': Mannequin avec 2 attributs ajouté!")
            self.mannequin_actif = True
            self.mannequin_special = True
        
        if self.cartes_initiales > 0:
            print(f"Vous commencez avec {self.cartes_initiales} carte(s) déjà posée(s).")
            for i in range(self.cartes_initiales):
                print(f"\nCarte {i+1}/{self.cartes_initiales} de départ:")
                
                # Sélection de la carte
                carte = self.selectionner_carte(f"Quelle carte avez-vous en position {i+1}?")
                if carte:
                    # Demander le niveau (important en Merge Tactics)
                    while True:
                        try:
                            niveau_input = input(f"Quel niveau pour {carte.nom}? (défaut: 1): ").strip()
                            if niveau_input == "":
                                niveau = 1
                            else:
                                niveau = int(niveau_input)
                            if niveau >= 1:
                                # Créer une nouvelle carte avec le bon niveau
                                carte_avec_niveau = Carte(carte.nom, carte.cout, carte.traits, niveau)
                                self.etat.main.append(carte_avec_niveau)
                                break
                            else:
                                print("Le niveau doit être au moins 1.")
                        except ValueError:
                            print("Veuillez entrer un nombre valide.")
                    
                    # Mise à jour de l'historique
                    if carte.nom in self.etat.historique_pool:
                        self.etat.historique_pool[carte.nom] += 1
                    else:
                        self.etat.historique_pool[carte.nom] = 1
        
        # Vérification de l'élixir initial (peut varier avec les bonus)
        elixir_defaut = 4
        print(f"\nVérification de l'élixir de départ (normal: {elixir_defaut})")
        while True:
            try:
                elixir = int(input(f"Combien d'élixir avez-vous actuellement? (défaut: {elixir_defaut}): ") or str(elixir_defaut))
                if elixir >= 0:
                    self.etat.elixir = elixir
                    break
                else:
                    print("L'élixir doit être positif.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
    
    def configurer_carte_etoile_debut(self):
        """Configure la carte spéciale obtenue avec les modificateurs étoile"""
        cout_max = {
            "etoile_rare": 2,
            "etoile_epique": 3, 
            "etoile_légendaire": 4,
            "etoile_de_champion": 5
        }
        
        cout = cout_max[self.modificateur_etoile_debut]
        print(f"Sélectionnez votre troupe 2⭐ à {cout} élixir:")
        
        # Filtrer les cartes par coût
        cartes_dispo = {nom: carte for nom, carte in self.bibliotheque_cartes.items() 
                       if carte.cout == cout}
        
        print(f"Cartes à {cout} élixir disponibles:")
        for i, (nom, carte) in enumerate(cartes_dispo.items()):
            print(f"{i+1}. {carte}")
        
        carte_choisie = self.selectionner_carte(f"Votre choix (coût {cout}):")
        if carte_choisie and carte_choisie.cout == cout:
            # Créer la carte 2 étoiles
            return Carte(carte_choisie.nom, carte_choisie.cout, carte_choisie.traits, 2)
        
        return None
    
    def tour_de_jeu(self):
        # Gestion des modificateurs en début de tour
        self.gerer_modificateurs_debut_tour()
        
        # Ajout d'élixir au début du tour (sauf tour 1)
        if self.tour > 1:
            elixir_gagne = self.elixir_par_tour
            
            # Intérêts stockés (de plus en plus riche)
            if hasattr(self, 'interets_stockes') and self.interets_stockes > 0:
                elixir_gagne += self.interets_stockes
                print(f"💎 Intérêts: +{self.interets_stockes} élixir!")
                self.interets_stockes = 0
            
            # Bonus de ventes stockés
            if hasattr(self, 'bonus_ventes') and self.bonus_ventes > 0:
                elixir_gagne += self.bonus_ventes
                print(f"💸 Bonus ventes: +{self.bonus_ventes} élixir!")
                self.bonus_ventes = 0
            
            # Bonus élixir Gobelin stockés
            if hasattr(self, 'gobelin_bonus_elixir') and self.gobelin_bonus_elixir > 0:
                elixir_gagne += self.gobelin_bonus_elixir
                print(f"🟢 Bonus Gobelin: +{self.gobelin_bonus_elixir} élixir!")
                self.gobelin_bonus_elixir = 0
            
            # Extracteur d'élixir
            if self.extracteur_actif:
                elixir_gagne += 2
                self.extracteur_stock += 2
                print(f"⚡ Extracteur d'élixir: +2 élixir stocké (total stocké: {self.extracteur_stock})")
            
            self.etat.elixir += elixir_gagne
            print(f"\n💰 +{elixir_gagne} élixir! Total: {self.etat.elixir}")
        
        self.afficher_etat()
        
        print("\n=== CHOIX DISPONIBLES ===")
        options = []
        
        # Sélection des options
        nb_choix = self.choix_par_tour
        while len(options) < nb_choix:
            carte = self.selectionner_carte(f"Sélectionnez l'option {len(options)+1}/{nb_choix} (ou 'quit' pour terminer):")
            if carte is None:
                if len(options) == 0:
                    return False  # Quitter le jeu
                break
            options.append(carte)
        
        if not options:
            return False
        
        print(f"\nOptions disponibles:")
        for i, carte in enumerate(options):
            print(f"{i+1}. {carte}")
        
        # Analyse et recommandation avec bonus de familles
        meilleur = self.meilleur_choix_avec_familles(options)
        
        if meilleur:
            print(f"\n🎯 RECOMMANDATION: {meilleur.nom}")
            # Affichage des scores détaillés
            print("\nAnalyse détaillée:")
            sc_traits = score_traits(meilleur, self.etat.main + self.etat.bench, self.weights)
            sc_merge = score_merge(meilleur, self.etat.main, self.weights)
            sc_infinite = score_infinite_elixir(meilleur, self.etat.main, self.weights)
            sc_disruption = score_disruption(meilleur, self.etat.historique_pool, self.weights)
            sc_budget = score_budget(meilleur, self.etat, self.weights)
            sc_familles = self.score_familles(meilleur)
            
            print(f"  • Score traits: {sc_traits:.2f}")
            print(f"  • Score fusion: {sc_merge:.2f}")
            print(f"  • Score élixir infini: {sc_infinite:.2f}")
            print(f"  • Score disruption: {sc_disruption:.2f}")
            print(f"  • Score budget: {sc_budget:.2f}")
            print(f"  • Score familles: {sc_familles:.2f}")
            print(f"  • TOTAL: {sc_traits + sc_merge + sc_infinite + sc_disruption + sc_budget + sc_familles:.2f}")
        else:
            print("\n❌ Aucun choix recommandé (pas assez d'élixir)")
        
        # Gestion de la première carte gratuite
        premiere_achat = True
        
        # Demander quel choix l'utilisateur a fait
        while True:
            try:
                choix_index = int(input(f"\nQuel choix avez-vous fait? (1-{len(options)}, 0 pour aucun): "))
                if choix_index == 0:
                    break
                elif 1 <= choix_index <= len(options):
                    carte_choisie = options[choix_index - 1]
                    
                    # Demander le niveau de la carte choisie
                    while True:
                        try:
                            niveau_input = input(f"Quel niveau pour {carte_choisie.nom}? (défaut: 1): ").strip()
                            if niveau_input == "":
                                niveau = 1
                            else:
                                niveau = int(niveau_input)
                            if niveau >= 1:
                                break
                            else:
                                print("Le niveau doit être au moins 1.")
                        except ValueError:
                            print("Veuillez entrer un nombre valide.")
                    
                    # Créer la carte avec le bon niveau
                    carte_avec_niveau = Carte(carte_choisie.nom, carte_choisie.cout, carte_choisie.traits, niveau)
                    
                    # Calculer le coût avec modificateurs
                    cout_final = carte_choisie.cout
                    if "cadeau_de_la_maison" in self.modificateurs_actifs and premiere_achat:
                        cout_final = 0
                        print("🎁 Première carte gratuite grâce au modificateur!")
                        premiere_achat = False
                    elif "premier_choix" in self.modificateurs_actifs and premiere_achat:
                        carte_avec_niveau.niveau = 2
                        print("⭐ Première carte transformée en 2 étoiles!")
                        premiere_achat = False
                    
                    # Mettre à jour l'état
                    self.etat.elixir -= cout_final
                    self.etat.main.append(carte_avec_niveau)
                    
                    # Mise à jour de l'historique
                    if carte_choisie.nom in self.etat.historique_pool:
                        self.etat.historique_pool[carte_choisie.nom] += 1
                    else:
                        self.etat.historique_pool[carte_choisie.nom] = 1
                    
                    print(f"✅ {carte_choisie.nom} niveau {niveau} ajouté à votre plateau!")
                    break
                else:
                    print(f"Veuillez entrer un nombre entre 0 et {len(options)}.")
            except ValueError:
                print("Veuillez entrer un nombre valide.")
        
        # Gestion des modificateurs en fin de tour
        self.gerer_modificateurs_fin_tour()
        
        self.tour += 1
        return True
    
    def score_familles(self, carte: Carte) -> float:
        """Score une carte selon son potentiel d'amélioration des bonus de familles"""
        score = 0
        
        # Simulation : ajouter cette carte et recalculer les bonus
        familles_count = {}
        for carte_existante in self.etat.main:
            for trait in carte_existante.traits:
                if trait in BONUS_FAMILLES:
                    familles_count[trait] = familles_count.get(trait, 0) + 1
        
        # Ajouter la nouvelle carte
        for trait in carte.traits:
            if trait in BONUS_FAMILLES:
                familles_count[trait] = familles_count.get(trait, 0) + 1
        
        # Calculer les bonus après ajout selon les vrais seuils
        for famille, count in familles_count.items():
            # Familles qui activent à 3 cartes uniquement
            if famille in ["Assassin", "Guetteur", "Vengeuse", "Lanceur"]:
                if count == 3:  # Activation du bonus (3 cartes)
                    score += 5.0
                elif count == 2:  # Proche de l'activation
                    score += 3.0
                elif count > 3:  # Plus de 3 cartes (synergie)
                    score += 1.5
            
            # Familles qui activent à 2 et 4 cartes
            elif famille in ["Noble", "Clan", "Gobelin", "Revenant", "Ace", "Colosse", "Bagarreur"]:
                if count == 2:  # Activation premier bonus (2 cartes)
                    score += 4.0
                elif count == 4:  # Activation deuxième bonus (4 cartes)
                    score += 6.0
                elif count == 3:  # Proche du deuxième bonus
                    score += 2.0
                elif count > 4:  # Plus de 4 cartes (synergie)
                    score += 1.0
        
        return score
    
    def meilleur_choix_avec_familles(self, options: List[Carte]) -> Optional[Carte]:
        """Version améliorée qui prend en compte les bonus de familles"""
        meilleurscore = float('-inf')
        meilleur = None
        for c in options:
            if c.cout > self.etat.elixir:
                continue
            sc = 0
            sc += score_traits(c, self.etat.main + self.etat.bench, self.weights)
            sc += score_merge(c, self.etat.main, self.weights)
            sc += score_infinite_elixir(c, self.etat.main, self.weights)
            sc += score_disruption(c, self.etat.historique_pool, self.weights)
            sc += score_budget(c, self.etat, self.weights)
            sc += self.score_familles(c)  # Nouveau score familles
            if sc > meilleurscore:
                meilleurscore = sc
                meilleur = c
        return meilleur
    
    def run(self):
        print("🏰 CLASH ROYALE MERGE TACTICS ASSISTANT 🏰")
        print("Bienvenue! Je vais vous aider à optimiser vos choix pendant la partie.")
        
        # Configuration directe pour Merge Tactics
        self.choisir_mode()
        
        # Configuration des modificateurs
        self.configuration_modificateurs()
        
        # Configuration initiale
        self.configuration_initiale()
        
        print(f"\n🎮 La partie Merge Tactics commence! Tapez 'quit' à tout moment pour arrêter.")
        
        while True:
            if not self.tour_de_jeu():
                break
        
        print("\n👋 Merci d'avoir joué! À bientôt!")

def score_traits(carte: Carte, main: List[Carte], weights: Dict[str, float]) -> float:
    score = 0
    for trait in carte.traits:
        count = sum(trait in c.traits for c in main)
        score += weights['traits'] * count
    return score

def score_merge(carte: Carte, main: List[Carte], weights: Dict[str, float]) -> float:
    same = sum(1 for c in main if c.nom == carte.nom)
    return weights['merge'] if same >= 1 else 0

def score_infinite_elixir(carte: Carte, main: List[Carte], weights: Dict[str, float]) -> float:
    # Simule fusion + vente post-fusion
    same = sum(1 for c in main if c.nom == carte.nom and c.niveau == carte.niveau)
    if same >= 1:
        # Fusion possible, puis vente = gain net d'1 élixir
        return weights['fusion_sell'] * 1
    return 0

def score_disruption(carte: Carte, historique_pool: Dict[str, int], weights: Dict[str, float]) -> float:
    dispo = historique_pool.get(carte.nom, 4)
    return weights['disruption'] / dispo

def score_budget(carte: Carte, etat: EtatJeu, weights: Dict[str, float]) -> float:
    return -weights['cost'] * carte.cout

def meilleur_choix(options: List[Carte], etat: EtatJeu, weights: Dict[str, float]) -> Optional[Carte]:
    meilleurscore = float('-inf')
    meilleur = None
    for c in options:
        if c.cout > etat.elixir:
            continue
        sc = 0
        sc += score_traits(c, etat.main + etat.bench, weights)
        sc += score_merge(c, etat.main, weights)
        sc += score_infinite_elixir(c, etat.main, weights)
        sc += score_disruption(c, etat.historique_pool, weights)
        sc += score_budget(c, etat, weights)
        if sc > meilleurscore:
            meilleurscore = sc
            meilleur = c
    return meilleur

if __name__ == "__main__":
    session = GameSession()
    session.run()
