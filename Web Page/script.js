const socket = io();
        const statusEl = document.getElementById('connection-status');
        const debugEl = document.getElementById('debug');
        const btnPerms = document.getElementById('request-perms');

        // État de la manette mis à jour avec H et Pause
        let controllerState = {
            id: Math.random().toString(36).substring(7),
            buttons: { 
                H: false, 
                Pause: false 
            },
            sensors: { 
                alpha: 0, 
                beta: 0, 
                gamma: 0 
            }
        };

        // Gestion de la connexion Socket.io
        socket.on('connect', () => {
            statusEl.innerText = "● Connecté au Raspberry Pi";
            statusEl.style.color = "#2ecc71";
        });

        socket.on('disconnect', () => {
            statusEl.innerText = "○ Déconnecté";
            statusEl.style.color = "#e74c3c";
        });

        /**
         * Configure les événements tactiles pour un bouton
         */
        function setupButton(id, key) {
            const el = document.getElementById(id);
            
            const updateState = (isActive) => {
                controllerState.buttons[key] = isActive;
                el.classList.toggle('active', isActive);
                sendData();
            };

            // Touch Events (Mobile)
            el.addEventListener('touchstart', (e) => { 
                e.preventDefault(); 
                updateState(true); 
            });
            el.addEventListener('touchend', (e) => { 
                e.preventDefault(); 
                updateState(false); 
            });

            // Mouse Events (Fallback Desktop pour test)
            el.addEventListener('mousedown', () => updateState(true));
            el.addEventListener('mouseup', () => updateState(false));
        }

        // Initialisation des nouveaux boutons
        setupButton('btn-H', 'H');
        setupButton('btn-Pause', 'Pause');

        /**
         * Capture les données d'orientation du téléphone
         */
        function handleOrientation(event) {
            // alpha: boussole, beta: avant/arrière, gamma: gauche/droite
            controllerState.sensors.alpha = Math.round(event.alpha || 0);
            controllerState.sensors.beta = Math.round(event.beta || 0);
            controllerState.sensors.gamma = Math.round(event.gamma || 0);
            
            debugEl.innerHTML = `Boussole: ${controllerState.sensors.alpha}° | Incl: ${controllerState.sensors.beta}°, ${controllerState.sensors.gamma}°`;
            sendData();
        }

        /**
         * Envoie les données au serveur avec limitation de fréquence (Throttling)
         */
        let lastSendTime = 0;
        const SEND_INTERVAL = 30; // ms (environ 33 FPS)

        function sendData() {
            const now = Date.now();
            if (now - lastSendTime > SEND_INTERVAL) {
                socket.emit('controller_data', controllerState);
                lastSendTime = now;
            }
        }

        /**
         * Gestion des permissions pour l'accéléromètre/gyroscope
         */
        btnPerms.onclick = () => {
            // Vérification si l'API de permission existe (iOS)
            if (typeof DeviceOrientationEvent !== 'undefined' && 
                typeof DeviceOrientationEvent.requestPermission === 'function') {
                
                DeviceOrientationEvent.requestPermission()
                    .then(response => {
                        if (response === 'granted') {
                            activateSensors();
                        } else {
                            alert("Permission refusée pour les capteurs.");
                        }
                    })
                    .catch(console.error);
            } else {
                // Pour les appareils Android ou navigateurs n'exigeant pas de permission explicite
                activateSensors();
            }
        };

        function activateSensors() {
            window.addEventListener('deviceorientation', handleOrientation);
            btnPerms.style.display = 'none';
            debugEl.innerText = "Capteurs : Activés";
        }