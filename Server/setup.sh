#!/bin/bash

# --- CONFIGURATION ---
PROJECT_ROOT=$(pwd)
SERVER_DIR="$PROJECT_ROOT/Server"
VENV_DIR="$PROJECT_ROOT/.venv"

echo "-------------------------------------------------------"
echo "   POLYCUBE OS - Installation & Lancement (RPi)        "
echo "-------------------------------------------------------"

# 1. Mise à jour des dépendances système (SDL2 pour Pygame)
echo "[1/5] Vérification des dépendances système..."
sudo apt update
sudo apt install -y python3-venv python3-pip \
    libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev \
    libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev \
    libfreetype6-dev

# 2. Création de l'environnement virtuel si inexistant
if [ ! -d "$VENV_DIR" ]; then
    echo "[2/5] Création de l'environnement virtuel Python..."
    python3 -m venv "$VENV_DIR"
fi

# 3. Installation des paquets Python
echo "[3/5] Installation des dépendances Python..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install flask flask-socketio eventlet pygame

# 4. Vérification SSL (Crucial pour les capteurs mobiles)
echo "[4/5] Vérification des certificats SSL..."
if [ ! -f "$SERVER_DIR/cert.pem" ] || [ ! -f "$SERVER_DIR/key.pem" ]; then
    echo "      /!\ ATTENTION : Fichiers SSL manquants dans $SERVER_DIR"
    echo "      Les capteurs de mouvement ne fonctionneront probablement pas sur smartphone via HTTP."
    echo "      Générez des certificats auto-signés ou utilisez un tunnel HTTPS."
else
    echo "      [OK] Certificats SSL détectés."
fi

# 5. Lancement de l'application
echo "[5/5] Démarrage de la console Polycube..."
echo "-------------------------------------------------------"
cd "$SERVER_DIR"

# On s'assure que le chemin Python inclut bien le dossier Server pour les imports
export PYTHONPATH=$PYTHONPATH:$SERVER_DIR

# Exécution du launcher
"$VENV_DIR/bin/python3" main_console.py

# Fin du script
echo "-------------------------------------------------------"
echo "Console arrêtée."