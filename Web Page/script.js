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
            btn.innerText = "OCCUPÉ";
        } else {
            btn.classList.replace('taken', 'available');
            btn.innerText = `JOUEUR ${i}`;
        }
    }
});

window.selectSlot = (num) => {
    document.getElementById('lobby-status').innerText = `Demande du slot ${num}...`;
    socket.emit('select_slot', num);
};

socket.on('slot_confirmed', (data) => {
    controllerState.id = `JOUEUR-${data.slot}`;
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

    calibStatus.innerText = "PRÊT !";
    setTimeout(() => {
        isCalibrating = false;
        calibOverlay.style.display = 'none';
        controllerUI.style.visibility = 'visible';
    }, 800);
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

// --- TRANSMISSION ---

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
    if (!controllerState.id || isCalibrating) return;
    const now = Date.now();
    if (now - lastSend > 30) { 
        socket.emit('controller_data', controllerState);
        lastSend = now;
    }
}

socket.on('connect', () => {
    statusEl.innerText = "● Connecté";
    statusEl.style.color = "#4ade80";
});