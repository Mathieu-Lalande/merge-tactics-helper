# 🏰 Clash Royale Merge Tactics Assistant

Une application web moderne et interactive pour optimiser vos parties de Merge Tactics dans Clash Royale. Interface rapide et intuitive avec système d'achat ultra-rapide pour respecter la limite de 30 secondes par tour.

## ✨ Fonctionnalités principales

- ⚡ **Mode Achat Rapide** - Interface optimisée pour des achats en moins de 30 secondes
- 🎯 **Recommandations IA intelligentes** basées sur la composition actuelle et les synergies
- 📊 **Suivi dynamique des bonus de familles** (Noble, Clan, Gobelin, Revenant, Ace, etc.)
- 🔧 **Gestion complète des modificateurs** (27+ modificateurs disponibles)
- �️ **Drag & Drop** - Déplacez vos cartes entre banc et plateau intuitivement
- 🔄 **Fusion automatique et manuelle** - Système de fusion robuste et récursif
- 🗑️ **Suppression de cartes** - Récupérez de l'élixir en vendant des cartes
- 🏆 **Gestion des leaders** - Bonus spéciaux selon votre choix de leader
- �💾 **État persistant** de la partie avec historique complet
- 🎮 **Interface moderne** avec animations et notifications
- 🎯 **Plateau hexagonal** - Visualisation et placement stratégique des troupes

## 🚀 Installation et Lancement

### Prérequis
- Python 3.7 ou plus récent
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger le projet**

2. **Installer les dépendances Python**
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application**
   ```bash
   python app.py
   ```

4. **Ouvrir votre navigateur**
   - L'application se lance sur : `http://localhost:5000`
   - Le navigateur s'ouvrira automatiquement

## 🎮 Comment utiliser l'application

### 1. Configuration initiale (une seule fois)
- **Choisissez votre leader** avec ses bonus spéciaux (fusion, victoire, etc.)
- **Sélectionnez UN modificateur** de partie parmi 27+ disponibles
- **Configurez votre carte de départ** et l'élixir initial

### 2. Interface de jeu principale
- **Plateau** : Vos cartes actives au combat (limite selon votre progression)
- **Banc** : Vos cartes en réserve, prêtes à être déployées
- **Bonus de Familles** : Suivi en temps réel des synergies actives
- **Plateau Hexagonal** : Visualisation du placement stratégique des troupes

### 3. Mode Achat Rapide ⚡ (recommandé)
- **4 cartes populaires** affichées en permanence (2x2 grille)
- **Sélection du niveau** (1-5) avant achat
- **Achat instantané** en un clic - perfect pour la limite de 30s
- **Fusion automatique** dès qu'un achat crée 3+ cartes identiques
- **Notifications visuelles** pour les fusions en cascade

### 4. Fonctionnalités avancées
- **Drag & Drop** : Glissez vos cartes entre banc et plateau
- **Fusion manuelle** : Cliquez sur ⚡ pour fusionner 3 cartes identiques
- **Suppression** : Cliquez sur 🗑️ pour vendre une carte contre de l'élixir
- **Plateau hexagonal** : Placez vos troupes stratégiquement sur la grille
- **Gestion des HP** : Suivi des points de vie et conditions de victoire/défaite

### 5. Conseils d'utilisation
- **Utilisez le mode rapide** pour respecter les 30 secondes par tour
- **Surveillez les bonus de familles** pour optimiser vos achats
- **Placez vos meilleures cartes sur le plateau** avant le combat
- **Gardez de l'élixir** pour les opportunités de fusion

## 🏗️ Structure du projet

```
clashroyale/
├── app.py                 # Serveur Flask (backend API)
├── main.py               # Logique de jeu originale (CLI)
├── requirements.txt      # Dépendances Python
├── templates/
│   └── index.html       # Interface web principale
└── static/
    ├── css/
    │   └── style.css    # Styles modernes
    └── js/
        └── app.js       # Logique frontend JavaScript
```

## 🎯 Fonctionnalités détaillées

### Système de cartes Merge Tactics
- **18 cartes disponibles** : Toutes les cartes officielles du mode Merge Tactics
- **Coûts variés** : 2-5 élixir selon la rareté
- **Familles/Traits** : 11 familles différentes avec bonus synergiques
  - Noble, Clan, Gobelin, Revenant, Ace, Colosse
  - Assassin, Guetteur, Bagarreur, Vengeuse, Lanceur
- **Niveaux de fusion** : 1 à 5 étoiles avec progression exponentielle

### Bonus de familles dynamiques
- **Activation automatique** : 2, 3 ou 4 cartes selon la famille
- **Calcul intelligent** : Cartes identiques comptent comme 1 unité unique
- **Effets puissants** : Bonus de dégâts, PV, vitesse, boucliers, etc.
- **Suivi visuel** : Interface claire montrant les bonus actifs/inactifs

### Système de fusion avancé
- **Fusion automatique** : 3 cartes identiques → 1 carte niveau supérieur
- **Fusion récursive** : Gestion des fusions en cascade (ex: 9 → 3 → 1)
- **Fusion manuelle** : Bouton ⚡ pour déclencher manuellement
- **Gain d'élixir** : +1 élixir par fusion + bonus du leader
- **Sécurité** : Logique robuste évitant les bugs et pertes de cartes

### Leaders et bonus spéciaux
- **Choix stratégique** : Chaque leader offre des bonus uniques
- **Bonus de fusion** : Élixir supplémentaire lors des fusions
- **Bonus de victoire** : Récompenses après victoire en combat
- **Adaptabilité** : Bonus s'activent selon vos actions en jeu

### Modificateurs de partie (27+ disponibles)
- **Économiques** : "Plein les poches" (+5 élixir), "Cadeau de la maison" (1ère carte gratuite)
- **Stratégiques** : "Plus on est de fous" (+1 taille équipe), "Moins c'est mieux" (bonus si moins de troupes)
- **Spéciaux** : "Miroir magique" (copie automatique), "Banc de Pandore" (remplacement aléatoire)
- **Élite** : "4 étoiles" (sélection doublée), "Ascension" (troupe 3⭐ au round 3)

### Interface utilisateur moderne
- **Design responsive** : Optimisé pour tous les écrans
- **Animations fluides** : Notifications, gains d'élixir, fusions
- **Drag & Drop intuitif** : Déplacement naturel des cartes
- **Mode sombre élégant** : Palette de couleurs soignée
- **Feedback visuel** : Confirmations, erreurs, succès clairement indiqués

## 🛠️ Fonctionnalités techniques

### Architecture
- **Backend** : Flask (Python) - API REST complète
- **Frontend** : HTML5, CSS3, JavaScript vanilla moderne
- **Stockage** : Sessions en mémoire avec UUID uniques
- **Communication** : AJAX asynchrone pour une expérience fluide

### APIs disponibles
- `POST /api/new_game` : Créer une nouvelle partie
- `GET /api/game_state/<session_id>` : État actuel de la partie
- `POST /api/buy_card` : Acheter une carte (mode rapide)
- `POST /api/move_card` : Déplacer une carte (drag & drop)
- `POST /api/manual_merge` : Fusionner manuellement
- `POST /api/delete_card` : Supprimer une carte
- `POST /api/battle_result` : Enregistrer résultat de bataille

### Sécurité et robustesse
- **Validation côté serveur** : Toutes les actions sont vérifiées
- **Gestion d'erreurs** : Messages clairs en cas de problème
- **Limites respectées** : Plateau, élixir, niveaux de fusion
- **Sessions isolées** : Chaque partie est indépendante

## 🐛 Dépannage et FAQ

### L'application ne démarre pas
1. **Vérifiez Python** : `python --version` (nécessite Python 3.7+)
2. **Installez les dépendances** : `pip install -r requirements.txt`
3. **Vérifiez le port** : Le port 5000 doit être libre
4. **Permissions** : Exécutez en tant qu'administrateur si nécessaire

### Erreurs dans le navigateur
1. **Actualisez la page** (F5) après avoir redémarré le serveur
2. **Console développeur** (F12) pour voir les erreurs détaillées  
3. **Cache du navigateur** : Ctrl+F5 pour vider le cache
4. **JavaScript activé** : Vérifiez que JS n'est pas bloqué

### Problèmes de fusion
- ✅ **Corrigé** : La logique de fusion a été entièrement reécrite
- ✅ **Fusion récursive** : Les fusions en cascade fonctionnent parfaitement
- ✅ **Cartes perdues** : Plus de problème de cartes qui disparaissent
- 💡 **Astuce** : Les fusions se font automatiquement après chaque achat

### Performance et optimisation
- **Rechargement automatique** : L'état se met à jour toutes les 30 secondes
- **Mode rapide** : Interface optimisée pour les achats rapides
- **Stockage local** : Pas de base de données, tout en mémoire
- **Compatibilité** : Fonctionne sur Chrome, Firefox, Edge, Safari

## 🚀 Conseils pour bien jouer

### Stratégies de base
1. **Priorité aux bonus** : Visez 2-4 cartes de même famille
2. **Gestion de l'élixir** : Gardez toujours 3-4 élixir de réserve
3. **Fusion intelligente** : Ne vendez pas avant d'avoir 3 cartes identiques
4. **Placement stratégique** : Vos meilleures cartes devant, support derrière

### Optimisation avancée
- **Calcul des synergies** : 2 Noble + 2 Clan = double bonus
- **Timing des achats** : Achetez en fin de tour pour maximiser les fusions
- **Gestion du plateau** : Respectez la limite de cartes actives
- **Leaders synergiques** : Choisissez selon votre style de jeu

### Modificateurs recommandés
- **Débutant** : "Cadeau de la maison" (1ère carte gratuite)
- **Économique** : "Plein les poches" (+5 élixir de départ)  
- **Agressif** : "4 étoiles" (plus de choix disponibles)
- **Expert** : "Miroir magique" (copies automatiques)

## 📝 Notes techniques et développement

### Stack technologique
- **Backend** : Flask 2.3.3 (Python) - API REST légère et rapide
- **Frontend** : HTML5, CSS3, JavaScript ES6+ vanilla
- **Stockage** : Sessions en mémoire avec UUID (pas de base de données)
- **Compatibilité** : Navigateurs modernes (Chrome 80+, Firefox 75+, Edge 80+, Safari 13+)

### Architecture modulaire
- `app.py` : Serveur Flask avec toutes les routes API
- `main.py` : Classes et logique métier (GameSession, Carte, etc.)
- `static/js/app.js` : Interface utilisateur et interactions
- `static/css/style.css` : Design moderne avec variables CSS
- `templates/index.html` : Structure HTML de l'application

### Extensibilité et personnalisation
- **Nouvelles cartes** : Ajout facile dans `BIBLIOTHEQUE_CARTES`
- **Nouveaux modificateurs** : Extension simple de `MODIFICATEURS_PARTIE`
- **Bonus personnalisés** : Modification de `BONUS_FAMILLES`
- **Interface** : CSS variables pour changer couleurs et thème
- **API** : Endpoints REST documentés et extensibles

## 🤝 Contribution et support

### Comment contribuer
1. **Tests** : Testez l'application et signalez les bugs
2. **Feedback** : Proposez des améliorations d'interface ou de gameplay
3. **Idées** : Suggérez de nouvelles cartes ou modificateurs
4. **Documentation** : Aidez à améliorer ce README ou les commentaires

### Signaler un problème
- **Fusion bug** : ✅ Déjà corrigé dans la dernière version
- **Interface** : Décrivez précisément le problème rencontré
- **Performance** : Mentionnez votre navigateur et OS
- **Fonctionnalité** : Expliquez le comportement attendu vs réel

### Feuille de route
- [ ] Mode multijoueur en local
- [ ] Sauvegarde des parties
- [ ] Statistiques et historique
- [ ] Mode tournoi
- [ ] API publique pour extensions

---

## 🎯 Résumé rapide

**Clash Royale Merge Tactics Assistant** est l'outil ultime pour dominer le mode Merge Tactics ! Interface ultra-rapide, fusion automatique, drag & drop, et strategies optimisées. Parfait pour respecter la limite de 30 secondes par tour tout en prenant les meilleures décisions.

**Installation** : `pip install -r requirements.txt` → `python app.py` → `http://localhost:5000`

**Bonne chance sur le champ de bataille ! �⚔️**
