const socket = io({
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000
});

const lobby = document.getElementById('lobby');
const controllerUI = document.getElementById('controller-ui');
const calibOverlay = document.getElementById('calibration-overlay');
const calibProgressBar = document.getElementById('calib-progress-bar');
const calibStatus = document.getElementById('calib-status');
const statusEl = document.getElementById('connection-status');

let controllerState = {
    id: null,
    buttons: { H: false, Pause: false },
    sensors: { alpha: 0, beta: 0, gamma: 0, accel: { x: 0, y: 0, z: 0 } }
};

let sensorOffsets = { x: 0, y: 0, z: 0 };
let isCalibrating = false;
let rawAccel = { x: 0, y: 0, z: 0 };
let wakeLock = null;

// --- GESTION DE L'ÉCRAN (WAKE LOCK) ---

async function requestWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log("Wake Lock actif : l'écran ne s'éteindra pas.");
        }
    } catch (err) {
        console.warn("Échec du Wake Lock:", err.message);
    }
}

// --- GESTION DES SLOTS ---

socket.on('slots_update', (slots) => {
    for (let i = 1; i <= 4; i++) {
        const btn = document.getElementById(`slot-${i}`);
        if (!btn) continue;
        if (slots[i]) {
            btn.classList.replace('available', 'taken');
            btn.innerText = "TAKEN";
        } else {
            btn.classList.replace('taken', 'available');
            btn.innerText = `PLAYER ${i}`;
        }
    }
});

window.selectSlot = (num) => {
    document.getElementById('lobby-status').innerText = `Waiting for slot ${num}...`;
    socket.emit('select_slot', num);
};

socket.on('slot_confirmed', (data) => {
    controllerState.id = `PLAYER-${data.slot}`;
    requestWakeLock(); // Activer le Wake Lock dès que le jeu commence
    startCalibrationFlow();
});

socket.on('force_reset', () => {
    window.location.reload(); 
});

socket.on('vibrate', (data) => {
    if (navigator.vibrate) {
        navigator.vibrate(data.duration || 50);
    }
});

// --- CALIBRATION ---

async function startCalibrationFlow() {
    lobby.style.display = 'none';
    calibOverlay.style.display = 'flex';
    controllerUI.style.visibility = 'hidden';
    
    try {
        if (typeof DeviceOrientationEvent !== 'undefined' && typeof DeviceOrientationEvent.requestPermission === 'function') {
            await DeviceOrientationEvent.requestPermission();
            await DeviceMotionEvent.requestPermission();
        }
    } catch (e) { console.error(e); }

    initSensorsListeners();
    await new Promise(r => setTimeout(r, 3000));
    
    isCalibrating = true;
    let samples = [];
    const targetSamples = 60; 
    
    const checkInterval = setInterval(() => {
        samples.push({ ...rawAccel });
        let progress = (samples.length / targetSamples) * 100;
        calibProgressBar.style.width = progress + "%";
        calibStatus.innerText = `Calibration : ${Math.round(progress)}%`;

        if (samples.length >= targetSamples) {
            clearInterval(checkInterval);
            finalizeCalibration(samples);
        }
    }, 30);
}

function finalizeCalibration(samples) {
    const sum = samples.reduce((acc, s) => ({
        x: acc.x + s.x, y: acc.y + s.y, z: acc.z + s.z
    }), { x: 0, y: 0, z: 0 });

    sensorOffsets = {
        x: sum.x / samples.length,
        y: sum.y / samples.length,
        z: sum.z / samples.length
    };

    calibStatus.innerText = "Ready !";
    setTimeout(() => {
        isCalibrating = false;
        calibOverlay.style.display = 'none';
        controllerUI.style.visibility = 'visible';
    }, 800);
}

// --- TRANSMISSION OPTIMISÉE ---

let lastSendData = {
    b: [false, false],
    s: [0, 0, 0, [0, 0, 0]]
};

let lastSendTime = 0;
const SEND_INTERVAL = 25; // ~40Hz, bon compromis réactivité/charge
const SENSOR_THRESHOLD = 0.8; // Seuil de changement pour envoyer (évite le jitter)

function sendData(force = false) {
    if (!controllerState.id || isCalibrating) return;

    const now = Date.now();
    if (!force && (now - lastSendTime < SEND_INTERVAL)) return;

    // On prépare un format COMPACT pour réduire le payload JSON
    // b: [Press, Back], s: [alpha, beta, gamma, [ax, ay, az]]
    const currentData = {
        b: [controllerState.buttons.Press || false, controllerState.buttons.Back || false],
        s: [
            controllerState.sensors.alpha,
            controllerState.sensors.beta,
            controllerState.sensors.gamma,
            [
                parseFloat(controllerState.sensors.accel.x.toFixed(3)),
                parseFloat(controllerState.sensors.accel.y.toFixed(3)),
                parseFloat(controllerState.sensors.accel.z.toFixed(3))
            ]
        ]
    };

    // Vérification si changement significatif (Delta compression manuelle)
    const hasButtonChange = currentData.b[0] !== lastSendData.b[0] || currentData.b[1] !== lastSendData.b[1];
    
    const hasSensorChange = 
        Math.abs(currentData.s[0] - lastSendData.s[0]) > SENSOR_THRESHOLD ||
        Math.abs(currentData.s[1] - lastSendData.s[1]) > SENSOR_THRESHOLD ||
        Math.abs(currentData.s[2] - lastSendData.s[2]) > SENSOR_THRESHOLD ||
        Math.abs(currentData.s[3][0] - lastSendData.s[3][0]) > 0.1; // Accel plus sensible

    if (force || hasButtonChange || hasSensorChange) {
        socket.emit('controller_data', currentData);
        lastSendData = JSON.parse(JSON.stringify(currentData));
        lastSendTime = now;
    }
}

// --- CAPTEURS ---

function initSensorsListeners() {
    window.addEventListener('deviceorientation', (event) => {
        controllerState.sensors.alpha = Math.round(event.alpha || 0);
        controllerState.sensors.beta = Math.round(event.beta || 0);
        controllerState.sensors.gamma = Math.round(event.gamma || 0);
        sendData();
    }, true);

    window.addEventListener('devicemotion', (event) => {
        if (event.accelerationIncludingGravity) {
            rawAccel.x = event.accelerationIncludingGravity.x;
            rawAccel.y = event.accelerationIncludingGravity.y;
            rawAccel.z = event.accelerationIncludingGravity.z;

            if (!isCalibrating) {
                controllerState.sensors.accel.x = rawAccel.x - sensorOffsets.x;
                controllerState.sensors.accel.y = rawAccel.y - sensorOffsets.y;
                controllerState.sensors.accel.z = rawAccel.z - sensorOffsets.z;
                sendData();
            }
        }
    }, true);
}

// --- BOUTONS ---

function setupButton(id, key) {
    const el = document.getElementById(id);
    if (!el) return;
    const update = (state) => {
        controllerState.buttons[key] = state;
        el.classList.toggle('active', state);
        sendData(true); // Forcer l'envoi lors d'un appui bouton
    };
    el.addEventListener('touchstart', (e) => { e.preventDefault(); update(true); });
    el.addEventListener('touchend', (e) => { e.preventDefault(); update(false); });
    el.addEventListener('mousedown', (e) => { e.preventDefault(); update(true); });
    el.addEventListener('mouseup', (e) => { e.preventDefault(); update(false); });
}

setupButton('btn-H', 'Press');
setupButton('btn-Pause', 'Back');

socket.on('connect', () => {
    statusEl.innerText = "● Connected";
    statusEl.style.color = "#4ade80";
});