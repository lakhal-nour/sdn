# Fichier: tests/network_tests.py
import time
import sys
import os
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from functools import partial

class DatacenterTopo(Topo):
    def build(self):
        spine1 = self.addSwitch('s1')
        spine2 = self.addSwitch('s2')
        leaf1 = self.addSwitch('s3')
        leaf2 = self.addSwitch('s4')
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')
        
        self.addLink(h1, leaf1)
        self.addLink(h2, leaf1)
        self.addLink(h3, leaf2)
        self.addLink(h4, leaf2)
        
        self.addLink(leaf1, spine1)
        self.addLink(leaf1, spine2)
        self.addLink(leaf2, spine1)
        self.addLink(leaf2, spine2)

def run_automated_tests():
    setLogLevel('info')
    info("*** 🏗️ Création du réseau NetDevOps...\n")
    
    topo = DatacenterTopo()
    switch_of13 = partial(OVSKernelSwitch, protocols='OpenFlow13')
    
    # On initialise Mininet
    net = Mininet(topo=topo, switch=switch_of13, controller=None)
    
    # On connecte le contrôleur Ryu
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    # CORRECTION : On démarre explicitement le contrôleur et on attend 3 secondes 
    # pour éviter le message "Unable to contact the remote controller"
    c0.start()
    time.sleep(3)
    
    # Maintenant on peut démarrer le réseau sereinement
    net.start()
    
    info("*** ⏳ Attente de 10s pour l'apprentissage du réseau...\n")
    time.sleep(10)

    info("*** 🔧 Injection de la règle ciblée : Bloquer UNIQUEMENT h1 vers h4...\n")
    dpids = ["0000000000000001", "0000000000000002", "0000000000000003", "0000000000000004"]
    for dpid in dpids:
        # 1. Activer le firewall
        os.system(f"curl -s -X PUT http://127.0.0.1:8080/firewall/module/enable/{dpid}")
        
        # 2. Règle spécifique : Bloquer TOUT trafic de 10.0.0.1 (h1) vers 10.0.0.4 (h4)
        rule_block = '{{"priority": 100, "dl_type": "IPv4", "nw_src": "10.0.0.1/32", "nw_dst": "10.0.0.4/32", "actions": "DENY"}}'
        os.system(f"curl -s -X POST -d '{rule_block}' http://127.0.0.1:8080/firewall/rules/{dpid}")
        
        # 3. Règle globale : Autoriser tout le reste (IPv4 et ARP)
        os.system(f"curl -s -X POST -d '{{\"priority\": 10, \"dl_type\": \"IPv4\", \"actions\": \"ALLOW\"}}' http://127.0.0.1:8080/firewall/rules/{dpid}")
        os.system(f"curl -s -X POST -d '{{\"priority\": 10, \"dl_type\": \"ARP\", \"actions\": \"ALLOW\"}}' http://127.0.0.1:8080/firewall/rules/{dpid}")

    info("*** ⏳ Application des règles...\n")
    time.sleep(5)

    h1, h2, h4 = net.get('h1', 'h2', 'h4')
    
    # --- TEST 1 : LE TRAFIC AUTORISÉ (h1 vers h2) ---
    info("*** 🟢 TEST 1: Ping autorisé (h1 vers h2). On s'attend à 0% dropped...\n")
    res1 = h1.cmd('ping -c 2 10.0.0.2')
    if "0% packet loss" in res1:
        info("   ✅ SUCCÈS : h1 communique parfaitement avec h2 !\n")
        test1_ok = True
    else:
        info("   ❌ ÉCHEC : Le trafic h1 -> h2 ne passe pas.\n")
        test1_ok = False

    # --- TEST 2 : LE TRAFIC BLOQUÉ (h1 vers h4) ---
    info("*** 🔴 TEST 2: Ping bloqué (h1 vers h4). On s'attend à 100% dropped...\n")
    res2 = h1.cmd('ping -c 2 10.0.0.4')
    if "100% packet loss" in res2 or "100% loss" in res2 or "errors" in res2:
        info("   ✅ SUCCÈS : Le Firewall bloque bien h1 vers h4 !\n")
        test2_ok = True
    else:
        info("   ❌ ÉCHEC : h1 arrive toujours à ping h4.\n")
        test2_ok = False

    net.stop()

    if test1_ok and test2_ok:
        info("\n🏆 RÉSULTAT FINAL : Workflow validé avec succès ! Le Firewall cible parfaitement.\n")
        sys.exit(0)
    else:
        info("\n💥 RÉSULTAT FINAL : Échec des tests.\n")
        sys.exit(1)

if __name__ == '__main__':
    run_automated_tests()