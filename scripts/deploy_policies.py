# Fichier: scripts/deploy_policies.py
import os
import json

def deploy_firewall(dpids):
    print("*** 🛡️ Lecture et injection des politiques Firewall (Policy as Code)...")
    policy_path = os.path.join(os.path.dirname(__file__), '../controller/policies/firewall.json')
    
    with open(policy_path, 'r') as f:
        policies = json.load(f)

    for dpid in dpids:
        # 1. Activer le firewall sur le switch
        os.system(f"curl -s -X PUT http://127.0.0.1:8080/firewall/module/enable/{dpid} > /dev/null")
        
        # 2. Appliquer les règles spécifiques (ex: Bloquer h1 -> h4)
        for rule in policies["specific_rules"]:
            rule_json = json.dumps(rule)
            os.system(f"curl -s -X POST -d '{rule_json}' http://127.0.0.1:8080/firewall/rules/{dpid} > /dev/null")
            
        # 3. Appliquer les règles globales (ex: ALLOW ALL pour le reste)
        for rule in policies["global_rules"]:
            rule_json = json.dumps(rule)
            os.system(f"curl -s -X POST -d '{rule_json}' http://127.0.0.1:8080/firewall/rules/{dpid} > /dev/null")

def deploy_qos(dpids):
    print("*** 📊 Lecture et injection des politiques QoS (Policy as Code)...")
    policy_path = os.path.join(os.path.dirname(__file__), '../controller/policies/qos.json')
    
    # On vérifie si le fichier QoS existe avant de le charger
    if not os.path.exists(policy_path):
        print("    ⚠️ Fichier qos.json introuvable, QoS ignorée.")
        return

    with open(policy_path, 'r') as f:
        qos_data = json.load(f)

    for dpid in dpids:
        # 1. Créer les compteurs/limiteurs (Meters)
        if "meters" in qos_data:
            for meter in qos_data["meters"]:
                meter_payload = {"dpid": int(dpid)}
                meter_payload.update(meter)
                # Note: On envoie ça à l'API stats native de Ryu
                os.system(f"curl -s -X POST -d '{json.dumps(meter_payload)}' http://127.0.0.1:8080/stats/meterentry/add > /dev/null")
        
        # 2. Appliquer les règles QoS (Lier le trafic au Meter)
        if "qos_rules" in qos_data:
            for rule in qos_data["qos_rules"]:
                rule_payload = {"dpid": int(dpid)}
                rule_payload.update(rule)
                os.system(f"curl -s -X POST -d '{json.dumps(rule_payload)}' http://127.0.0.1:8080/stats/flowentry/add > /dev/null")

if __name__ == '__main__':
    # La liste de tes switches
    switches = ["0000000000000001", "0000000000000002", "0000000000000003", "0000000000000004"]
    switches_int = ["1", "2", "3", "4"] # Ryu utilise parfois des entiers pour les stats/meters
    
    # 1. On déploie le Firewall
    deploy_firewall(switches)
    
    # 2. On déploie la QoS
    deploy_qos(switches_int)
    
    print("*** ✅ Toutes les politiques (Firewall + QoS) ont été appliquées avec succès !")