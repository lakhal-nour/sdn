from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Config
RYU_URL = "http://127.0.0.1:8080"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"🔔 Alerte reçue : {data}")
    
    for alert in data.get('alerts', []):
        if alert['status'] == 'firing':
            # On récupère l'IP source de l'alerte (label envoyé par Prometheus)
            src_ip = alert['labels'].get('src_ip')
            if src_ip:
                print(f"🚨 Détection de trafic anormal depuis {src_ip}. Blocage en cours...")
                block_ip(src_ip)
                
    return jsonify({"status": "success"}), 200

def block_ip(ip):
    # Appel à l'API REST du Firewall Ryu
    # Note : Vérifie le chemin exact de ton API Ryu Firewall
    payload = {
        "nw_src": ip,
        "nw_proto": "ICMP", # ou TCP/UDP
        "action": "DENY"
    }
    try:
        r = requests.post(f"{RYU_URL}/firewall/rules/0000000000000001", json=payload)
        print(f"✅ Réponse Ryu : {r.status_code}")
    except Exception as e:
        print(f"❌ Erreur Ryu : {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)