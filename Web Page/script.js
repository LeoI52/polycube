const socket = io();
const lobby = document.getElementById('lobby');
const btnJoin = document.getElementById('btn-join');
const displayId = document.getElementById('display-id');
const statusEl = document.getElementById('connection-status');
const debugEl = document.getElementById('debug');

// 1. Génération de l'ID unique
const myId = "CTRL-" + Math.random().toString(36).substring(2, 7).toUpperCase();
displayId.innerText = "ID: " + myId;

let controllerState = {
    id: myId,
    buttons: { H: false, Pause: false },
    sensors: { 
        alpha: 0, beta: 0, gamma: 0, 
        accel: { x: 0, y: 0, z: 0 } 
    }
};

socket.on('connect', () => {
    statusEl.innerText = "● Connecté au Serveur";
    statusEl.style.color = "#4ade80";
});

// 2. Gestion des boutons physiques de l'interface
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
    // Support souris pour le test sur PC
    el.addEventListener('mousedown', () => update(true));
    el.addEventListener('mouseup', () => update(false));
}

setupButton('btn-H', 'H');
setupButton('btn-Pause', 'Pause');

// 3. Gestion des Permissions (La partie critique pour iOS/Android)
async function requestDevicePermissions() {
    try {
        // Test iOS 13+ pour l'Orientation
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            const status = await DeviceOrientationEvent.requestPermission();
            if (status !== 'granted') {
                alert("Permission d'orientation refusée.");
            }
        }
        
        // Test iOS 13+ pour le Mouvement (Accéléromètre)
        if (typeof DeviceMotionEvent !== 'undefined' && typeof DeviceMotionEvent.requestPermission === 'function') {
            const status = await DeviceMotionEvent.requestPermission();
            if (status !== 'granted') {
                alert("Permission de mouvement refusée.");
            }
        }

        // Si on arrive ici, on tente de démarrer les capteurs
        startSensors();
    } catch (error) {
        console.error(error);
        alert("Erreur lors de la demande de capteurs. Vérifiez que vous êtes en HTTPS ou que les drapeaux de sécurité sont configurés.");
        // On force quand même l'entrée dans la manette pour tester les boutons
        startSensors();
    }
}

function startSensors() {
    lobby.style.display = 'none';
    debugEl.innerText = "Capteurs : Initialisation...";

    // Écouteur Orientation
    window.addEventListener('deviceorientation', (event) => {
        controllerState.sensors.alpha = Math.round(event.alpha || 0);
        controllerState.sensors.beta = Math.round(event.beta || 0);
        controllerState.sensors.gamma = Math.round(event.gamma || 0);
        sendData();
    }, true);

    // Écouteur Accéléromètre (Valeurs Brutes)
    window.addEventListener('devicemotion', (event) => {
        if (event.accelerationIncludingGravity) {
            // Utilisation des valeurs brutes en m/s²
            controllerState.sensors.accel.x = event.accelerationIncludingGravity.x;
            controllerState.sensors.accel.y = event.accelerationIncludingGravity.y;
            controllerState.sensors.accel.z = event.accelerationIncludingGravity.z;
            
            // Affichage en m/s² dans l'interface de debug
            debugEl.innerText = `X: ${controllerState.sensors.accel.x.toFixed(2)} m/s² | Y: ${controllerState.sensors.accel.y.toFixed(2)} m/s²`;
            sendData();
        }
    }, true);
    
    // Si après 1 seconde rien ne bouge, on prévient l'utilisateur
    setTimeout(() => {
        if (controllerState.sensors.alpha === 0 && (controllerState.sensors.accel.x === 0 || controllerState.sensors.accel.x === null)) {
            debugEl.innerText = "Capteurs : Inactifs (Vérifiez HTTPS / Flags)";
            debugEl.style.color = "#f87171";
        }
    }, 1000);
}

btnJoin.onclick = () => {
    requestDevicePermissions();
};

// 4. Envoi des données vers le Raspberry Pi
let lastSend = 0;
function sendData() {
    const now = Date.now();
    if (now - lastSend > 30) { // Max ~33 FPS
        socket.emit('controller_data', controllerState);
        lastSend = now;
    }
}