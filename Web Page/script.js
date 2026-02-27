
let socket;
let deviceId = 'phone_' + Math.random().toString(36).substr(2, 5);
const statusEl = document.getElementById('status');

// Fonction de capture séparée pour pouvoir l'arrêter proprement
function handleMotion(e) {
    const acc = e.accelerationIncludingGravity;
    if (!acc) return;

    document.getElementById('x').textContent = acc.x.toFixed(2);
    document.getElementById('y').textContent = acc.y.toFixed(2);
    document.getElementById('z').textContent = acc.z.toFixed(2);

    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({
            id: deviceId,
            x: acc.x, y: acc.y, z: acc.z,
            ts: Date.now()
        }));
    }
}

async function requestPermission() {
    // Cas spécifique pour iOS 13+
    if (typeof DeviceMotionEvent.requestPermission === 'function') {
        try {
            const permissionState = await DeviceMotionEvent.requestPermission();
            return permissionState === 'granted';
        } catch (error) {
            console.error(error);
            return false;
        }
    }
    // Pour les autres navigateurs (Android), on suppose que c'est OK si l'API existe
    return true;
}

document.getElementById('startButton').addEventListener('click', async () => {
    const isAllowed = await requestPermission();

    if (isAllowed) {
        // WebSocket - remplacez par votre IP locale (ex: ws://192.168.1.15:8765)
        socket = new WebSocket("ws://VOTRE_IP_LOCALE:8765");

        window.addEventListener('devicemotion', handleMotion);

        statusEl.textContent = "Statut : Connecté & Capture...";
        document.getElementById('startButton').disabled = true;
        document.getElementById('stopButton').disabled = false;
    } else {
        alert("Permission refusée ou non supportée.");
    }
});

document.getElementById('stopButton').addEventListener('click', () => {
    window.removeEventListener('devicemotion', handleMotion);
    if (socket) socket.close();

    statusEl.textContent = "Statut : Arrêté";
    document.getElementById('startButton').disabled = false;
    document.getElementById('stopButton').disabled = true;
});
