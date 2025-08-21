// État global de l'application
let gameState = {
    isConfigured: false,
    currentStep: 1,
    selectedModificateur: null, // Un seul modificateur au lieu d'un tableau
    selectedLeader: null,
    currentChoices: [],
    selectedChoice: null,
    session: null
};

// Stockage des cartes pour accès global
let cardsData = {};

// Configuration initiale
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialisation de l'application
function initializeApp() {
    loadModificateurs();
    loadLeaders();
    loadCardOptions();
    showStep(1);
}

// Navigation entre les étapes de configuration
function showStep(stepNumber) {
    // Masquer toutes les étapes
    document.querySelectorAll('.config-step').forEach(step => {
        step.classList.remove('active');
    });
    
    // Afficher l'étape demandée
    const targetStep = document.getElementById(`step-${stepNumber}`);
    if (targetStep) {
        targetStep.classList.add('active');
        gameState.currentStep = stepNumber;
    }
}

// Démarrer le jeu
function startGame() {
    showStep(2);
}

// Charger les modificateurs
async function loadModificateurs() {
    try {
        const response = await fetch('/api/modificateurs');
        const data = await response.json();
        
        if (data.success) {
            displayModificateurs(data.modificateurs);
        } else {
            console.error('Erreur lors du chargement des modificateurs:', data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
    }
}

// Afficher les modificateurs
function displayModificateurs(modificateurs) {
    const container = document.getElementById('modificateurs-list');
    container.innerHTML = '';
    
    Object.entries(modificateurs).forEach(([key, mod]) => {
        const modCard = document.createElement('div');
        modCard.className = 'modificateur-card';
        modCard.setAttribute('data-modificateur', key); // Utiliser data-modificateur au lieu de dataset.key
        modCard.innerHTML = `
            <h4>${mod.nom}</h4>
            <p>${mod.description}</p>
        `;
        
        modCard.addEventListener('click', () => toggleModificateur(key, modCard));
        container.appendChild(modCard);
    });
}

// Basculer la sélection d'un modificateur
function toggleModificateur(key, element) {
    // Désélectionner le modificateur actuellement sélectionné
    if (gameState.selectedModificateur) {
        const prevSelected = document.querySelector(`[data-modificateur="${gameState.selectedModificateur}"]`);
        if (prevSelected) {
            prevSelected.classList.remove('selected');
        }
    }
    
    // Si on clique sur le même modificateur, le désélectionner
    if (gameState.selectedModificateur === key) {
        gameState.selectedModificateur = null;
    } else {
        // Sélectionner le nouveau modificateur
        gameState.selectedModificateur = key;
        element.classList.add('selected');
    }
}

// Sélection automatique des modificateurs
function selectAutoModificateurs() {
    // Sélectionner aléatoirement 1 modificateur
    const allModificateurs = Array.from(document.querySelectorAll('.modificateur-card'));
    
    // Réinitialiser la sélection
    gameState.selectedModificateur = null;
    allModificateurs.forEach(card => card.classList.remove('selected'));
    
    // Sélectionner aléatoirement 1 modificateur
    if (allModificateurs.length > 0) {
        const randomIndex = Math.floor(Math.random() * allModificateurs.length);
        const selectedCard = allModificateurs[randomIndex];
        const key = selectedCard.getAttribute('data-modificateur');
        
        gameState.selectedModificateur = key;
        selectedCard.classList.add('selected');
    }
}

// Appliquer les modificateurs sélectionnés
function applyModificateurs() {
    if (!gameState.selectedModificateur) {
        alert('Veuillez sélectionner un modificateur.');
        return;
    }
    
    showStep(4);
}

// Charger les leaders
async function loadLeaders() {
    try {
        const response = await fetch('/api/leaders');
        const data = await response.json();
        
        if (data.success) {
            displayLeaders(data.leaders);
        } else {
            console.error('Erreur lors du chargement des leaders:', data.error);
        }
    } catch (error) {
        console.error('Erreur réseau lors du chargement des leaders:', error);
    }
}

// Afficher les leaders
function displayLeaders(leaders) {
    const container = document.getElementById('leaders-list');
    container.innerHTML = '';
    
    Object.entries(leaders).forEach(([key, leader]) => {
        const leaderCard = document.createElement('div');
        leaderCard.className = 'leader-card';
        leaderCard.dataset.key = key;
        leaderCard.onclick = () => selectLeader(key, leaderCard);
        
        leaderCard.innerHTML = `
            <div class="leader-icon">${leader.icone}</div>
            <h4>${leader.nom}</h4>
            <p>${leader.description}</p>
            <div class="leader-bonus">
                ${leader.bonus_merge > 0 ? `🔥 +${leader.bonus_merge} élixir par fusion` : ''}
                ${leader.bonus_defeat > 0 ? `💪 +${leader.bonus_defeat} élixir par défaite` : ''}
            </div>
        `;
        
        container.appendChild(leaderCard);
    });
}

// Sélectionner un leader
function selectLeader(key, element) {
    // Désélectionner tous les leaders
    document.querySelectorAll('.leader-card').forEach(card => {
        card.classList.remove('selected');
    });
    
    // Sélectionner le leader cliqué
    element.classList.add('selected');
    gameState.selectedLeader = key;
}

// Valider le choix du leader
function applyLeaderChoice() {
    if (!gameState.selectedLeader) {
        alert('Veuillez sélectionner un leader.');
        return;
    }
    
    showStep(3);
}

// Charger les options de cartes
async function loadCardOptions() {
    try {
        const response = await fetch('/api/cards');
        const data = await response.json();
        
        if (data.success) {
            displayCardOptions(data.cards);
        } else {
            console.error('Erreur lors du chargement des cartes:', data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
    }
}

// Afficher les options de cartes dans les selects
function displayCardOptions(cards) {
    // Stocker les cartes pour accès global
    cardsData = cards;
    
    const selects = document.querySelectorAll('.card-select');
    
    selects.forEach(select => {
        select.innerHTML = '<option value="">Choisir une carte...</option>';
        
        Object.entries(cards).forEach(([key, card]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `${card.nom} (${card.cout_elixir}⚡ - ${card.famille})`;
            select.appendChild(option);
        });
    });
    
    // Initialiser les cartes rapides après le chargement
    if (document.getElementById('quick-cards-grid')) {
        generateQuickCards();
    }
}

// Appliquer la configuration initiale
async function applyInitialConfig() {
    const initialCard = document.getElementById('initial-card').value;
    const initialLevel = parseInt(document.getElementById('initial-level').value) || 1;
    const initialElixir = parseInt(document.getElementById('initial-elixir').value) || 4;
    
    if (!initialCard) {
        alert('Veuillez sélectionner une carte de départ.');
        return;
    }
    
    // Créer une nouvelle session
    try {
        const response = await fetch('/api/new_game', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                modificateur: gameState.selectedModificateur, // Un seul modificateur au lieu d'un tableau
                leader: gameState.selectedLeader,
                carte_initiale: initialCard,
                niveau_initial: initialLevel,
                elixir_initial: initialElixir
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            gameState.session = data.session_id;
            gameState.isConfigured = true;
            showGameInterface();
            updateGameDisplay();
        } else {
            alert('Erreur lors de la création de la partie: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        alert('Erreur de connexion au serveur.');
    }
}

// Afficher l'interface de jeu
function showGameInterface() {
    document.getElementById('config-panel').style.display = 'none';
    document.getElementById('game-interface').style.display = 'grid';
    
    // Afficher les game-stats dans le header
    const gameStats = document.getElementById('game-stats');
    if (gameStats) {
        gameStats.style.display = 'flex';
    }
    
    // Configurer les zones de drop pour le drag and drop
    setupDropZones();
    
    // Initialiser le mode achat rapide
    initializeQuickBuy();
}

// === SYSTÈME D'ACHAT RAPIDE ===
// Initialiser le mode achat rapide
function initializeQuickBuy() {
    generateQuickCards();
}

// Générer les cartes communes pour l'achat rapide - VERSION SIMPLIFIÉE
function generateQuickCards() {
    if (!cardsData || Object.keys(cardsData).length === 0) {
        setTimeout(generateQuickCards, 500);
        return;
    }
    
    const container = document.getElementById('quick-cards-grid');
    container.innerHTML = '';
    
    // Sélectionner SEULEMENT 4 cartes les plus populaires (2x2 grid)
    const popularCards = [
        'Chevalier',    // Coût 2, Noble/Colosse
        'Gobelins',     // Coût 2, Gobelin/Assassin  
        'Prince',       // Coût 3, Noble/Bagarreur
        'P.E.K.K.A'         // Coût 3, Ace/Colosse
    ];
    
    popularCards.forEach(cardName => {
        const cardData = cardsData[cardName];
        if (cardData) {
            const quickCard = createQuickCard(cardName, cardData);
            container.appendChild(quickCard);
        }
    });
}

// Créer une carte rapide - VERSION SIMPLIFIÉE
function createQuickCard(cardKey, cardData) {
    const currentElixir = parseInt(document.getElementById('elixir-count')?.textContent) || 0;
    const canAfford = cardData.cout_elixir <= currentElixir;
    
    const cardDiv = document.createElement('div');
    cardDiv.className = `quick-card ${canAfford ? 'affordable' : 'expensive'}`;
    cardDiv.dataset.cardKey = cardKey;
    cardDiv.dataset.selectedLevel = '1';
    
    cardDiv.innerHTML = `
        <div class="quick-card-header">
            <div class="quick-card-name">${cardData.nom}</div>
            <div class="quick-card-cost">${cardData.cout_elixir}⚡</div>
        </div>
        
        <div class="quick-card-level">
            ${[1, 2, 3].map(level => `
                <button class="level-btn ${level === 1 ? 'selected' : ''}" 
                        onclick="selectQuickLevel('${cardKey}', ${level})">${level}</button>
            `).join('')}
        </div>
        
        <button class="quick-buy-btn" 
                onclick="quickBuyCard('${cardKey}')" 
                ${!canAfford ? 'disabled' : ''}>
            ${canAfford ? 'Acheter' : 'Trop cher'}
        </button>
    `;
    
    return cardDiv;
}

// Sélectionner le niveau pour l'achat rapide
function selectQuickLevel(cardKey, level) {
    const cardElement = document.querySelector(`[data-card-key="${cardKey}"]`);
    if (!cardElement) return;
    
    // Mettre à jour le niveau sélectionné
    cardElement.dataset.selectedLevel = level;
    
    // Mettre à jour l'affichage des boutons de niveau
    const levelBtns = cardElement.querySelectorAll('.level-btn');
    levelBtns.forEach((btn, index) => {
        if (index + 1 === level) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });
}

// Achat rapide d'une carte
async function quickBuyCard(cardKey) {
    if (!gameState.session) {
        showNotification('Session de jeu non initialisée.', 'error');
        return;
    }
    
    const cardElement = document.querySelector(`[data-card-key="${cardKey}"]`);
    const level = parseInt(cardElement.dataset.selectedLevel) || 1;
    
    try {
        const response = await fetch('/api/buy_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: cardKey,
                niveau: level
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Message d'achat avec informations de fusion
            let notificationMessage = `✅ ${cardKey} niveau ${level} acheté !`;
            let notificationType = 'success';
            
            if (data.fusion_effectuee) {
                notificationMessage = `🎆 ${data.message}`;
                notificationType = 'success';
                
                // Animation d'élixir pour les fusions
                if (data.elixir_gagne > 0) {
                    animateElixirGain(data.elixir_gagne);
                }
                
                // Animation spéciale pour plusieurs fusions
                if (data.fusions_totales > 1) {
                    showNotification(`🔥 ${data.fusions_totales} fusions en cascade !`, 'success');
                }
            }
            
            showNotification(notificationMessage, notificationType);
            
            // Actualiser l'état du jeu
            await updateGameDisplay();
            
            // Regenerer les cartes rapides avec le nouvel élixir
            setTimeout(generateQuickCards, 500);
            
        } else {
            showNotification(data.error || 'Erreur lors de l\'achat', 'error');
        }
    } catch (error) {
        console.error('Erreur achat rapide:', error);
        showNotification('Erreur de connexion', 'error');
    }
}

// Actualiser les cartes rapides
function refreshQuickCards() {
    generateQuickCards();
    showNotification('Cartes actualisées !', 'info');
}

// Basculer entre mode rapide et avancé
function toggleAdvancedMode() {
    const advancedSection = document.getElementById('advanced-choices');
    const isVisible = advancedSection.style.display !== 'none';
    
    if (isVisible) {
        advancedSection.style.display = 'none';
        showNotification('Mode rapide activé', 'info');
    } else {
        advancedSection.style.display = 'block';
        showNotification('Mode avancé activé', 'info');
    }
}

// Configurer les zones de drop pour le drag and drop
function setupDropZones() {
    const benchZone = document.getElementById('bench-cards');
    const plateauZone = document.getElementById('plateau-cards');
    
    [benchZone, plateauZone].forEach(zone => {
        if (zone) {
            zone.addEventListener('dragover', handleDragOver);
            zone.addEventListener('dragleave', handleDragLeave);
            zone.addEventListener('drop', handleDrop);
            zone.classList.add('drop-zone');
        }
    });
}

// Mettre à jour l'affichage du jeu
async function updateGameDisplay() {
    if (!gameState.session) return;
    
    try {
        const response = await fetch(`/api/game_state/${gameState.session}`);
        const data = await response.json();
        
        if (data.success) {
            const state = data.state;
            
            // Mettre à jour les compteurs
            document.getElementById('elixir-count').textContent = state.elixir;
            document.getElementById('tour-count').textContent = state.tour;
            
            // Mettre à jour les stats HP et Élixir
            if (document.getElementById('elixir-display')) {
                document.getElementById('elixir-display').textContent = state.elixir;
            }
            if (document.getElementById('hp-display')) {
                document.getElementById('hp-display').textContent = state.hp;
            }
            
            // Vérifier si le jeu est terminé
            if (state.game_over) {
                showGameOver();
                return;
            }
            
            // Mettre à jour le compteur de cartes plateau
            const cartesPlateauCount = state.plateau.length;
            const maxCartesPlateauLimit = state.max_cartes_plateau || 2;
            document.getElementById('cartes-plateau-count').textContent = cartesPlateauCount;
            document.getElementById('max-cartes-plateau').textContent = maxCartesPlateauLimit;
            
            // Ajouter classe d'alerte si proche de la limite
            const plateauLimitCounter = document.querySelector('.plateau-limit-counter');
            plateauLimitCounter.classList.remove('warning', 'full');
            if (cartesPlateauCount >= maxCartesPlateauLimit) {
                plateauLimitCounter.classList.add('full');
            } else if (cartesPlateauCount >= maxCartesPlateauLimit - 1) {
                plateauLimitCounter.classList.add('warning');
            }
            
            // Mettre à jour le leader
            displayLeaderInfo(state.leader);
            
            // Mettre à jour le plateau
            displayCards('plateau-cards', state.plateau);
            
            // Mettre à jour le banc
            displayCards('bench-cards', state.banc);
            
            // Mettre à jour les bonus
            displayBonusFamilles(state.bonus_familles);
            
            // Mettre à jour le plateau hexagonal
            updateGameBoardDisplay(state);
            
        } else {
            console.error('Erreur lors de la récupération de l\'état:', data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
    }
}

// Afficher les informations du leader
function displayLeaderInfo(leader) {
    const container = document.getElementById('leader-info');
    
    if (!leader) {
        container.innerHTML = '<p>Aucun leader sélectionné</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="leader-display-card">
            <div class="leader-icon-big">${leader.icone}</div>
            <div class="leader-details">
                <h4>${leader.nom}</h4>
                <p>${leader.description}</p>
                <div class="leader-bonus-info">
                    ${leader.bonus_merge > 0 ? `<span class="bonus-merge">🔥 +${leader.bonus_merge} élixir/fusion</span>` : ''}
                    ${leader.bonus_defeat > 0 ? `<span class="bonus-defeat">💪 +${leader.bonus_defeat} élixir/défaite</span>` : ''}
                </div>
                ${leader.bonus_defeat > 0 ? `<div class="leader-tip">💡 Astuce: Utilisez les boutons Victoire/Défaite pour activer les bonus !</div>` : ''}
            </div>
        </div>
    `;
}

// Afficher les cartes sans fusion automatique côté client
function displayCards(containerId, cards) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    // Compter les occurrences de chaque carte pour déterminer les fusions possibles
    const cardCounts = {};
    cards.forEach(card => {
        const key = `${card.nom}_${card.niveau}`;
        cardCounts[key] = (cardCounts[key] || 0) + 1;
    });
    
    // Afficher chaque carte individuellement sans fusion côté client
    cards.forEach(card => {
        const cardElement = document.createElement('div');
        cardElement.className = `card-item elixir-${card.cout_elixir}`;
        
        // Afficher toutes les familles/traits
        const famillesHtml = card.traits ? card.traits.map(trait => 
            `<span class="family-trait family-${trait}">${getFamilyIcon(trait)}</span>`
        ).join('') : `<span class="family-trait">${getFamilyIcon('Neutre')}</span>`;
        
        // Vérifier si on peut fusionner cette carte (3+ cartes identiques dans le banc)
        const cardKey = `${card.nom}_${card.niveau}`;
        const canMerge = containerId === 'bench-cards' && cardCounts[cardKey] >= 3;
        
        cardElement.innerHTML = `
            <div class="card-families">
                ${famillesHtml}
            </div>
            <div class="card-name">${card.nom}</div>
            <div class="card-level">Niv. ${card.niveau}</div>
            <div class="card-cost">${card.cout_elixir} ⚡</div>
            <div class="card-actions">
                ${canMerge ? '<button class="btn-card-merge" title="Fusionner 3 cartes identiques">⚡</button>' : ''}
                <button class="btn-card-delete" title="Supprimer pour récupérer de l\'élixir">🗑️</button>
            </div>
        `;
        
        // Ajouter le support drag and drop
        cardElement.draggable = true;
        cardElement.setAttribute('data-card-name', card.nom);
        cardElement.setAttribute('data-card-level', card.niveau);
        cardElement.setAttribute('data-location', containerId === 'bench-cards' ? 'banc' : 'plateau');
        
        // Événements drag and drop
        cardElement.addEventListener('dragstart', handleDragStart);
        cardElement.addEventListener('dragend', handleDragEnd);
        
        // Bouton de fusion
        const mergeBtn = cardElement.querySelector('.btn-card-merge');
        if (mergeBtn) {
            mergeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                manualMerge(card);
            });
        }
        
        // Bouton de suppression
        const deleteBtn = cardElement.querySelector('.btn-card-delete');
        deleteBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteCard(card, containerId === 'bench-cards' ? 'banc' : 'plateau');
        });
        
        // Rendre les cartes du banc cliquables pour les déplacer vers le plateau (ancien système)
        if (containerId === 'bench-cards') {
            cardElement.addEventListener('click', (e) => {
                // Ne pas déclencher si on clique sur les boutons
                if (!e.target.classList.contains('btn-card-delete') && !e.target.classList.contains('btn-card-merge')) {
                    moveCardToField(card);
                }
            });
        }
        
        container.appendChild(cardElement);
    });
}

// Obtenir l'icône de famille
function getFamilyIcon(famille) {
    const icons = {
        'Noble': '🦁',
        'Clan': '🛡️',
        'Gobelin': '🧌',
        'Revenant': '👻',
        'Ace': '🎲',
        'Colosse': '🏋️',
        'Assassin': '🥷',
        'Guetteur': '🦉',
        'Bagarreur': '🥊',
        'Vengeuse': '⚡',
        'Lanceur': '🎯'
    };
    return icons[famille] || '❓';
}

// Variables globales pour le drag and drop
let draggedCard = null;

// Gestion du drag and drop
function handleDragStart(e) {
    draggedCard = {
        nom: e.target.getAttribute('data-card-name'),
        niveau: parseInt(e.target.getAttribute('data-card-level')),
        from: e.target.getAttribute('data-location')
    };
    e.target.style.opacity = '0.5';
}

function handleDragEnd(e) {
    e.target.style.opacity = '1';
    draggedCard = null;
}

function handleDragOver(e) {
    e.preventDefault();
    e.currentTarget.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.currentTarget.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.currentTarget.classList.remove('drag-over');
    
    if (!draggedCard) return;
    
    const dropZone = e.currentTarget;
    const toLocation = dropZone.id === 'bench-cards' ? 'banc' : 'plateau';
    
    if (draggedCard.from !== toLocation) {
        moveCard(draggedCard.nom, draggedCard.niveau, draggedCard.from, toLocation);
    }
}

// Déplacer une carte via drag and drop
async function moveCard(carteName, niveau, fromLocation, toLocation) {
    if (!gameState.session) {
        showError('Aucune session de jeu active');
        return;
    }
    
    try {
        const response = await fetch('/api/move_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: carteName,
                niveau: niveau,
                from: fromLocation,
                to: toLocation
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification(data.message, 'success');
            updateGameDisplay();
        } else {
            showError(data.error);
        }
    } catch (error) {
        console.error('Erreur lors du déplacement:', error);
        showError('Erreur lors du déplacement de la carte');
    }
}

// Supprimer une carte pour récupérer de l'élixir
async function deleteCard(card, location) {
    if (!gameState.session) {
        showError('Aucune session de jeu active');
        return;
    }
    
    const elixirRecupere = Math.max(1, card.cout_elixir - 1);
    const confirmation = confirm(`Supprimer ${card.nom} niveau ${card.niveau} pour récupérer ${elixirRecupere} élixir ?`);
    
    if (!confirmation) return;
    
    try {
        const response = await fetch('/api/delete_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: card.nom,
                niveau: card.niveau,
                location: location
            })
        });
        
        const data = await response.json();
        if (data.success) {
            showNotification(data.message, 'success');
            
            // Animation d'élixir si disponible
            if (data.elixir_recupere > 0) {
                animateElixirGain(data.elixir_recupere);
            }
            
            updateGameDisplay();
        } else {
            showError(data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la suppression:', error);
        showError('Erreur lors de la suppression de la carte');
    }
}

// Fusionner manuellement 3 cartes identiques
async function manualMerge(card) {
    if (!gameState.session) {
        showError('Aucune session de jeu active');
        return;
    }
    
    const confirmation = confirm(`Fusionner 3x ${card.nom} niveau ${card.niveau} en 1x niveau ${card.niveau + 1} ?`);
    
    if (!confirmation) return;
    
    try {
        const response = await fetch('/api/manual_merge', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: card.nom,
                niveau: card.niveau
            })
        });
        
        const data = await response.json();
        if (data.success) {
            // Message avec information sur les fusions multiples
            let notificationMessage = data.message;
            
            if (data.fusions_totales > 1) {
                showNotification(`🔥 ${data.fusions_totales} fusions en cascade !`, 'success');
            }
            
            showNotification(notificationMessage, 'success');
            
            // Animation d'élixir pour toutes les fusions
            if (data.elixir_gagne > 0) {
                animateElixirGain(data.elixir_gagne);
            }
            
            updateGameDisplay();
        } else {
            showError(data.error);
        }
    } catch (error) {
        console.error('Erreur lors de la fusion:', error);
        showError('Erreur lors de la fusion des cartes');
    }
}

// Déplacer une carte du banc vers le plateau
async function moveCardToField(card) {
    if (!gameState.session) {
        alert('Session de jeu non initialisée.');
        return;
    }
    
    try {
        const response = await fetch('/api/move_to_field', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: card.nom,
                niveau: card.niveau
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Déclencher animation élixir si fusion OU si élixir gagné
            if (data.elixir_gagne > 0) {
                animateElixirGain(data.elixir_gagne);
            }
            
            // Mettre à jour l'affichage
            updateGameDisplay();
            // Petit message de succès discret
            console.log(data.message);
        } else {
            // Affichage d'erreurs amélioré avec couleurs
            if (data.error.includes('Plateau plein')) {
                showError(data.error, 'warning');
            } else {
                alert('Erreur lors du déplacement: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        alert('Erreur de connexion au serveur.');
    }
}

// Fonction pour afficher des notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Ajouter les styles en ligne si pas dans le CSS
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        z-index: 10000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
        max-width: 400px;
        word-wrap: break-word;
    `;
    
    // Couleurs selon le type
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#10b981';
            break;
        case 'error':
            notification.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f59e0b';
            break;
        default:
            notification.style.backgroundColor = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    // Animation d'entrée
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Suppression automatique
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentNode) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 4000);
}

// Afficher l'écran de fin de partie avec un design moderne
function showGameOver() {
    const gameOverDiv = document.createElement('div');
    gameOverDiv.id = 'game-over-screen';
    gameOverDiv.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.8), rgba(30, 30, 60, 0.9));
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 20000;
        font-family: 'Segoe UI', sans-serif;
        backdrop-filter: blur(10px);
        animation: fadeIn 0.5s ease-out;
    `;
    
    // Récupérer les statistiques de la partie
    const currentTour = document.getElementById('tour-count').textContent || '1';
    const currentElixir = document.getElementById('elixir-count').textContent || '0';
    
    gameOverDiv.innerHTML = `
        <div style="
            background: linear-gradient(135deg, #1e293b, #334155);
            padding: 3rem;
            border-radius: 25px;
            text-align: center;
            color: white;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
            border: 2px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
            animation: slideInUp 0.6s ease-out 0.2s both;
        ">
            <!-- Effet de particules en arrière-plan -->
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 100 100\"><circle cx=\"20\" cy=\"20\" r=\"2\" fill=\"rgba(255,255,255,0.1)\"/><circle cx=\"80\" cy=\"40\" r=\"1\" fill=\"rgba(255,255,255,0.1)\"/><circle cx=\"40\" cy=\"80\" r=\"1.5\" fill=\"rgba(255,255,255,0.1)\"/><circle cx=\"90\" cy=\"10\" r=\"1\" fill=\"rgba(255,255,255,0.1)\"/><circle cx=\"10\" cy=\"90\" r=\"2\" fill=\"rgba(255,255,255,0.1)\"/></svg>') repeat;
                opacity: 0.3;
                animation: float 6s ease-in-out infinite;
            "></div>
            
            <!-- Contenu principal -->
            <div style="position: relative; z-index: 1;">
                <!-- Titre avec icône animée -->
                <div style="margin-bottom: 2rem;">
                    <div style="
                        font-size: 4rem;
                        margin-bottom: 0.5rem;
                        animation: skull-bounce 2s ease-in-out infinite;
                        filter: drop-shadow(0 0 20px rgba(239, 68, 68, 0.5));
                    ">💀</div>
                    <h1 style="
                        font-size: 2.5rem;
                        margin: 0;
                        background: linear-gradient(45deg, #ef4444, #f97316);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                        font-weight: 800;
                        letter-spacing: 2px;
                    ">GAME OVER</h1>
                </div>
                
                <!-- Message de défaite avec style -->
                <div style="
                    background: rgba(239, 68, 68, 0.1);
                    border: 1px solid rgba(239, 68, 68, 0.3);
                    border-radius: 15px;
                    padding: 1.5rem;
                    margin: 2rem 0;
                    backdrop-filter: blur(5px);
                ">
                    <p style="
                        font-size: 1.3rem;
                        margin: 0;
                        color: #fca5a5;
                        font-weight: 600;
                    ">⚡ Vos HP sont tombés à 0 !</p>
                    <p style="
                        font-size: 1rem;
                        margin: 0.5rem 0 0 0;
                        color: #d1d5db;
                        opacity: 0.8;
                    ">La bataille s'arrête ici, mais vous pouvez toujours recommencer !</p>
                </div>
                
                <!-- Statistiques de la partie -->
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    margin: 2rem 0;
                ">
                    <div style="
                        background: rgba(59, 130, 246, 0.1);
                        border: 1px solid rgba(59, 130, 246, 0.3);
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                    ">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">🕐</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #60a5fa;">Tour ${currentTour}</div>
                        <div style="font-size: 0.9rem; color: #d1d5db; opacity: 0.7;">Tours joués</div>
                    </div>
                    <div style="
                        background: rgba(16, 185, 129, 0.1);
                        border: 1px solid rgba(16, 185, 129, 0.3);
                        border-radius: 12px;
                        padding: 1rem;
                        text-align: center;
                    ">
                        <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
                        <div style="font-size: 1.5rem; font-weight: bold; color: #34d399;">${currentElixir}</div>
                        <div style="font-size: 0.9rem; color: #d1d5db; opacity: 0.7;">Élixir final</div>
                    </div>
                </div>
                
                <!-- Boutons d'action -->
                <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                    <button onclick="restartGame()" style="
                        padding: 15px 25px;
                        font-size: 1.1rem;
                        background: linear-gradient(135deg, #10b981, #059669);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: all 0.3s ease;
                        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    " onmouseover="this.style.transform='scale(1.05) translateY(-2px)'; this.style.boxShadow='0 12px 25px rgba(16, 185, 129, 0.4)'" 
                       onmouseout="this.style.transform='scale(1) translateY(0)'; this.style.boxShadow='0 8px 20px rgba(16, 185, 129, 0.3)'">
                        🔄 Nouvelle partie
                    </button>
                    <button onclick="document.getElementById('game-over-screen').remove()" style="
                        padding: 15px 25px;
                        font-size: 1.1rem;
                        background: linear-gradient(135deg, #6b7280, #4b5563);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        cursor: pointer;
                        font-weight: 600;
                        transition: all 0.3s ease;
                        box-shadow: 0 8px 20px rgba(75, 85, 99, 0.3);
                        display: flex;
                        align-items: center;
                        gap: 0.5rem;
                    " onmouseover="this.style.transform='scale(1.05) translateY(-2px)'; this.style.boxShadow='0 12px 25px rgba(75, 85, 99, 0.4)'" 
                       onmouseout="this.style.transform='scale(1) translateY(0)'; this.style.boxShadow='0 8px 20px rgba(75, 85, 99, 0.3)'">
                        📊 Voir l'état
                    </button>
                </div>
                
                <!-- Message encourageant -->
                <div style="
                    margin-top: 2rem;
                    padding: 1rem;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                ">
                    <p style="
                        font-size: 0.95rem;
                        color: #d1d5db;
                        margin: 0;
                        opacity: 0.8;
                        font-style: italic;
                    ">💪 "Chaque défaite est une leçon pour la prochaine victoire !"</p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(gameOverDiv);
}

// Fonction pour afficher des erreurs avec style
function showError(message, type = 'error') {
    const errorElement = document.createElement('div');
    errorElement.className = `error-toast ${type}`;
    errorElement.textContent = message;
    
    // Ajouter au header pour visibilité
    const header = document.querySelector('.header');
    header.appendChild(errorElement);
    
    // Animation d'apparition
    setTimeout(() => errorElement.classList.add('show'), 100);
    
    // Retirer après 3 secondes
    setTimeout(() => {
        errorElement.classList.remove('show');
        setTimeout(() => header.removeChild(errorElement), 300);
    }, 3000);
}

// Afficher les bonus de familles
function displayBonusFamilles(bonusFamilles) {
    const container = document.getElementById('bonus-familles');
    container.innerHTML = '';
    
    Object.entries(bonusFamilles).forEach(([famille, bonus]) => {
        const bonusElement = document.createElement('div');
        bonusElement.className = `bonus-item ${bonus.actif ? '' : 'inactive'}`;
        bonusElement.innerHTML = `
            <div class="bonus-header">
                <span>${getFamilyIcon(famille)}</span>
                <span class="famille-nom">${famille}</span>
                <span class="famille-count">(${bonus.nombre})</span>
                <span class="famille-status">${bonus.actif ? '✅' : '❌'}</span>
            </div>
            <div class="bonus-description">${bonus.description || ''}</div>
        `;
        container.appendChild(bonusElement);
    });
}

// Ajouter un choix
function addChoice() {
    const cardSelect = document.getElementById('choice-card');
    const levelInput = document.getElementById('choice-level');
    
    const selectedCard = cardSelect.value;
    const level = parseInt(levelInput.value) || 1;
    
    if (!selectedCard) {
        alert('Veuillez sélectionner une carte.');
        return;
    }
    
    // Vérifier si la carte n'est pas déjà dans les choix
    const existingChoice = gameState.currentChoices.find(choice => choice.carte === selectedCard);
    if (existingChoice) {
        alert('Cette carte est déjà dans les choix.');
        return;
    }
    
    // Récupérer les informations de la carte
    const cardInfo = cardsData[selectedCard];
    const elixirCost = cardInfo ? cardInfo.cout_elixir : 0;
    
    // Ajouter le choix
    const choice = {
        carte: selectedCard,
        niveau: level,
        index: gameState.currentChoices.length + 1,
        cout_elixir: elixirCost
    };
    
    gameState.currentChoices.push(choice);
    displayCurrentChoices();
    
    // Réinitialiser le formulaire
    cardSelect.value = '';
    levelInput.value = 1;
}

// Afficher les choix actuels
function displayCurrentChoices() {
    const container = document.getElementById('current-choices');
    container.innerHTML = '';
    
    gameState.currentChoices.forEach((choice, index) => {
        const choiceElement = document.createElement('div');
        choiceElement.className = 'choice-item';
        choiceElement.dataset.index = index;
        choiceElement.style.cursor = 'pointer'; // Ajouter le curseur pointer
        
        // Afficher élixir si disponible
        const elixirInfo = choice.cout_elixir ? ` - ${choice.cout_elixir}⚡` : '';
        
        choiceElement.innerHTML = `
            <div class="choice-content">
                <strong>${choice.index}.</strong> ${choice.carte} (Niv. ${choice.niveau}${elixirInfo})
            </div>
            <button class="btn btn-secondary" onclick="removeChoice(${index})">
                <i class="fas fa-trash"></i>
            </button>
        `;
        
        choiceElement.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                selectChoice(index);
            }
        });
        
        container.appendChild(choiceElement);
    });
}

// Supprimer un choix
function removeChoice(index) {
    gameState.currentChoices.splice(index, 1);
    // Réindexer les choix
    gameState.currentChoices.forEach((choice, i) => {
        choice.index = i + 1;
    });
    displayCurrentChoices();
}

// Sélectionner un choix
function selectChoice(index) {
    // Désélectionner tous les choix
    document.querySelectorAll('.choice-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Sélectionner le choix cliqué
    const choiceElement = document.querySelector(`[data-index="${index}"]`);
    if (choiceElement) {
        choiceElement.classList.add('selected');
        gameState.selectedChoice = index;
    }
}

// Obtenir les recommandations
async function getRecommendations() {
    if (gameState.currentChoices.length === 0) {
        alert('Veuillez ajouter au moins un choix.');
        return;
    }
    
    if (!gameState.session) {
        alert('Session de jeu non initialisée.');
        return;
    }
    
    const recommendationsContainer = document.getElementById('recommendations');
    recommendationsContainer.classList.add('visible'); // Rendre visible
    recommendationsContainer.innerHTML = '<div class="loading">Analyse en cours...</div>';
    
    try {
        const response = await fetch('/api/recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                choix: gameState.currentChoices.map(choice => ({
                    carte: choice.carte,
                    niveau: choice.niveau
                }))
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRecommendations(data);
        } else {
            recommendationsContainer.innerHTML = `<p>Erreur: ${data.error}</p>`;
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        recommendationsContainer.innerHTML = '<p>Erreur de connexion au serveur.</p>';
    }
}

// Afficher les recommandations
function displayRecommendations(data) {
    const container = document.getElementById('recommendations');
    
    let html = `<h3><i class="fas fa-brain"></i> Recommandations IA</h3>`;
    
    // Afficher le conseil général si présent
    if (data.conseil_general) {
        html += `<div class="conseil-general"><i class="fas fa-lightbulb"></i> ${data.conseil_general}</div>`;
    }
    
    // Afficher l'élixir actuel
    html += `<div class="elixir-info"><i class="fas fa-bolt"></i> Élixir disponible: ${data.elixir_actuel}</div>`;
    
    // Séparer les cartes abordables et chères
    if (data.cartes_abordables && data.cartes_abordables.length > 0) {
        html += `<h4 class="recommandations-section"><i class="fas fa-shopping-cart"></i> Cartes abordables maintenant</h4>`;
        data.cartes_abordables.forEach((rec, index) => {
            html += createRecommendationHtml(rec, index, 'abordable');
        });
    }
    
    if (data.cartes_cheres && data.cartes_cheres.length > 0) {
        html += `<h4 class="recommandations-section"><i class="fas fa-hourglass-half"></i> Cartes à considérer plus tard</h4>`;
        data.cartes_cheres.forEach((rec, index) => {
            html += createRecommendationHtml(rec, index, 'cher');
        });
    }
    
    // Si pas de données structurées, utiliser l'ancien format
    if (!data.cartes_abordables && !data.cartes_cheres && data.recommendations) {
        data.recommendations.forEach((rec, index) => {
            html += createRecommendationHtml(rec, index, rec.peut_acheter ? 'abordable' : 'cher');
        });
    }
    
    container.innerHTML = html;
}

// Créer le HTML pour une recommandation
function createRecommendationHtml(rec, index, type) {
    const typeClass = type === 'abordable' ? 'recommendation-affordable' : 'recommendation-expensive';
    const icon = type === 'abordable' ? '✅' : '⏳';
    
    return `
        <div class="recommendation-item ${typeClass}">
            <h4>${icon} Choix ${rec.choix_numero}: ${rec.carte} (Niveau ${rec.niveau})</h4>
            <div class="recommendation-score">Score: ${rec.score.toFixed(2)}</div>
            <p><strong>Raison:</strong> ${rec.raison}</p>
            <div><strong>Détails:</strong> ${rec.details}</div>
            ${!rec.peut_acheter ? '<div class="warning-elixir">💰 Élixir insuffisant pour cette carte</div>' : ''}
        </div>
    `;
}

// Valider le choix sélectionné (acheter la carte)
async function makeChoice() {
    if (gameState.selectedChoice === null) {
        alert('Veuillez sélectionner un choix.');
        return;
    }
    
    if (!gameState.session) {
        alert('Session de jeu non initialisée.');
        return;
    }
    
    const selectedChoiceData = gameState.currentChoices[gameState.selectedChoice];
    
    try {
        const response = await fetch('/api/buy_card', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: selectedChoiceData.carte,
                niveau: selectedChoiceData.niveau
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Déclencher animation élixir si élixir gagné
            if (data.elixir_gagne > 0) {
                animateElixirGain(data.elixir_gagne);
            }
            
            // Retirer le choix sélectionné de la liste
            gameState.currentChoices.splice(gameState.selectedChoice, 1);
            gameState.selectedChoice = null;
            
            // Réindexer les choix restants
            gameState.currentChoices.forEach((choice, i) => {
                choice.index = i + 1;
            });
            
            displayCurrentChoices();
            
            // Mettre à jour l'affichage du jeu
            updateGameDisplay();
            
            // Cacher les recommandations
            document.getElementById('recommendations').classList.remove('visible');
            document.getElementById('recommendations').innerHTML = '';
            
            alert(data.message);
            
        } else {
            alert('Erreur lors de l\'achat: ' + data.error);
        }
    } catch (error) {
        console.error('Erreur réseau:', error);
        alert('Erreur de connexion au serveur.');
    }
}

// Afficher les questions post-tour
function showPostTurnQuestions(questions) {
    // Créer une modal pour les questions post-tour
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Questions post-tour</h3>
                <span class="close" onclick="closeModal('post-turn-modal')">&times;</span>
            </div>
            <div class="modal-body">
                <div class="questions-container">
                    ${questions.map((question, index) => `
                        <div class="question-item">
                            <p><strong>Question ${index + 1}:</strong> ${question}</p>
                            <div class="question-actions">
                                <button class="btn btn-primary" onclick="answerQuestion(${index}, 'oui')">Oui</button>
                                <button class="btn btn-secondary" onclick="answerQuestion(${index}, 'non')">Non</button>
                                <button class="btn btn-tertiary" onclick="answerQuestion(${index}, 'ignore')">Ignorer</button>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="modal-footer">
                    <button class="btn btn-success" onclick="closeModal('post-turn-modal')">Terminer</button>
                </div>
            </div>
        </div>
    `;
    modal.id = 'post-turn-modal';
    
    // Supprimer l'ancienne modal si elle existe
    const existingModal = document.getElementById('post-turn-modal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Ajouter la modal au DOM
    document.body.appendChild(modal);
    modal.style.display = 'block';
}

// Répondre à une question post-tour
function answerQuestion(questionIndex, answer) {
    console.log(`Question ${questionIndex + 1}: ${answer}`);
    // Ici, on pourrait envoyer la réponse au serveur si nécessaire
    
    // Marquer la question comme répondue visuellement
    const questionItem = document.querySelectorAll('.question-item')[questionIndex];
    if (questionItem) {
        questionItem.style.opacity = '0.6';
        questionItem.querySelector('.question-actions').innerHTML = `<span class="answer-display">Réponse: ${answer}</span>`;
    }
}

// Fermer une modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Animation de gain d'élixir
function animateElixirGain(elixirGagne) {
    if (!elixirGagne || elixirGagne <= 0) return;
    
    const elixirCounter = document.querySelector('.elixir-counter');
    const elixirCount = document.getElementById('elixir-count');
    
    // Éviter les animations multiples simultanées
    if (elixirCounter.classList.contains('elixir-gain')) {
        return;
    }
    
    // Ajouter classe d'animation
    elixirCounter.classList.add('elixir-gain');
    
    // Créer l'élément de bonus flottant
    const bonusElement = document.createElement('div');
    bonusElement.className = 'elixir-bonus';
    bonusElement.textContent = `+${elixirGagne}`;
    
    // Ajouter le bonus au compteur
    elixirCounter.appendChild(bonusElement);
    
    // Effet sonore visuel supplémentaire pour les grosses gains
    if (elixirGagne >= 3) {
        bonusElement.style.fontSize = '1.1rem';
        bonusElement.style.fontWeight = '900';
        bonusElement.textContent = `🔥 +${elixirGagne}`;
    }
    
    // Supprimer les animations après leur durée
    setTimeout(() => {
        elixirCounter.classList.remove('elixir-gain');
        if (bonusElement.parentNode) {
            bonusElement.parentNode.removeChild(bonusElement);
        }
    }, 2000); // Augmenté pour correspondre à la nouvelle durée d'animation
}

// Afficher l'écran de fin de partie
function showGameOver() {
    // Créer la modal Game Over moderne
    const modal = document.createElement('div');
    modal.id = 'game-over-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(5px);
        animation: fadeIn 0.3s ease-out;
    `;
    
    // Récupérer les statistiques de la partie
    const currentTour = document.getElementById('tour-count')?.textContent || '1';
    const currentElixir = document.getElementById('elixir-count')?.textContent || '0';
    const currentHP = document.getElementById('hp-display')?.textContent || '0';
    
    modal.innerHTML = `
        <div style="
            background: linear-gradient(135deg, var(--white), var(--light-gray));
            border-radius: 20px;
            padding: 2.5rem;
            max-width: 600px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            text-align: center;
            animation: slideInUp 0.3s ease-out;
            border: 1px solid rgba(255, 255, 255, 0.2);
        ">
            <!-- Icône Game Over avec animation -->
            <div style="
                width: 100px;
                height: 100px;
                background: linear-gradient(135deg, var(--error), #dc2626);
                border-radius: 50%;
                margin: 0 auto 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 3rem;
                color: white;
                animation: skull-bounce 0.6s ease-out;
                box-shadow: 0 10px 30px rgba(239, 68, 68, 0.3);
            ">💀</div>
            
            <!-- Titre Game Over -->
            <h1 style="
                color: var(--error);
                margin-bottom: 1rem;
                font-size: 2.5rem;
                font-weight: 700;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            ">Game Over</h1>
            
            <!-- Message principal -->
            <p style="
                color: var(--dark-gray);
                font-size: 1.3rem;
                margin-bottom: 2rem;
                line-height: 1.5;
            ">Vous avez perdu tous vos HP !<br>La partie est terminée.</p>
            
            <!-- Statistiques de la partie -->
            <div style="
                background: rgba(255, 255, 255, 0.5);
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.3);
            ">
                <h3 style="
                    color: var(--dark-gray);
                    margin-bottom: 1rem;
                    font-size: 1.2rem;
                    font-weight: 600;
                ">📊 Statistiques de la partie</h3>
                
                <div style="
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                    gap: 1rem;
                    text-align: center;
                ">
                    <div style="
                        background: white;
                        padding: 1rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏰</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--primary-blue);">${currentTour}</div>
                        <div style="font-size: 0.9rem; color: var(--gray);">Tours</div>
                    </div>
                    
                    <div style="
                        background: white;
                        padding: 1rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💧</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--primary-purple);">${currentElixir}</div>
                        <div style="font-size: 0.9rem; color: var(--gray);">Élixir</div>
                    </div>
                    
                    <div style="
                        background: white;
                        padding: 1rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">❤️</div>
                        <div style="font-size: 1.2rem; font-weight: 600; color: var(--error);">${currentHP}</div>
                        <div style="font-size: 0.9rem; color: var(--gray);">HP</div>
                    </div>
                </div>
            </div>
            
            <!-- Boutons d'action -->
            <div style="
                display: flex;
                gap: 1rem;
                justify-content: center;
                flex-wrap: wrap;
            ">
                <button id="restart-game" style="
                    background: linear-gradient(135deg, var(--success), #059669);
                    color: white;
                    border: none;
                    padding: 1rem 2rem;
                    border-radius: 12px;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    min-width: 180px;
                    justify-content: center;
                ">
                    <i class="fas fa-redo"></i> Nouvelle partie
                </button>
                
                <button id="close-game-over" style="
                    background: var(--light-gray);
                    color: var(--dark-gray);
                    border: none;
                    padding: 1rem 2rem;
                    border-radius: 12px;
                    font-size: 1.1rem;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    min-width: 180px;
                    justify-content: center;
                ">
                    <i class="fas fa-eye"></i> Voir l'état
                </button>
            </div>
            
            <!-- Message encourageant -->
            <div style="
                margin-top: 2rem;
                padding: 1rem;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            ">
                <p style="
                    font-size: 1rem;
                    color: var(--gray);
                    margin: 0;
                    opacity: 0.8;
                    font-style: italic;
                ">💪 "L'échec est le fondement de la réussite !"</p>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Gestion des événements
    const restartBtn = document.getElementById('restart-game');
    const closeBtn = document.getElementById('close-game-over');
    
    const cleanup = () => {
        modal.style.opacity = '0';
        setTimeout(() => {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
        }, 300);
    };
    
    restartBtn.onclick = () => {
        cleanup();
        restartGame();
    };
    
    closeBtn.onclick = () => {
        cleanup();
    };
    
    // Effets hover sur les boutons
    [restartBtn, closeBtn].forEach(btn => {
        btn.onmouseenter = () => {
            btn.style.transform = 'translateY(-2px)';
            if (btn === restartBtn) {
                btn.style.boxShadow = '0 6px 20px rgba(16, 185, 129, 0.4)';
            } else {
                btn.style.boxShadow = '0 6px 20px rgba(0, 0, 0, 0.15)';
            }
        };
        btn.onmouseleave = () => {
            btn.style.transform = 'translateY(0)';
            if (btn === restartBtn) {
                btn.style.boxShadow = '0 4px 15px rgba(16, 185, 129, 0.3)';
            } else {
                btn.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
            }
        };
    });
}

// Redémarrer le jeu
function restartGame() {
    // Fermer tous les modals
    document.querySelectorAll('.modal').forEach(modal => {
        modal.remove();
    });
    
    // Réinitialiser l'état du jeu
    gameState = {
        currentStep: 1,
        sessionId: null,
        selectedLeader: null,
        selectedModificateur: null,
        selectedCard: null,
        selectedCardLevel: 1
    };
    
    // Masquer l'interface de jeu
    document.getElementById('game-interface').style.display = 'none';
    
    // Afficher le panneau de configuration
    document.getElementById('config-panel').style.display = 'block';
    
    // Retourner à l'étape 1
    showStep(1);
}

// Modal moderne pour saisir le nombre de troupes adverses restantes
function showDefeatModal() {
    return new Promise((resolve) => {
        // Créer la modal
        const modal = document.createElement('div');
        modal.id = 'defeat-modal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
            animation: fadeIn 0.3s ease-out;
        `;
        
        modal.innerHTML = `
            <div style="
                background: linear-gradient(135deg, var(--white), var(--light-gray));
                border-radius: 20px;
                padding: 2rem;
                max-width: 500px;
                width: 90%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                text-align: center;
                animation: slideInUp 0.3s ease-out;
            ">
                <div style="
                    width: 80px;
                    height: 80px;
                    background: linear-gradient(135deg, var(--error), #dc2626);
                    border-radius: 50%;
                    margin: 0 auto 1.5rem;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 2.5rem;
                    color: white;
                    animation: skull-bounce 0.6s ease-out;
                ">💀</div>
                
                <h2 style="
                    color: var(--dark-gray);
                    margin-bottom: 1rem;
                    font-size: 1.8rem;
                    font-weight: 600;
                ">Défaite !</h2>
                
                <p style="
                    color: var(--gray);
                    margin-bottom: 2rem;
                    font-size: 1.1rem;
                ">Combien de troupes adverses restent-elles sur le plateau ?</p>
                
                <div style="margin-bottom: 2rem;">
                    <input type="number" 
                           id="troops-input" 
                           min="0" 
                           max="20" 
                           value="0" 
                           placeholder="Nombre de troupes"
                           style="
                               width: 200px;
                               padding: 1rem;
                               border: 2px solid var(--light-gray);
                               border-radius: 10px;
                               font-size: 1.2rem;
                               text-align: center;
                               background: white;
                               color: var(--dark-gray);
                               box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                               transition: all 0.3s ease;
                           ">
                </div>
                
                <div style="display: flex; gap: 1rem; justify-content: center;">
                    <button id="confirm-defeat" style="
                        background: linear-gradient(135deg, var(--error), #dc2626);
                        color: white;
                        border: none;
                        padding: 1rem 2rem;
                        border-radius: 10px;
                        font-size: 1.1rem;
                        font-weight: 600;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
                        transition: all 0.3s ease;
                    ">
                        <i class="fas fa-check"></i> Confirmer
                    </button>
                    <button id="cancel-defeat" style="
                        background: var(--light-gray);
                        color: var(--dark-gray);
                        border: none;
                        padding: 1rem 2rem;
                        border-radius: 10px;
                        font-size: 1.1rem;
                        font-weight: 600;
                        cursor: pointer;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
                        transition: all 0.3s ease;
                    ">
                        <i class="fas fa-times"></i> Annuler
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Focus sur l'input
        setTimeout(() => {
            document.getElementById('troops-input').focus();
            document.getElementById('troops-input').select();
        }, 100);
        
        // Gestion des événements
        const confirmBtn = document.getElementById('confirm-defeat');
        const cancelBtn = document.getElementById('cancel-defeat');
        const input = document.getElementById('troops-input');
        
        const cleanup = () => {
            modal.style.opacity = '0';
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
            }, 300);
        };
        
        confirmBtn.onclick = () => {
            const value = parseInt(input.value) || 0;
            const validValue = Math.max(0, Math.min(20, value)); // Entre 0 et 20
            cleanup();
            resolve(validValue);
        };
        
        cancelBtn.onclick = () => {
            cleanup();
            resolve(null);
        };
        
        // Validation sur Entrée
        input.onkeydown = (e) => {
            if (e.key === 'Enter') {
                confirmBtn.click();
            } else if (e.key === 'Escape') {
                cancelBtn.click();
            }
        };
        
        // Effet hover sur les boutons
        [confirmBtn, cancelBtn].forEach(btn => {
            btn.onmouseenter = () => {
                btn.style.transform = 'translateY(-2px)';
                btn.style.boxShadow = btn === confirmBtn 
                    ? '0 6px 20px rgba(239, 68, 68, 0.4)' 
                    : '0 6px 20px rgba(0, 0, 0, 0.15)';
            };
            btn.onmouseleave = () => {
                btn.style.transform = 'translateY(0)';
                btn.style.boxShadow = btn === confirmBtn 
                    ? '0 4px 15px rgba(239, 68, 68, 0.3)' 
                    : '0 4px 15px rgba(0, 0, 0, 0.1)';
            };
        });
        
        // Effet focus sur l'input
        input.onfocus = () => {
            input.style.borderColor = 'var(--primary-blue)';
            input.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
        };
        input.onblur = () => {
            input.style.borderColor = 'var(--light-gray)';
            input.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
        };
    });
}

// Fonction pour enregistrer le résultat d'une bataille avec modal pour les troupes adverses
async function recordBattleResult(victoire) {
    let troupesAdversesRestantes = 0;
    
    // Si c'est une défaite, demander le nombre de troupes adverses restantes avec une belle modal
    if (!victoire) {
        troupesAdversesRestantes = await showDefeatModal();
        if (troupesAdversesRestantes === null) {
            return; // L'utilisateur a annulé
        }
    }
    
    try {
        const response = await fetch('/api/battle_result', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: gameState.session,
                victoire: victoire,
                troupes_adverses_restantes: troupesAdversesRestantes
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            let message = data.message;
            
            if (data.victoire) {
                showNotification(message, 'success');
            } else {
                showNotification(message, 'error');
            }
            
            // Animation d'élixir si gagné
            if (data.elixir_gagne > 0) {
                animateElixirGain(data.elixir_gagne);
            }
            
            // Vérifier si le jeu est terminé
            if (data.game_over) {
                setTimeout(() => {
                    showGameOver();
                }, 2000);
            } else {
                // Actualiser l'état du jeu
                setTimeout(() => {
                    updateGameDisplay();
                }, 2000);
            }
        } else {
            showNotification(data.error || 'Erreur lors de l\'enregistrement du résultat', 'error');
        }
    } catch (error) {
        console.error('Erreur:', error);
        showNotification('Erreur de connexion', 'error');
    }
}

// Gestion des clics sur les modals
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// Raccourcis clavier
document.addEventListener('keydown', function(e) {
    // Echap pour fermer les modals
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    // Chiffres pour sélectionner rapidement les choix
    if (e.key >= '1' && e.key <= '9') {
        const choiceIndex = parseInt(e.key) - 1;
        if (choiceIndex < gameState.currentChoices.length) {
            selectChoice(choiceIndex);
        }
    }
});

// Redémarrer le jeu
function restartGame() {
    // Supprimer l'écran de game over
    const gameOverScreen = document.querySelector('div[style*="position: fixed"][style*="z-index: 20000"]');
    if (gameOverScreen) {
        document.body.removeChild(gameOverScreen);
    }
    
    // Réinitialiser l'état du jeu
    gameState = {
        isConfigured: false,
        currentStep: 1,
        selectedModificateur: null,
        selectedLeader: null,
        currentChoices: [],
        selectedChoice: null,
        session: null
    };
    
    // Cacher les game-stats dans le header
    const gameStats = document.getElementById('game-stats');
    if (gameStats) {
        gameStats.style.display = 'none';
    }
    
    // Afficher le panel de configuration
    document.getElementById('config-panel').style.display = 'block';
    document.getElementById('game-interface').style.display = 'none';
    
    // Retourner à l'étape 1
    showStep(1);
}

// ===== PLATEAU HEXAGONAL ===== 
// État du plateau de jeu
let gameBoard = {
    allyTroops: {}, // Position -> {nom, niveau, famille}
    enemyTroops: {} // Position -> {nom, niveau, famille}
};

// Initialiser le plateau hexagonal
function initializeGameBoard() {
    // Ajouter les événements de clic sur les cellules
    document.querySelectorAll('.hex-cell').forEach(cell => {
        cell.addEventListener('click', handleHexCellClick);
        cell.addEventListener('dragover', handleHexDragOver);
        cell.addEventListener('drop', handleHexDrop);
    });
}

// Gérer le clic sur une cellule hexagonale
function handleHexCellClick(event) {
    const cell = event.currentTarget;
    const position = cell.dataset.pos;
    const row = parseInt(position.split('-')[0]);
    
    // Vérifier si c'est une zone alliée (lignes négatives)
    if (row < 0) {
        handleAllyCellClick(cell, position);
    } else {
        handleEnemyCellClick(cell, position);
    }
}

// Gérer le clic sur une cellule alliée
function handleAllyCellClick(cell, position) {
    if (cell.classList.contains('occupied')) {
        // Cellule occupée - montrer les options
        showTroopOptions(cell, position, 'ally');
    } else {
        // Cellule vide - proposer de placer une troupe du banc
        showPlacementOptions(cell, position);
    }
}

// Gérer le clic sur une cellule ennemie
function handleEnemyCellClick(cell, position) {
    if (cell.classList.contains('occupied')) {
        // Troupe ennemie - montrer les infos
        showEnemyTroopInfo(cell, position);
    } else {
        // Cellule vide ennemie - ajouter une troupe ennemie manuellement
        showEnemyPlacementOptions(cell, position);
    }
}

// Afficher les options de placement pour une cellule vide
function showPlacementOptions(cell, position) {
    // Récupérer les troupes disponibles sur le banc
    const benchTroops = document.querySelectorAll('#bench-cards .card-item');
    
    if (benchTroops.length === 0) {
        showNotification('Aucune troupe disponible sur le banc', 'warning');
        return;
    }
    
    // Créer un menu contextuel
    const menu = document.createElement('div');
    menu.className = 'hex-placement-menu';
    menu.innerHTML = `
        <div class="hex-menu-header">
            <h4>Placer une troupe</h4>
            <button class="close-hex-menu">&times;</button>
        </div>
        <div class="hex-menu-troops">
            ${Array.from(benchTroops).map(troop => {
                const name = troop.querySelector('.card-name').textContent;
                const level = troop.querySelector('.card-level').textContent;
                return `
                    <div class="hex-menu-troop" data-troop="${name}" data-level="${level}">
                        <span class="troop-name">${name}</span>
                        <span class="troop-level">${level}</span>
                    </div>
                `;
            }).join('')}
        </div>
    `;
    
    // Positionner le menu
    const rect = cell.getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.left = rect.left + 'px';
    menu.style.top = rect.bottom + 5 + 'px';
    menu.style.zIndex = '1000';
    
    document.body.appendChild(menu);
    
    // Gérer les événements du menu
    menu.querySelector('.close-hex-menu').addEventListener('click', () => {
        document.body.removeChild(menu);
    });
    
    menu.querySelectorAll('.hex-menu-troop').forEach(troopOption => {
        troopOption.addEventListener('click', () => {
            const troopName = troopOption.dataset.troop;
            const troopLevel = troopOption.dataset.level;
            placeTroopOnBoard(position, troopName, troopLevel, 'ally');
            document.body.removeChild(menu);
        });
    });
}

// Placer une troupe sur le plateau
function placeTroopOnBoard(position, troopName, troopLevel, side) {
    const cell = document.querySelector(`[data-pos="${position}"]`);
    
    // Récupérer les informations de la carte
    const cardData = cardsData[troopName];
    if (!cardData) {
        showError('Carte non trouvée: ' + troopName);
        return;
    }
    
    // Mettre à jour la cellule
    cell.classList.add('occupied');
    if (side === 'enemy') {
        cell.classList.add('enemy-troop');
    }
    
    cell.innerHTML = `
        <div class="troop-info">
            <div class="troop-name">${troopName}</div>
            <div class="troop-level">★${troopLevel}</div>
        </div>
    `;
    
    // Stocker dans l'état du plateau
    if (side === 'ally') {
        gameBoard.allyTroops[position] = {
            nom: troopName,
            niveau: parseInt(troopLevel),
            familles: cardData.traits
        };
    } else {
        gameBoard.enemyTroops[position] = {
            nom: troopName,
            niveau: parseInt(troopLevel),
            familles: cardData.traits
        };
    }
    
    showNotification(`${troopName} (★${troopLevel}) placé en ${position}`, 'success');
}

// Afficher les options pour une troupe existante
function showTroopOptions(cell, position, side) {
    const troopData = side === 'ally' ? gameBoard.allyTroops[position] : gameBoard.enemyTroops[position];
    
    const menu = document.createElement('div');
    menu.className = 'hex-troop-menu';
    menu.innerHTML = `
        <div class="hex-menu-header">
            <h4>${troopData.nom} ★${troopData.niveau}</h4>
            <button class="close-hex-menu">&times;</button>
        </div>
        <div class="hex-menu-actions">
            <button class="hex-action-btn move-troop">
                <i class="fas fa-arrows-alt"></i> Déplacer
            </button>
            <button class="hex-action-btn remove-troop">
                <i class="fas fa-trash"></i> Retirer
            </button>
            ${side === 'ally' ? `
                <button class="hex-action-btn return-bench">
                    <i class="fas fa-undo"></i> Vers banc
                </button>
            ` : ''}
        </div>
        <div class="troop-details">
            <p><strong>Familles:</strong> ${troopData.familles.join(', ')}</p>
        </div>
    `;
    
    const rect = cell.getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.left = rect.right + 5 + 'px';
    menu.style.top = rect.top + 'px';
    menu.style.zIndex = '1000';
    
    document.body.appendChild(menu);
    
    // Gérer les actions
    menu.querySelector('.close-hex-menu').addEventListener('click', () => {
        document.body.removeChild(menu);
    });
    
    menu.querySelector('.remove-troop').addEventListener('click', () => {
        removeTroopFromBoard(position, side);
        document.body.removeChild(menu);
    });
    
    if (menu.querySelector('.return-bench')) {
        menu.querySelector('.return-bench').addEventListener('click', () => {
            returnTroopToBench(position);
            document.body.removeChild(menu);
        });
    }
}

// Retirer une troupe du plateau
function removeTroopFromBoard(position, side) {
    const cell = document.querySelector(`[data-pos="${position}"]`);
    
    cell.classList.remove('occupied', 'enemy-troop');
    cell.innerHTML = '';
    
    if (side === 'ally') {
        delete gameBoard.allyTroops[position];
    } else {
        delete gameBoard.enemyTroops[position];
    }
    
    showNotification('Troupe retirée du plateau', 'info');
}

// Retourner une troupe au banc
async function returnTroopToBench(position) {
    const troopData = gameBoard.allyTroops[position];
    
    if (!troopData) return;
    
    // Simuler un appel API pour remettre la troupe au banc
    try {
        const response = await fetch('/api/move_card', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: troopData.nom,
                niveau: troopData.niveau,
                from: 'plateau',
                to: 'banc'
            })
        });
        
        if (response.ok) {
            removeTroopFromBoard(position, 'ally');
            await updateGameDisplay();
            showNotification(`${troopData.nom} retourné au banc`, 'success');
        }
    } catch (error) {
        console.error('Erreur lors du retour au banc:', error);
        showError('Erreur lors du retour au banc');
    }
}

// Drag and drop pour le plateau hexagonal
function handleHexDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('hex-drag-over');
}

function handleHexDrop(event) {
    event.preventDefault();
    const cell = event.currentTarget;
    cell.classList.remove('hex-drag-over');
    
    if (draggedCard && !cell.classList.contains('occupied')) {
        const position = cell.dataset.pos;
        const row = parseInt(position.split('-')[0]);
        
        // Seules les zones alliées peuvent recevoir nos troupes
        if (row < 0) {
            const cardName = draggedCard.querySelector('.card-name').textContent;
            const cardLevel = draggedCard.querySelector('.card-level').textContent.replace('★', '');
            
            placeTroopOnBoard(position, cardName, cardLevel, 'ally');
            
            // Simuler le déplacement via l'API
            moveCardToFieldHex(draggedCard, position);
        }
    }
}

// Déplacer une carte vers une position hexagonale spécifique
async function moveCardToFieldHex(card, hexPosition) {
    const cardName = card.querySelector('.card-name').textContent;
    const cardLevel = card.querySelector('.card-level').textContent.replace('★', '');
    
    try {
        const response = await fetch('/api/move_card', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: gameState.session,
                carte: cardName,
                niveau: parseInt(cardLevel),
                from: 'banc',
                to: 'plateau',
                hex_position: hexPosition
            })
        });
        
        if (response.ok) {
            await updateGameDisplay();
            showNotification(`${cardName} placé en ${hexPosition}`, 'success');
        }
    } catch (error) {
        console.error('Erreur lors du placement:', error);
        showError('Erreur lors du placement');
    }
}

// Afficher les options de placement d'ennemis
function showEnemyPlacementOptions(cell, position) {
    const menu = document.createElement('div');
    menu.className = 'hex-enemy-menu';
    menu.innerHTML = `
        <div class="hex-menu-header">
            <h4>Ajouter troupe ennemie</h4>
            <button class="close-hex-menu">&times;</button>
        </div>
        <div class="enemy-input-group">
            <select class="enemy-troop-select">
                <option value="">Choisir une troupe...</option>
                ${Object.keys(cardsData).map(cardName => 
                    `<option value="${cardName}">${cardName}</option>`
                ).join('')}
            </select>
            <input type="number" class="enemy-level-input" min="1" max="5" value="1" placeholder="Niveau">
            <button class="place-enemy-btn">Placer</button>
        </div>
    `;
    
    const rect = cell.getBoundingClientRect();
    menu.style.position = 'fixed';
    menu.style.left = rect.left + 'px';
    menu.style.top = rect.bottom + 5 + 'px';
    menu.style.zIndex = '1000';
    
    document.body.appendChild(menu);
    
    menu.querySelector('.close-hex-menu').addEventListener('click', () => {
        document.body.removeChild(menu);
    });
    
    menu.querySelector('.place-enemy-btn').addEventListener('click', () => {
        const troopName = menu.querySelector('.enemy-troop-select').value;
        const troopLevel = menu.querySelector('.enemy-level-input').value;
        
        if (troopName && troopLevel) {
            placeTroopOnBoard(position, troopName, troopLevel, 'enemy');
            document.body.removeChild(menu);
        } else {
            showError('Veuillez sélectionner une troupe et un niveau');
        }
    });
}

// Mettre à jour l'affichage du plateau avec les données du serveur
function updateGameBoardDisplay(gameStateData) {
    // Effacer le plateau actuel
    clearGameBoard();
    
    // Afficher les troupes du plateau
    if (gameStateData.plateau) {
        gameStateData.plateau.forEach((carte, index) => {
            // Pour l'instant, placer les troupes sur la première ligne disponible
            const position = `-1-${index}`;
            const cell = document.querySelector(`[data-pos="${position}"]`);
            
            if (cell && index < 5) { // Maximum 5 troupes sur une ligne
                placeTroopOnBoard(position, carte.nom, carte.niveau, 'ally');
            }
        });
    }
}

// Effacer le plateau
function clearGameBoard() {
    document.querySelectorAll('.hex-cell.occupied').forEach(cell => {
        cell.classList.remove('occupied', 'enemy-troop');
        cell.innerHTML = '';
    });
    
    gameBoard.allyTroops = {};
    gameBoard.enemyTroops = {};
}

// CSS pour les menus hexagonaux (à ajouter dynamiquement)
function addHexMenuStyles() {
    if (!document.getElementById('hex-menu-styles')) {
        const style = document.createElement('style');
        style.id = 'hex-menu-styles';
        style.textContent = `
            .hex-placement-menu, .hex-troop-menu, .hex-enemy-menu {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                border: 2px solid var(--primary-blue);
                min-width: 200px;
                max-width: 300px;
            }
            
            .hex-menu-header {
                background: var(--primary-blue);
                color: white;
                padding: 0.8rem;
                border-radius: 6px 6px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .hex-menu-header h4 {
                margin: 0;
                font-size: 0.9rem;
            }
            
            .close-hex-menu {
                background: none;
                border: none;
                color: white;
                font-size: 1.2rem;
                cursor: pointer;
                padding: 0;
                width: 1.5rem;
                height: 1.5rem;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .hex-menu-troops, .hex-menu-actions, .enemy-input-group {
                padding: 1rem;
            }
            
            .hex-menu-troop {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem;
                border-radius: 4px;
                cursor: pointer;
                margin-bottom: 0.3rem;
                border: 1px solid var(--light-gray);
            }
            
            .hex-menu-troop:hover {
                background: var(--light-blue);
            }
            
            .hex-action-btn {
                width: 100%;
                padding: 0.6rem;
                margin-bottom: 0.5rem;
                background: var(--primary-blue);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 0.8rem;
            }
            
            .hex-action-btn:hover {
                background: var(--dark-blue);
            }
            
            .enemy-input-group {
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            .enemy-troop-select, .enemy-level-input {
                padding: 0.5rem;
                border: 1px solid var(--gray);
                border-radius: 4px;
            }
            
            .place-enemy-btn {
                padding: 0.6rem;
                background: var(--error);
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            
            .hex-cell.hex-drag-over {
                background: var(--primary-gold) !important;
                transform: scale(1.1);
            }
            
            .troop-details {
                padding: 0 1rem 1rem;
                font-size: 0.8rem;
                color: var(--dark-gray);
            }
        `;
        document.head.appendChild(style);
    }
}

// Initialiser le plateau lors du chargement de l'interface de jeu
function showGameInterface() {
    document.getElementById('config-panel').style.display = 'none';
    document.getElementById('game-interface').style.display = 'grid';
    
    // Afficher les game-stats dans le header
    const gameStats = document.getElementById('game-stats');
    if (gameStats) {
        gameStats.style.display = 'flex';
    }
    
    // Configurer les zones de drop pour le drag and drop
    setupDropZones();
    
    // Initialiser le plateau hexagonal
    initializeGameBoard();
    addHexMenuStyles();
}

// Mise à jour automatique de l'état du jeu toutes les 30 secondes
setInterval(() => {
    if (gameState.isConfigured && gameState.session) {
        updateGameDisplay();
    }
}, 30000);
