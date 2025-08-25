# 🔐 Guide des Comptes et Sauvegardes

Ce guide explique comment utiliser les nouvelles fonctionnalités de gestion de compte et de sauvegarde dans l'assistant Clash Royale Merge Tactics.

## 👤 Gestion des Comptes

### Création d'un compte

1. **Cliquez sur "Inscription"** dans l'en-tête de l'application
2. **Remplissez le formulaire** :
   - Nom d'utilisateur (minimum 3 caractères)
   - Adresse email valide
   - Mot de passe (minimum 6 caractères)
   - Confirmation du mot de passe
3. **Cliquez sur "S'inscrire"**

Votre compte est créé et vous êtes automatiquement connecté !

### Connexion

1. **Cliquez sur "Connexion"** dans l'en-tête
2. **Entrez vos identifiants** :
   - Nom d'utilisateur
   - Mot de passe
3. **Cliquez sur "Se connecter"**

### Déconnexion

Cliquez simplement sur le bouton **"Déconnexion"** à côté de votre nom d'utilisateur.

## 💾 Gestion des Sauvegardes

### Sauvegarder une partie

1. **Connectez-vous** à votre compte
2. **Démarrez une partie** et configurez-la
3. **Cliquez sur "Sauvegardes"** dans l'en-tête
4. **Cliquez sur "Sauvegarder la partie actuelle"**
5. **Donnez un nom** à votre sauvegarde
6. **Cliquez sur "Sauvegarder"**

### Charger une partie sauvegardée

1. **Cliquez sur "Sauvegardes"** dans l'en-tête
2. **Trouvez la partie** que vous voulez charger
3. **Cliquez sur "Charger"**

La partie se charge immédiatement avec :
- Votre tour actuel
- Votre élixir
- Vos points de vie
- Toutes vos cartes (plateau et banc)
- Vos bonus de familles
- Votre leader et modificateur

### Mettre à jour une sauvegarde

Si vous avez une partie en cours qui correspond à une sauvegarde existante :

1. **Ouvrez la liste des sauvegardes**
2. **Cliquez sur "Mettre à jour"** sur la sauvegarde concernée

Cela met à jour la sauvegarde avec l'état actuel de votre partie.

### Supprimer une sauvegarde

1. **Ouvrez la liste des sauvegardes**
2. **Cliquez sur "Supprimer"** (icône poubelle)
3. **Confirmez la suppression**

⚠️ **Attention** : Cette action est irréversible !

## 📊 Statistiques

### Accéder aux statistiques

1. **Connectez-vous** à votre compte
2. **Cliquez sur "Stats"** dans l'en-tête

### Statistiques disponibles

#### Vue d'ensemble
- **Parties jouées** : Nombre total de parties terminées
- **Taux de victoire** : Pourcentage de victoires
- **Meilleur tour** : Tour le plus élevé atteint
- **Tour moyen** : Moyenne des tours atteints
- **Élixir total** : Élixir total gagné dans toutes les parties
- **Fusions totales** : Nombre total de fusions effectuées

#### Préférences
- **Leader favori** : Leader le plus utilisé
- **Modificateur favori** : Modificateur le plus utilisé

#### Historique récent
Les 10 dernières parties avec :
- Résultat (Victoire/Défaite)
- Tour atteint
- Leader utilisé
- Date de la partie

### Sauvegarde automatique des statistiques

Les statistiques sont **automatiquement sauvegardées** à la fin de chaque partie :
- Lorsque vous cliquez sur "Victoire" ou "Défaite"
- Les données sont immédiatement ajoutées à votre profil
- Aucune action manuelle requise

## 🗂️ Structure des Données

### Stockage local

Toutes les données sont stockées localement dans le dossier `data/` :

- `accounts.json` : Comptes utilisateurs (mots de passe hashés)
- `saved_games.json` : Parties sauvegardées
- `game_stats.json` : Statistiques des parties

### Sécurité

- **Mots de passe hashés** : Les mots de passe ne sont jamais stockés en clair
- **Sessions sécurisées** : Utilisation des sessions Flask
- **Isolation des données** : Chaque utilisateur ne peut accéder qu'à ses propres données

## 🛠️ Dépannage

### Problèmes de connexion

**"Nom d'utilisateur ou mot de passe incorrect"**
- Vérifiez l'orthographe de votre nom d'utilisateur
- Vérifiez que votre mot de passe est correct
- Les mots de passe sont sensibles à la casse

**"Ce nom d'utilisateur existe déjà"**
- Choisissez un autre nom d'utilisateur
- Ou connectez-vous si c'est votre compte

### Problèmes de sauvegarde

**"Connexion requise pour sauvegarder"**
- Créez un compte ou connectez-vous
- Les sauvegardes nécessitent un compte utilisateur

**"Aucune partie active trouvée"**
- Démarrez une nouvelle partie
- Configurez au moins le leader avant de sauvegarder

**"Sauvegarde introuvable"**
- La sauvegarde a peut-être été supprimée
- Vérifiez que vous êtes connecté au bon compte

### Problèmes de statistiques

**"Aucune statistique disponible"**
- Terminez au moins une partie pour voir des statistiques
- Les statistiques ne s'accumulent qu'après avoir cliqué "Victoire" ou "Défaite"

## 🚀 Conseils d'utilisation

### Gestion efficace des sauvegardes

1. **Nommage clair** : Utilisez des noms descriptifs
   - ✅ "Partie Noble/Clan Tour 8"
   - ❌ "Ma partie"

2. **Sauvegarde régulière** : Sauvegardez aux moments clés
   - Avant un combat important
   - Après une bonne configuration
   - À chaque palier de tours (5, 10, 15...)

3. **Nettoyage périodique** : Supprimez les anciennes sauvegardes
   - Gardez vos meilleures configurations
   - Supprimez les parties échouées

### Optimisation des statistiques

1. **Objectifs clairs** : Utilisez les stats pour fixer des objectifs
   - Améliorer votre taux de victoire
   - Atteindre un tour plus élevé
   - Maîtriser différents leaders

2. **Analyse des tendances** : Regardez vos parties récentes
   - Quels leaders vous réussissent le mieux ?
   - À quel tour échouez-vous souvent ?
   - Quels modificateurs vous conviennent ?

3. **Expérimentation** : Testez de nouvelles stratégies
   - Essayez différents leaders
   - Variez vos modificateurs
   - Adaptez selon vos statistiques

## 📱 Interface Mobile

Les nouvelles fonctionnalités sont **entièrement responsive** :

- **Modals adaptives** : S'ajustent à la taille de l'écran
- **Navigation tactile** : Boutons optimisés pour le touch
- **Formulaires mobiles** : Claviers appropriés sur mobile
- **Listes scrollables** : Navigation fluide sur petit écran

---

**🎯 Résumé** : Avec ces nouvelles fonctionnalités, vous pouvez maintenant créer un compte, sauvegarder vos parties favorites, et suivre votre progression dans Merge Tactics. Plus jamais de partie perdue !
