# Fichier: scripts/start_demo.py
import time
import sys
import subprocess
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from functools import partial

# On importe ta topologie
sys.path.append('.')
from topology.datacenter_topo import DatacenterTopo

def start_interactive_demo():
    setLogLevel('info')
    info("*** 🏗️ Démarrage de l'environnement de Démo NetDevOps...\n")
    
    topo = DatacenterTopo()
    switch_of13 = partial(OVSKernelSwitch, protocols='OpenFlow13')
    
    net = Mininet(topo=topo, switch=switch_of13, link=TCLink, controller=None)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    c0.start()
    time.sleep(3)
    net.start()
    
    info("*** ⏳ Attente de 5s pour l'apprentissage du réseau...\n")
    time.sleep(5)

    info("*** 🚀 Déploiement des politiques (Firewall & QoS) via Policy-as-Code...\n")
    subprocess.run(["python3", "scripts/deploy_policies.py"])
    
    info("\n" + "="*60 + "\n")
    info("🟢 RÉSEAU ACTIF ET MONITORING EN COURS !\n")
    info("👉 Allez sur Grafana (http://localhost:3000) pour voir les courbes.\n")
    info("👉 Générez du trafic ici en tapant :  h1 ping h2  ou  iperf h1 h2\n")
    info("👉 Tapez 'exit' pour fermer proprement le réseau.\n")
    info("="*60 + "\n")
    
    # 🌟 C'est ici la magie : on lance le CLI interactif ! Le script se met en pause ici.
    CLI(net)
    
    # Quand tu taperas "exit" dans le CLI, le code reprendra ici pour tout nettoyer.
    info("\n*** 🛑 Arrêt du réseau de démo...\n")
    net.stop()

if __name__ == '__main__':
    start_interactive_demo()