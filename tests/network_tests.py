# Fichier: tests/network_tests.py
import time
import sys
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.topo import Topo
from mininet.log import setLogLevel, info
from functools import partial

class DatacenterTopo(Topo):
    def build(self):
        # 1. Spines (Couche Core / Cœur de réseau)
        spine1 = self.addSwitch('s1') # Nommé s1 pour que tes règles Ansible actuelles fonctionnent
        spine2 = self.addSwitch('s2')

        # 2. Leaves (Couche Accès / Racks)
        leaf1 = self.addSwitch('s3')
        leaf2 = self.addSwitch('s4')

        # 3. Hosts (Serveurs)
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')

        # Connexions Serveurs <-> Racks (Leaves)
        self.addLink(h1, leaf1)
        self.addLink(h2, leaf1)
        self.addLink(h3, leaf2)
        self.addLink(h4, leaf2)

        # Connexions Racks (Leaves) <-> Cœur (Spines) - Chaque Leaf va vers chaque Spine
        self.addLink(leaf1, spine1)
        self.addLink(leaf1, spine2)
        self.addLink(leaf2, spine1)
        self.addLink(leaf2, spine2)

def run_automated_tests():
    setLogLevel('info')
    info("*** 🏗️ Création du réseau NetDevOps (Topologie Datacenter)...\n")
    
    topo = DatacenterTopo()
    
    # 🔴 LA CORRECTION EST ICI : Forcer OpenFlow 1.3 pour que le Firewall Ryu ne plante pas
    switch_of13 = partial(OVSKernelSwitch, protocols='OpenFlow13')
    
    # Utilisation de switch_of13 au lieu de OVSKernelSwitch
    net = Mininet(topo=topo, switch=switch_of13, controller=None)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    net.start()
    
    info("*** ⏳ Attente de 40 secondes pour que Ryu et Ansible injectent les règles Firewall...\n")
    time.sleep(40)

    # 📊 VARIABLES POUR LE PIPELINE GITHUB
    test1_ok = False
    test2_ok = False

    info("*** 🛡️ TEST 1: Vérification du blocage ICMP (Pingall)...\n")
    dropped = net.pingAll()
    if dropped == 100.0:
        info("✅ TEST 1 RÉUSSI : Le pare-feu bloque bien l'ICMP !\n")
        test1_ok = True
    else:
        info(f"❌ TEST 1 ÉCHOUÉ : Le ping est passé (Perte: {dropped}%).\n")
        test1_ok = False

    info("*** 🌐 TEST 2: Vérification du trafic TCP (Web/Applicatif)...\n")
    h1, h4 = net.get('h1', 'h4')
    h4.cmd('iperf -s &') 
    time.sleep(2)
    result = h1.cmd('iperf -c 10.0.0.4 -t 3') 
    
    if "Connection failed" in result or "refused" in result:
        info("❌ TEST 2 ÉCHOUÉ : Le trafic TCP est bloqué.\n")
        test2_ok = False
    else:
        info("✅ TEST 2 RÉUSSI : Le trafic TCP passe parfaitement !\n")
        test2_ok = True

    info("*** 🛑 Arrêt du réseau virtuel...\n")
    net.stop()

    # 🛑 DÉCISION FINALE POUR GITHUB ACTIONS
    if test1_ok and test2_ok:
        info("🟢 TOUS LES TESTS SONT PASSÉS. Le Pipeline CI/CD va valider ce build.\n")
        sys.exit(0)
    else:
        info("🔴 ÉCHEC DES TESTS. Le Pipeline CI/CD va rejeter ce build.\n")
        sys.exit(1)

if __name__ == '__main__':
    run_automated_tests()