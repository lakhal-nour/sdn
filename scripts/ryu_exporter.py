# Fichier: scripts/ryu_exporter.py
import time
import requests
from prometheus_client import start_http_server, Gauge

# Définition des métriques (Bande passante envoyée et reçue par les ports des switchs)
TX_BYTES = Gauge('ryu_port_tx_bytes', 'Bytes transmis par le port', ['dpid', 'port_no'])
RX_BYTES = Gauge('ryu_port_rx_bytes', 'Bytes recus par le port', ['dpid', 'port_no'])

def fetch_metrics():
    try:
        # On interroge l'API REST de Ryu pour avoir les stats de tous les switchs
        response = requests.get("http://127.0.0.1:8080/stats/port/ALL")
        if response.status_code == 200:
            data = response.json()
            for dpid, ports in data.items():
                for port in ports:
                    # On ignore le port local du switch
                    if port['port_no'] != 'LOCAL':
                        # On met à jour Prometheus avec les nouvelles valeurs
                        TX_BYTES.labels(dpid=dpid, port_no=port['port_no']).set(port['tx_bytes'])
                        RX_BYTES.labels(dpid=dpid, port_no=port['port_no']).set(port['rx_bytes'])
    except Exception as e:
        print(f"Erreur de connexion a Ryu: {e}")

if __name__ == '__main__':
    # On démarre le serveur Prometheus sur le port 8000
    start_http_server(8000)
    print("🚀 SDN Exporter démarré sur le port 8000...")
    while True:
        fetch_metrics()
        time.sleep(5) # Mise à jour toutes les 5 secondes