# tests/validate_lab.py
import subprocess
import sys
import time
import requests

RYU_HEALTH_URL = "http://127.0.0.1:8080/firewall/module/status"
TOPOLOGY_PROCESS_NAME = "start_lab_topology.py"


def run(cmd):
    return subprocess.run(cmd, shell=True, text=True, capture_output=True)


def main():
    print("=== Validation du lab persistant ===")
    time.sleep(5)

    # 1. Vérifier l'API REST de Ryu
    try:
        response = requests.get(RYU_HEALTH_URL, timeout=5)
        if response.status_code != 200:
            print(f"❌ API Ryu non saine : HTTP {response.status_code}")
            sys.exit(1)
        print("✅ API REST Ryu opérationnelle")
    except Exception as e:
        print(f"❌ Erreur API Ryu : {e}")
        sys.exit(1)

    # 2. Vérifier que la topologie persistante tourne
    topo_check = run(f"pgrep -f {TOPOLOGY_PROCESS_NAME}")
    if topo_check.returncode != 0:
        print("❌ La topologie persistante n'est pas en cours d'exécution")
        sys.exit(1)
    print("✅ Processus de topologie persistante détecté")

    # 3. Vérifier qu'OVS a bien des bridges
    ovs_check = run("sudo ovs-vsctl list-br")
    if ovs_check.returncode != 0:
        print("❌ Impossible de lire les bridges OVS")
        print(ovs_check.stderr)
        sys.exit(1)

    bridges = [line.strip() for line in ovs_check.stdout.splitlines() if line.strip()]
    if not bridges:
        print("❌ Aucun bridge OVS détecté")
        sys.exit(1)

    print(f"✅ Bridges OVS détectés : {', '.join(bridges)}")

    print("🏆 Validation du lab persistant réussie")
    sys.exit(0)


if __name__ == "__main__":
    main()