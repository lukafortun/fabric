#!../fabric-venv/bin/python3

import subprocess
import psutil

def get_current_connection_info():
    # Vérifier si l'interface Ethernet est active
    ethernet_interface = "eth0"  # Cela peut être différent selon votre système
    wifi_interface = "wlan0"  # Cela peut être différent selon votre système
    
    # Vérifier si on est connecté en Ethernet
    is_ethernet = ethernet_interface in psutil.net_if_addrs()

    # Récupérer le SSID WiFi (sur Linux avec nmcli)
    try:
        ssid = subprocess.check_output("nmcli -t -f active,ssid dev wifi | grep ^oui", shell=True).decode().strip().split(":")[1]
    except subprocess.CalledProcessError:
        ssid = None
    
    # Récupérer la puissance du signal WiFi (sur Linux avec nmcli)
    try:
        signal_strength = subprocess.check_output("nmcli -f IN-USE,SIGNAL dev wifi", shell=True).decode()
        signal_strength = [line for line in signal_strength.splitlines() if "*" in line]
        signal_strength = signal_strength[0].split("    ")[1].strip() if signal_strength else None
    except subprocess.CalledProcessError:
        signal_strength = None

    return {
        "SSID": ssid,
        "Signal Strength": signal_strength,
        "Is Ethernet": is_ethernet
    }

# Exemple d'utilisation
connection_info = get_current_connection_info()
print(connection_info)

