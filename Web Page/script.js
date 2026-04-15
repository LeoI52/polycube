const socket = io({
    reconnection: true,
    reconnectionAttempts: 10,
    reconnectionDelay: 1000
});

// Éléments UI
const lobby = document.getElementById('lobby');
const controllerUI = document.getElementById('controller-ui');
const calibOverlay = document.getElementById('calibration-overlay');
const calibProgressBar = document.getElementById('calib-progress-bar');
const calibStatus = document.getElementById('calib-status');
const statusEl = document.getElementById('connection-status');

// État du contrôleur
let controllerState = {
    id: null,
    buttons: { Press: false, Back: false },
    sensors: { alpha: 0, beta: 0, gamma: 0, accel: { x: 0, y: 0, z: 0 } }
};

// Offsets de calibration
let sensorOffsets = { 
    x: 0, y: 0, z: 0, 
    alpha: 0, beta: 0, gamma: 0 
};

// Valeurs brutes en temps réel
let rawAccel = { x: 0, y: 0, z: 0 };
let rawRotation = { alpha: 0, beta: 0, gamma: 0 };

let isCalibrating = false;
let wakeLock = null;

// --- GESTION DE L'ÉCRAN (WAKE LOCK) ---
async function requestWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
        }
    } catch (err) {
        console.warn("Wake Lock fail:", err.message);
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
    requestWakeLock();
    startCalibrationFlow();
});

socket.on('force_reset', () => window.location.reload());

socket.on('vibrate', (data) => {
    if (navigator.vibrate) navigator.vibrate(data.duration || 50);
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
    } catch (e) { console.error("Permission denied", e); }

    initSensorsListeners();
    
    // Attente de stabilisation avant de commencer à enregistrer
    calibStatus.innerText = "Hold steady...";
    await new Promise(r => setTimeout(r, 2000));
    
    isCalibrating = true;
    let samples = [];
    const targetSamples = 60; 
    
    const checkInterval = setInterval(() => {
        // On capture les snapshots des deux capteurs
        samples.push({ 
            acc: { ...rawAccel }, 
            rot: { ...rawRotation } 
        });

        let progress = (samples.length / targetSamples) * 100;
        calibProgressBar.style.width = progress + "%";
        calibStatus.innerText = `Calibrating: ${Math.round(progress)}%`;

        if (samples.length >= targetSamples) {
            clearInterval(checkInterval);
            finalizeCalibration(samples);
        }
    }, 30);
}

function finalizeCalibration(samples) {
    const count = samples.length;
    const sum = samples.reduce((acc, s) => ({
        x: acc.x + s.acc.x, y: acc.y + s.acc.y, z: acc.z + s.acc.z,
        a: acc.a + s.rot.alpha, b: acc.b + s.rot.beta, g: acc.g + s.rot.gamma
    }), { x: 0, y: 0, z: 0, a: 0, b: 0, g: 0 });

    sensorOffsets = {
        x: sum.x / count, y: sum.y / count, z: sum.z / count,
        alpha: sum.a / count, beta: sum.b / count, gamma: sum.g / count
    };

    calibStatus.innerText = "Ready!";
    setTimeout(() => {
        isCalibrating = false;
        calibOverlay.style.display = 'none';
        controllerUI.style.visibility = 'visible';
    }, 800);
}

// --- TRANSMISSION ---
let lastSendData = { b: [false, false], s: [0, 0, 0, [0, 0, 0]] };
let lastSendTime = 0;
const SEND_INTERVAL = 25; 
const SENSOR_THRESHOLD = 0.5; 

function sendData(force = false) {
    if (!controllerState.id || isCalibrating) return;

    const now = Date.now();
    if (!force && (now - lastSendTime < SEND_INTERVAL)) return;

    const currentData = {
        b: [controllerState.buttons.Press, controllerState.buttons.Back],
        s: [
            controllerState.sensors.alpha,
            controllerState.sensors.beta,
            controllerState.sensors.gamma,
            [
                parseFloat(controllerState.sensors.accel.x.toFixed(2)),
                parseFloat(controllerState.sensors.accel.y.toFixed(2)),
                parseFloat(controllerState.sensors.accel.z.toFixed(2))
            ]
        ]
    };

    const hasButtonChange = currentData.b[0] !== lastSendData.b[0] || currentData.b[1] !== lastSendData.b[1];
    const hasSensorChange = 
        Math.abs(currentData.s[0] - lastSendData.s[0]) > SENSOR_THRESHOLD ||
        Math.abs(currentData.s[1] - lastSendData.s[1]) > SENSOR_THRESHOLD ||
        Math.abs(currentData.s[2] - lastSendData.s[2]) > SENSOR_THRESHOLD;

    if (force || hasButtonChange || hasSensorChange) {
        socket.emit('controller_data', currentData);
        lastSendData = JSON.parse(JSON.stringify(currentData));
        lastSendTime = now;
    }
}

// --- CAPTEURS ---
function initSensorsListeners() {
    window.addEventListener('deviceorientation', (event) => {
        rawRotation.alpha = event.alpha || 0;
        rawRotation.beta = event.beta || 0;
        rawRotation.gamma = event.gamma || 0;

        if (!isCalibrating) {
            // On soustrait l'offset pour centrer à 0
            controllerState.sensors.alpha = Math.round(rawRotation.alpha - sensorOffsets.alpha);
            controllerState.sensors.beta = Math.round(rawRotation.beta - sensorOffsets.beta);
            controllerState.sensors.gamma = Math.round(rawRotation.gamma - sensorOffsets.gamma);
            sendData();
        }
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
        sendData(true);
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