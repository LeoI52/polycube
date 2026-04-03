import os
import socket
import ssl
import threading
import time

def check_files():
    print("--- 1. Vérification des fichiers ---")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cert = os.path.join(current_dir, "SSL/cert.pem")
    key = os.path.join(current_dir, "SSL/key.pem")
    
    for f in [cert, key]:
        if os.path.exists(f):
            print(f"[OK] Trouvé: {f}")
            print(f"     Taille: {os.path.getsize(f)} octets")
        else:
            print(f"[ERREUR] Manquant: {f}")

def check_network():
    print("\n--- 2. Vérification Réseau ---")
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Nom d'hôte: {hostname}")
    print(f"IP locale détectée: {local_ip}")
    print("Note: Vous devez utiliser cette IP pour vous connecter depuis votre téléphone.")

def check_port_4000():
    print("\n--- 3. Vérification du Port 4000 ---")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    result = sock.connect_ex(('127.0.0.1', 4000))
    if result == 0:
        print("[OK] Quelque chose écoute sur le port 4000.")
    else:
        print("[INFO] Le port 4000 est libre (ou le serveur n'est pas lancé).")
    sock.close()

def test_gpio():
    print("\n--- 4. Test rapide GPIO ---")
    try:
        from gpiozero import LED, RGBLED
        print("[OK] Bibliothèque gpiozero trouvée.")
        # Test très court
        led = LED(27)
        print("Allumage LED 27 (G1) pendant 1s...")
        led.on()
        time.sleep(1)
        led.off()
        print("[OK] Test GPIO terminé.")
    except Exception as e:
        print(f"[ERREUR] GPIO: {e}")

if __name__ == "__main__":
    print("=== DIAGNOSTIC POLYCUBE ===\n")
    check_files()
    check_network()
    check_port_4000()
    test_gpio()
    print("\n=== FIN DU DIAGNOSTIC ===")
