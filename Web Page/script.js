const socket = io();
const lobby = document.getElementById('lobby');
const btnTest = document.getElementById('btn-test');
const statusEl = document.getElementById('connection-status');
const debugEl = document.getElementById('debug');
const lobbyStatus = document.getElementById('lobby-status');

// État initial de la manette
let controllerState = {
    id: null,
    buttons: { H: false, Pause: false },
    sensors: { 
        alpha: 0, beta: 0, gamma: 0, 
        accel: { x: 0, y: 0, z: 0 } 
    }
};

// --- GESTION DES SLOTS (1-4) ---

// Mise à jour visuelle des boutons de slots selon l'occupation
socket.on('slots_update', (slots) => {
    for (let i = 1; i <= 4; i++) {
        const btn = document.getElementById(`slot-${i}`);
        if (slots[i]) {
            btn.classList.replace('available', 'taken');
            btn.innerText = "OCCUPÉ";
        } else {
            btn.classList.replace('taken', 'available');
            btn.innerText = `JOUEUR ${i}`;
        }
    }
});

// Envoi de la demande de slot au serveur
window.selectSlot = (num) => {
    lobbyStatus.innerText = `Demande du slot ${num}...`;
    socket.emit('select_slot', num);
};

// Confirmation du slot par le serveur
socket.on('slot_confirmed', (data) => {
    controllerState.id = `JOUEUR-${data.slot}`;
    requestDevicePermissions();
});

// Refus du slot
socket.on('slot_denied', (data) => {
    alert(data.message);
    lobbyStatus.innerText = "Sélectionnez un autre slot.";
});

// Réception du signal de Kick (Reset) depuis la page Dev
socket.on('force_reset', () => {
    window.location.reload(); 
});

// --- MODE TEST ---
btnTest.onclick = () => {
    controllerState.id = "TEST-" + Math.random().toString(36).substring(2, 7).toUpperCase();
    requestDevicePermissions();
};

// --- PERMISSIONS ET CAPTEURS ---

async function requestDevicePermissions() {
    try {
        // Demande de permission iOS (nécessite HTTPS)
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            await DeviceOrientationEvent.requestPermission();
            await DeviceMotionEvent.requestPermission();
        }
        startSensors();
    } catch (e) {
        console.warn("Permissions capteurs échouées, démarrage forcé :", e);
        startSensors(); // On démarre quand même pour les boutons
    }
}

function startSensors() {
    lobby.style.display = 'none'; // On cache le menu de sélection
    
    // Écouteur Orientation (Degrés)
    window.addEventListener('deviceorientation', (event) => {
        controllerState.sensors.alpha = Math.round(event.alpha || 0);
        controllerState.sensors.beta = Math.round(event.beta || 0);
        controllerState.sensors.gamma = Math.round(event.gamma || 0);
        sendData();
    }, true);

    // Écouteur Mouvement (Valeurs brutes m/s²)
    window.addEventListener('devicemotion', (event) => {
        if (event.accelerationIncludingGravity) {
            controllerState.sensors.accel.x = event.accelerationIncludingGravity.x;
            controllerState.sensors.accel.y = event.accelerationIncludingGravity.y;
            controllerState.sensors.accel.z = event.accelerationIncludingGravity.z;
            
            debugEl.innerText = `Brut X: ${controllerState.sensors.accel.x.toFixed(2)} | Y: ${controllerState.sensors.accel.y.toFixed(2)}`;
            sendData();
        }
    }, true);
}

// --- BOUTONS ET TRANSMISSION ---

function setupButton(id, key) {
    const el = document.getElementById(id);
    if (!el) return;

    const update = (state) => {
        controllerState.buttons[key] = state;
        el.classList.toggle('active', state);
        sendData();
    };

    el.addEventListener('touchstart', (e) => { e.preventDefault(); update(true); });
    el.addEventListener('touchend', (e) => { e.preventDefault(); update(false); });
    el.addEventListener('mousedown', () => update(true));
    el.addEventListener('mouseup', () => update(false));
}

setupButton('btn-H', 'H');
setupButton('btn-Pause', 'Pause');

let lastSend = 0;
function sendData() {
    if (!controllerState.id) return;
    const now = Date.now();
    if (now - lastSend > 30) { // Environ 33 FPS
        socket.emit('controller_data', controllerState);
        lastSend = now;
    }
}

socket.on('vibrate', (data) => {
    if (navigator.vibrate) {
        navigator.vibrate(data.duration || 50);
    }
});


// Statut de connexion socket
socket.on('connect', () => {
    statusEl.innerText = "● Serveur Connecté";
    statusEl.style.color = "#4ade80";
});