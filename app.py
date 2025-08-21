from flask import Flask, render_template, request, jsonify, session
from main import GameSession, BIBLIOTHEQUE_CARTES, MODIFICATEURS_PARTIE, BONUS_FAMILLES, Carte
import uuid
import json
import uuid
import json

app = Flask(__name__)
app.secret_key = 'clash_royale_merge_tactics_secret_key'

# Stockage des sessions de jeu
game_sessions = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    """Démarre une nouvelle partie"""
    session_id = str(uuid.uuid4())
    game_session = GameSession()
    game_sessions[session_id] = game_session
    
    session['game_id'] = session_id
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Nouvelle partie créée!'
    })

@app.route('/api/cards')
@app.route('/api/get_bibliotheque')
def get_bibliotheque():
    """Retourne la bibliothèque des cartes organisée par coût"""
    cartes_dict = {}
    for nom, carte in BIBLIOTHEQUE_CARTES.items():
        cartes_dict[nom] = {
            'nom': carte.nom,
            'cout_elixir': carte.cout,
            'famille': carte.traits[0] if carte.traits else 'Neutre',
            'traits': carte.traits,
            'niveau': carte.niveau
        }
    
    return jsonify({
        'success': True,
        'cards': cartes_dict
    })

@app.route('/api/modificateurs')
@app.route('/api/get_modificateurs')
def get_modificateurs():
    """Retourne la liste des modificateurs disponibles"""
    modificateurs_dict = {}
    for key, desc in MODIFICATEURS_PARTIE.items():
        modificateurs_dict[key] = {
            'nom': key.replace('_', ' ').title(),
            'description': desc
        }
    
    return jsonify({
        'success': True,
        'modificateurs': modificateurs_dict
    })

@app.route('/api/leaders')
def get_leaders():
    """Retourne la liste des leaders disponibles"""
    # Créer une session temporaire pour accéder aux leaders
    temp_session = GameSession()
    
    return jsonify({
        'success': True,
        'leaders': temp_session.leaders_disponibles
    })

@app.route('/api/new_game', methods=['POST'])
def new_game():
    """Créer une nouvelle session de jeu"""
    data = request.json
    session_id = str(uuid.uuid4())
    
    # Créer la session de jeu
    game_session = GameSession()
    game_session.choisir_mode()  # Configurer pour Merge Tactics
    
    # Configurer le leader choisi
    if 'leader' in data:
        leader_nom = data['leader']
        if leader_nom in game_session.leaders_disponibles:
            game_session.leader_choisi = game_session.leaders_disponibles[leader_nom]
    
    # Appliquer le modificateur sélectionné
    if 'modificateur' in data:
        game_session.modificateurs_actifs = [data['modificateur']]  # Un seul modificateur dans une liste
        game_session.appliquer_modificateurs()
    
    # Configurer la carte initiale
    if 'carte_initiale' in data:
        carte_nom = data['carte_initiale']
        niveau = data.get('niveau_initial', 1)
        
        if carte_nom in BIBLIOTHEQUE_CARTES:
            carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
            from main import Carte
            carte = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau)
            game_session.etat.main.append(carte)
            
            # Mise à jour historique
            game_session.etat.historique_pool[carte.nom] = 1
    
    # Configurer l'élixir initial
    if 'elixir_initial' in data:
        game_session.etat.elixir = data['elixir_initial']
    
    # Stocker la session
    game_sessions[session_id] = game_session
    session['game_id'] = session_id
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Nouvelle partie créée!'
    })

@app.route('/api/game_state/<session_id>')
def get_game_state_by_id(session_id):
    """Retourne l'état du jeu pour une session donnée"""
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    
    # Calculer la limite de cartes sur le plateau
    max_cartes_plateau = game_session.calculer_max_cartes_plateau()
    
    # Calculer les bonus de familles
    game_session.calculer_bonus_familles()
    
    # Compter les cartes par famille pour l'affichage
    # IMPORTANT: Dans Merge Tactics, deux cartes identiques (même nom) comptent comme 1 seule unité pour les bonus
    compteur_familles = {}
    toutes_cartes = game_session.etat.main + game_session.etat.bench
    
    # Grouper d'abord par nom de carte (peu importe le niveau)
    cartes_uniques = {}
    for carte in toutes_cartes:
        cartes_uniques[carte.nom] = carte  # Garde seulement une instance de chaque nom
    
    # Maintenant compter les familles basées sur les cartes uniques
    for nom_carte, carte in cartes_uniques.items():
        for trait in carte.traits:
            if trait not in compteur_familles:
                compteur_familles[trait] = 0
            compteur_familles[trait] += 1
    
    # Formater les cartes pour l'affichage
    plateau = []
    for carte in game_session.etat.main:
        plateau.append({
            'nom': carte.nom,
            'cout_elixir': carte.cout,
            'famille': carte.traits[0] if carte.traits else 'Neutre',
            'niveau': carte.niveau,
            'traits': carte.traits
        })
    
    banc = []
    for carte in game_session.etat.bench:
        banc.append({
            'nom': carte.nom,
            'cout_elixir': carte.cout,
            'famille': carte.traits[0] if carte.traits else 'Neutre',
            'niveau': carte.niveau,
            'traits': carte.traits
        })
    
    # Formater les bonus de familles
    bonus_familles = {}
    
    # Ajouter les familles actives
    for famille, niveau in game_session.bonus_familles_actifs.items():
        bonus_familles[famille] = {
            'niveau': niveau,
            'actif': True,
            'nombre': compteur_familles.get(famille, 0),
            'description': BONUS_FAMILLES[famille][niveau] if famille in BONUS_FAMILLES and niveau in BONUS_FAMILLES[famille] else "Bonus activé"
        }
    
    # Ajouter les familles inactives (qui ont des cartes mais pas assez pour le bonus)
    for famille, count in compteur_familles.items():
        if famille not in bonus_familles and famille in BONUS_FAMILLES:
            bonus_familles[famille] = {
                'niveau': 0,
                'actif': False,
                'nombre': count,
                'description': f"Nécessite {min(BONUS_FAMILLES[famille].keys())} cartes pour activation"
            }
    
    return jsonify({
        'success': True,
        'state': {
            'tour': game_session.tour,
            'elixir': game_session.etat.elixir,
            'hp': game_session.etat.hp,
            'plateau': plateau,
            'banc': banc,
            'bonus_familles': bonus_familles,
            'modificateurs_actifs': game_session.modificateurs_actifs,
            'leader': game_session.leader_choisi,
            'max_cartes_plateau': max_cartes_plateau,
            'game_over': game_session.etat.hp <= 0
        }
    })

@app.route('/api/recommendations', methods=['POST'])
def get_recommendations():
    """Calcule les recommandations pour les choix donnés"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    choix_data = data.get('choix', [])
    
    # Convertir en objets Carte
    options = []
    for choix in choix_data:
        if choix['carte'] in BIBLIOTHEQUE_CARTES:
            carte_base = BIBLIOTHEQUE_CARTES[choix['carte']]
            carte = Carte(carte_base.nom, carte_base.cout, carte_base.traits, choix['niveau'])
            options.append(carte)
    
    if not options:
        return jsonify({'success': False, 'error': 'Aucune option valide'})
    
    # Vérifier l'élixir disponible
    elixir_actuel = game_session.etat.elixir
    
    # Calculer les recommandations
    recommendations = []
    cartes_abordables = []
    cartes_cheres = []
    
    for i, carte in enumerate(options):
        # Score basé sur la logique existante
        score = game_session.score_familles(carte)
        score += (5 - carte.cout) * 0.5  # Préférer les cartes moins chères
        score += len([t for t in carte.traits if t in ['Ace', 'Noble']]) * 2  # Bonus pour certains traits
        
        peut_acheter = carte.cout <= elixir_actuel
        
        if peut_acheter:
            raison = f"Recommandé - Synergie: {score:.1f}"
            details = f"💰 Coût: {carte.cout} élixir | 🎯 Traits: {', '.join(carte.traits)}"
            recommendation_type = "achetable"
        else:
            elixir_manquant = carte.cout - elixir_actuel
            raison = f"Attendre {elixir_manquant} élixir de plus"
            details = f"💸 Coût: {carte.cout} élixir (manque {elixir_manquant}) | 🎯 Traits: {', '.join(carte.traits)}"
            recommendation_type = "trop_cher"
            score -= 10  # Pénalité pour les cartes inabordables
        
        recommendation = {
            'choix_numero': i + 1,
            'carte': carte.nom,
            'niveau': carte.niveau,
            'score': score,
            'raison': raison,
            'details': details,
            'peut_acheter': peut_acheter,
            'type': recommendation_type,
            'cout': carte.cout
        }
        
        if peut_acheter:
            cartes_abordables.append(recommendation)
        else:
            cartes_cheres.append(recommendation)
        
        recommendations.append(recommendation)
    
    # Trier par score
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    cartes_abordables.sort(key=lambda x: x['score'], reverse=True)
    cartes_cheres.sort(key=lambda x: x['score'], reverse=True)
    
    # Message d'aide selon la situation
    conseil_general = ""
    if not cartes_abordables:
        conseil_general = f"⏳ Pas assez d'élixir pour aucune carte. Passez le tour pour gagner {game_session.elixir_par_tour} élixir supplémentaire."
    elif len(cartes_abordables) < len(options):
        conseil_general = f"💡 {len(cartes_abordables)} cartes abordables maintenant, {len(cartes_cheres)} nécessitent plus d'élixir."
    
    return jsonify({
        'success': True,
        'recommendations': recommendations,
        'cartes_abordables': cartes_abordables,
        'cartes_cheres': cartes_cheres,
        'elixir_actuel': elixir_actuel,
        'conseil_general': conseil_general
    })

@app.route('/api/buy_card', methods=['POST'])
def buy_card():
    """Acheter une carte sans finir le tour"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    
    if not carte_nom or carte_nom not in BIBLIOTHEQUE_CARTES:
        return jsonify({'success': False, 'error': 'Carte non trouvée'})
    
    carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
    carte = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau)
    
    # Vérifier si on peut se permettre la carte
    if carte.cout > game_session.etat.elixir:
        return jsonify({'success': False, 'error': 'Pas assez d\'élixir'})
    
    # Déduire l'élixir immédiatement
    game_session.etat.elixir -= carte.cout
    
    # Ajouter la carte au banc d'abord
    game_session.etat.bench.append(carte)
    
    # LOGIQUE DE FUSION AMÉLIORÉE ET SÉCURISÉE
    fusion_effectuee = False
    fusions_totales = 0
    elixir_gagne = 0
    message_fusion = ""
    
    def effectuer_fusions_recursives():
        """Effectue toutes les fusions possibles de manière sécurisée"""
        nonlocal fusion_effectuee, fusions_totales, elixir_gagne, message_fusion
        
        max_iterations = 10  # Limite de sécurité pour éviter les boucles infinies
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            fusion_trouvee = False
            
            # Compter les cartes par nom et niveau dans le banc SEULEMENT
            compteur_cartes = {}
            for carte in game_session.etat.bench[:]:  # Copie de la liste pour éviter les modifications en cours
                key = f"{carte.nom}_{carte.niveau}"
                if key not in compteur_cartes:
                    compteur_cartes[key] = []
                compteur_cartes[key].append(carte)
            
            # Chercher une fusion possible (3+ cartes identiques)
            for key, cartes_groupe in compteur_cartes.items():
                if len(cartes_groupe) >= 3:
                    # Prendre les 3 premières cartes identiques
                    cartes_a_fusionner = cartes_groupe[:3]
                    nom_carte = cartes_a_fusionner[0].nom
                    niveau_carte = cartes_a_fusionner[0].niveau
                    cout_carte = cartes_a_fusionner[0].cout
                    traits_carte = cartes_a_fusionner[0].traits.copy()
                    
                    # Vérifier qu'on peut fusionner (niveau < 5)
                    if niveau_carte >= 5:
                        continue
                    
                    # Retirer exactement ces 3 cartes du banc
                    for carte_a_retirer in cartes_a_fusionner:
                        if carte_a_retirer in game_session.etat.bench:
                            game_session.etat.bench.remove(carte_a_retirer)
                    
                    # Créer la carte fusionnée (niveau +1)
                    carte_fusionnee = Carte(nom_carte, cout_carte, traits_carte, niveau_carte + 1)
                    game_session.etat.bench.append(carte_fusionnee)
                    
                    # Marquer la fusion
                    fusion_effectuee = True
                    fusion_trouvee = True
                    fusions_totales += 1
                    elixir_gagne += 1
                    
                    if fusions_totales == 1:
                        message_fusion = f" → Fusion {nom_carte} niv.{niveau_carte + 1}!"
                    else:
                        message_fusion += f" → {nom_carte} niv.{niveau_carte + 1}!"
                    
                    break  # Une seule fusion par itération pour la stabilité
            
            # Si aucune fusion trouvée, arrêter
            if not fusion_trouvee:
                break
    
    # Effectuer les fusions
    effectuer_fusions_recursives()
    
    # Ajouter l'élixir gagné des fusions
    game_session.etat.elixir += elixir_gagne
    
    # Appliquer bonus du leader pour fusion
    if fusion_effectuee and game_session.leader_choisi:
        bonus_elixir = game_session.appliquer_bonus_leader("merge", f"({carte.nom} fusionné {fusions_totales} fois)")
        if bonus_elixir > 0:
            game_session.etat.elixir += bonus_elixir
            elixir_gagne += bonus_elixir
            message_fusion += f" +{bonus_elixir} élixir (Leader)"
    
    if fusion_effectuee:
        message_fusion += f" +{elixir_gagne} élixir total"
    
    # Mise à jour historique
    if carte.nom in game_session.etat.historique_pool:
        game_session.etat.historique_pool[carte.nom] += 1
    else:
        game_session.etat.historique_pool[carte.nom] = 1
    
    return jsonify({
        'success': True,
        'message': f'{carte_nom} niveau {niveau} acheté{message_fusion}',
        'elixir_restant': game_session.etat.elixir,
        'fusion_effectuee': fusion_effectuee,
        'fusions_totales': fusions_totales,
        'elixir_gagne': elixir_gagne
    })

@app.route('/api/manual_merge', methods=['POST'])
def manual_merge():
    """Fusionner manuellement des cartes identiques dans le banc"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    
    # Vérifier qu'il y a au moins 3 cartes identiques dans le banc
    cartes_identiques = [c for c in game_session.etat.bench if c.nom == carte_nom and c.niveau == niveau]
    
    if len(cartes_identiques) < 3:
        return jsonify({'success': False, 'error': f'Pas assez de cartes identiques pour fusionner (besoin de 3, trouvé {len(cartes_identiques)})'})
    
    if niveau >= 5:
        return jsonify({'success': False, 'error': 'Impossible de fusionner au-delà du niveau 5'})
    
    # Supprimer exactement 3 cartes identiques du banc
    cartes_supprimees = 0
    for i in range(len(game_session.etat.bench) - 1, -1, -1):
        if cartes_supprimees >= 3:
            break
        if game_session.etat.bench[i].nom == carte_nom and game_session.etat.bench[i].niveau == niveau:
            game_session.etat.bench.pop(i)
            cartes_supprimees += 1
    
    # Créer la carte fusionnée
    carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
    carte_fusionnee = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau + 1)
    game_session.etat.bench.append(carte_fusionnee)
    
    # Gain d'élixir pour fusion
    elixir_gagne = 1
    game_session.etat.elixir += elixir_gagne
    
    # Appliquer bonus du leader
    if game_session.leader_choisi:
        bonus_elixir = game_session.appliquer_bonus_leader("merge", f"({carte_nom} fusionné manuellement)")
        if bonus_elixir > 0:
            game_session.etat.elixir += bonus_elixir
            elixir_gagne += bonus_elixir
    
    message = f"Fusion réussie ! 3x {carte_nom} niv.{niveau} → 1x {carte_nom} niv.{niveau + 1} (+{elixir_gagne} élixir)"
    
    # Effectuer les fusions récursives supplémentaires de manière sécurisée
    fusions_recursives = 0
    
    def effectuer_fusions_post_manuelle():
        nonlocal fusions_recursives, elixir_gagne
        
        max_iterations = 10  # Limite de sécurité
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            fusion_trouvee = False
            
            # Compter les cartes par nom et niveau dans le banc SEULEMENT
            compteur_cartes = {}
            for carte in game_session.etat.bench[:]:  # Copie pour éviter modifications en cours
                key = f"{carte.nom}_{carte.niveau}"
                if key not in compteur_cartes:
                    compteur_cartes[key] = []
                compteur_cartes[key].append(carte)
            
            # Chercher une fusion possible (3+ cartes identiques)
            for key, cartes_groupe in compteur_cartes.items():
                if len(cartes_groupe) >= 3:
                    # Prendre les 3 premières cartes identiques
                    cartes_a_fusionner = cartes_groupe[:3]
                    nom_carte = cartes_a_fusionner[0].nom
                    niveau_carte = cartes_a_fusionner[0].niveau
                    cout_carte = cartes_a_fusionner[0].cout
                    traits_carte = cartes_a_fusionner[0].traits.copy()
                    
                    # Vérifier qu'on peut fusionner (niveau < 5)
                    if niveau_carte >= 5:
                        continue
                    
                    # Retirer exactement ces 3 cartes du banc
                    for carte_a_retirer in cartes_a_fusionner:
                        if carte_a_retirer in game_session.etat.bench:
                            game_session.etat.bench.remove(carte_a_retirer)
                    
                    # Créer la carte fusionnée (niveau +1)
                    carte_fusionnee_auto = Carte(nom_carte, cout_carte, traits_carte, niveau_carte + 1)
                    game_session.etat.bench.append(carte_fusionnee_auto)
                    
                    # Marquer la fusion
                    fusion_trouvee = True
                    fusions_recursives += 1
                    elixir_gagne += 1
                    game_session.etat.elixir += 1
                    
                    break  # Une seule fusion par itération
            
            # Si aucune fusion trouvée, arrêter
            if not fusion_trouvee:
                break
    
    # Effectuer les fusions automatiques supplémentaires
    effectuer_fusions_post_manuelle()
    
    if fusions_recursives > 0:
        message += f" + {fusions_recursives} fusion(s) automatique(s)!"
    
    return jsonify({
        'success': True,
        'message': message,
        'elixir_gagne': elixir_gagne,
        'fusions_totales': 1 + fusions_recursives,
        'elixir_restant': game_session.etat.elixir
    })

@app.route('/api/delete_card', methods=['POST'])
def delete_card():
    """Supprimer une carte pour récupérer de l'élixir (prix de la carte - 1)"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    location = data.get('location', 'banc')  # 'banc' ou 'plateau'
    
    carte_trouvee = None
    
    # Chercher dans le banc ou plateau selon location
    if location == 'banc':
        for i, carte in enumerate(game_session.etat.bench):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.bench.pop(i)
                break
    else:  # plateau
        for i, carte in enumerate(game_session.etat.main):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.main.pop(i)
                break
    
    if not carte_trouvee:
        return jsonify({'success': False, 'error': 'Carte non trouvée'})
    
    # Récupérer l'élixir : prix de la carte - 1 (minimum 1)
    elixir_recupere = max(1, carte_trouvee.cout - 1)
    game_session.etat.elixir += elixir_recupere
    
    message = f'{carte_nom} niveau {niveau} supprimé pour {elixir_recupere} élixir'
    
    return jsonify({
        'success': True,
        'message': message,
        'elixir_restant': game_session.etat.elixir,
        'elixir_recupere': elixir_recupere
    })

@app.route('/api/move_card', methods=['POST'])
def move_card():
    """Déplacer une carte entre banc et plateau (drag and drop)"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    from_location = data.get('from')  # 'banc' ou 'plateau'
    to_location = data.get('to')      # 'banc' ou 'plateau'
    
    if from_location == to_location:
        return jsonify({'success': False, 'error': 'Impossible de déplacer vers la même zone'})
    
    carte_trouvee = None
    
    # Chercher et retirer de la source
    if from_location == 'banc':
        for i, carte in enumerate(game_session.etat.bench):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.bench.pop(i)
                break
    else:  # plateau
        for i, carte in enumerate(game_session.etat.main):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.main.pop(i)
                break
    
    if not carte_trouvee:
        return jsonify({'success': False, 'error': 'Carte non trouvée'})
    
    # Vérifier les limites avant d'ajouter à la destination
    max_cartes_plateau = game_session.calculer_max_cartes_plateau()
    
    if to_location == 'plateau' and len(game_session.etat.main) >= max_cartes_plateau:
        # Remettre la carte à sa place d'origine
        if from_location == 'banc':
            game_session.etat.bench.append(carte_trouvee)
        else:
            game_session.etat.main.append(carte_trouvee)
        return jsonify({'success': False, 'error': f'Plateau plein (max {max_cartes_plateau} cartes)'})
    
    # Ajouter à la destination
    if to_location == 'banc':
        game_session.etat.bench.append(carte_trouvee)
        message = f'{carte_nom} niveau {niveau} déplacé vers le banc'
    else:  # plateau
        game_session.etat.main.append(carte_trouvee)
        message = f'{carte_nom} niveau {niveau} déplacé vers le plateau'
    
    return jsonify({
        'success': True,
        'message': message
    })

@app.route('/api/sell_card', methods=['POST'])
def sell_card():
    """Vendre une carte (déclenche le bonus du Roi Royal)"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    location = data.get('location', 'banc')  # 'banc' ou 'plateau'
    
    carte_trouvee = None
    
    # Chercher dans le banc ou plateau selon location
    if location == 'banc':
        for i, carte in enumerate(game_session.etat.bench):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.bench.pop(i)
                break
    else:  # plateau
        for i, carte in enumerate(game_session.etat.main):
            if carte.nom == carte_nom and carte.niveau == niveau:
                carte_trouvee = game_session.etat.main.pop(i)
                break
    
    if not carte_trouvee:
        return jsonify({'success': False, 'error': 'Carte non trouvée'})
    
    # Élixir de base pour la vente (généralement 1 élixir)
    elixir_vente = max(1, carte_trouvee.cout // 2)
    game_session.etat.elixir += elixir_vente
    
    message = f'{carte_nom} niveau {niveau} vendu pour {elixir_vente} élixir'
    
    # Appliquer bonus du leader pour défaite/vente
    bonus_elixir = game_session.appliquer_bonus_leader("defeat", f"({carte_nom} vendu)")
    if bonus_elixir > 0:
        message += f" +{bonus_elixir} élixir (Leader)"
    
    return jsonify({
        'success': True,
        'message': message,
        'elixir_restant': game_session.etat.elixir
    })

@app.route('/api/make_choice', methods=['POST'])
def make_choice():
    """Valider un choix et avancer le jeu (ancien endpoint conservé pour compatibilité)"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    
    questions = []
    
    if carte_nom and carte_nom in BIBLIOTHEQUE_CARTES:
        carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
        from main import Carte
        carte = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau)
        
        # Vérifier si on peut se permettre la carte
        if carte.cout <= game_session.etat.elixir:
            # Ajouter la carte
            game_session.etat.main.append(carte)
            game_session.etat.elixir -= carte.cout
            
            # Mise à jour historique
            if carte.nom in game_session.etat.historique_pool:
                game_session.etat.historique_pool[carte.nom] += 1
            else:
                game_session.etat.historique_pool[carte.nom] = 1
        else:
            return jsonify({'success': False, 'error': 'Pas assez d\'élixir'})
    
    # Avancer le tour
    game_session.tour += 1
    
    # Ajouter l'élixir du tour suivant
    game_session.etat.elixir += game_session.elixir_par_tour
    
    # Générer questions post-tour
    questions = game_session.poser_question_modificateur("post_tour")
    
    return jsonify({
        'success': True,
        'questions': questions,
        'message': f'{carte_nom} niveau {niveau} ajouté !' if carte_nom else 'Tour passé'
    })

@app.route('/api/battle_result', methods=['POST'])
def battle_result():
    """Enregistrer le résultat d'une bataille (victoire ou défaite)"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    victoire = data.get('victoire', False)  # True pour victoire, False pour défaite
    troupes_adverses_restantes = data.get('troupes_adverses_restantes', 0)  # Nombre de troupes adverses restantes
    
    # Gérer le résultat de la bataille
    resultat = game_session.gerer_resultat_bataille(victoire, troupes_adverses_restantes)
    
    return jsonify({
        'success': True,
        'elixir_gagne': resultat['elixir_gagne'],
        'hp_perdus': resultat['hp_perdus'],
        'message': resultat['message'],
        'victoire': resultat['victoire'],
        'game_over': resultat['game_over'],
        'hp_restants': resultat['hp_restants'],
        'tour': resultat['tour'],
        'elixir_total': game_session.etat.elixir
    })

@app.route('/api/move_to_field', methods=['POST'])
def move_to_field():
    """Déplacer une carte du banc vers le plateau"""
    data = request.json
    session_id = data.get('session_id')
    
    if session_id not in game_sessions:
        return jsonify({'success': False, 'error': 'Session non trouvée'})
    
    game_session = game_sessions[session_id]
    carte_nom = data.get('carte')
    niveau = data.get('niveau', 1)
    
    if not carte_nom:
        return jsonify({'success': False, 'error': 'Carte non spécifiée'})
    
    # Calculer la limite de cartes sur le plateau
    max_cartes_plateau = game_session.calculer_max_cartes_plateau()
    
    # Chercher la carte dans le banc
    carte_trouvee = None
    for i, carte in enumerate(game_session.etat.bench):
        if carte.nom == carte_nom and carte.niveau == niveau:
            carte_trouvee = game_session.etat.bench.pop(i)
            break
    
    if not carte_trouvee:
        return jsonify({'success': False, 'error': 'Carte non trouvée dans le banc'})
    
    # Vérifier s'il y a possibilité de fusion avant de vérifier la limite
    cartes_identiques_plateau = [c for c in game_session.etat.main if c.nom == carte_nom and c.niveau == niveau]
    
    # Vérifier la limite du plateau seulement si pas de fusion possible
    if len(game_session.etat.main) >= max_cartes_plateau and len(cartes_identiques_plateau) == 0:
        # Remettre la carte dans le banc
        game_session.etat.bench.append(carte_trouvee)
        return jsonify({
            'success': False, 
            'error': f'Plateau plein ! Limite : {max_cartes_plateau} cartes (Tour {game_session.tour})'
        })
    
    # Vérifier s'il y a des fusions possibles sur le plateau
    fusion_effectuee = False
    elixir_gagne = 0
    message = f'{carte_nom} niveau {niveau} déplacé vers le plateau !'
    
    # Vérifier d'abord s'il y a déjà des cartes identiques sur le plateau (AVANT d'ajouter)
    cartes_identiques_plateau = [c for c in game_session.etat.main if c.nom == carte_nom and c.niveau == niveau]
    
    if len(cartes_identiques_plateau) >= 2:
        # Fusion avec 3 cartes (2 sur plateau + 1 du banc)
        # Retirer 2 cartes du plateau
        for _ in range(2):
            for i, c in enumerate(game_session.etat.main):
                if c.nom == carte_nom and c.niveau == niveau:
                    game_session.etat.main.pop(i)
                    break
        
        # La carte du banc + les 2 du plateau = fusion
        # Créer la carte fusionnée
        from main import Carte
        carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
        carte_fusionnee = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau + 1)
        game_session.etat.main.append(carte_fusionnee)
        
        fusion_effectuee = True
        
        # Gain de base pour fusion : +1 élixir
        game_session.etat.elixir += 1
        elixir_gagne = 1
        message = f'{carte_nom} niveau {niveau} fusionné avec le plateau → niveau {niveau + 1}! +1 élixir'
        
        # Appliquer bonus du leader pour fusion
        bonus_elixir = game_session.appliquer_bonus_leader("merge", f"({carte_nom} fusionné)")
        if bonus_elixir > 0:
            elixir_gagne += bonus_elixir
            message += f" +{bonus_elixir} élixir (Leader)"
            
    elif len(cartes_identiques_plateau) == 1:
        # Fusion avec 2 cartes (1 sur plateau + 1 du banc)
        # Retirer 1 carte du plateau
        for i, c in enumerate(game_session.etat.main):
            if c.nom == carte_nom and c.niveau == niveau:
                game_session.etat.main.pop(i)
                break
        
        # La carte du banc + celle du plateau = fusion
        # Créer la carte fusionnée
        from main import Carte
        carte_base = BIBLIOTHEQUE_CARTES[carte_nom]
        carte_fusionnee = Carte(carte_base.nom, carte_base.cout, carte_base.traits, niveau + 1)
        game_session.etat.main.append(carte_fusionnee)
        
        fusion_effectuee = True
        
        # Gain de base pour fusion : +1 élixir
        game_session.etat.elixir += 1
        elixir_gagne = 1
        message = f'{carte_nom} niveau {niveau} fusionné avec le plateau → niveau {niveau + 1}! +1 élixir'
        
        # Appliquer bonus du leader pour fusion
        bonus_elixir = game_session.appliquer_bonus_leader("merge", f"({carte_nom} fusionné)")
        if bonus_elixir > 0:
            elixir_gagne += bonus_elixir
            message += f" +{bonus_elixir} élixir (Leader)"
    else:
        # Pas de fusion, simplement ajouter la carte au plateau
        game_session.etat.main.append(carte_trouvee)
    
    return jsonify({
        'success': True,
        'message': message,
        'fusion_effectuee': fusion_effectuee,
        'elixir_gagne': elixir_gagne
    })

if __name__ == '__main__':
    print("🏰 Lancement du serveur Clash Royale Merge Tactics Assistant...")
    print("📱 Ouvrez votre navigateur sur : http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)