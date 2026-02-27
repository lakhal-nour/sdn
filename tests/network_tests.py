# Fichier: tests/network_tests.py
import time
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.topo import Topo
from mininet.cli import CLI
from mininet.log import setLogLevel, info

class SimpleTreeTopo(Topo):
    def build(self):
        # Création de la topologie (identique à ton --topo tree,depth=2,fanout=2)
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')

        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        h3 = self.addHost('h3', ip='10.0.0.3')
        h4 = self.addHost('h4', ip='10.0.0.4')

        self.addLink(s2, h1)
        self.addLink(s2, h2)
        self.addLink(s3, h3)
        self.addLink(s3, h4)
        self.addLink(s1, s2)
        self.addLink(s1, s3)

def run_automated_tests():
    setLogLevel('info')
    info("*** 🏗️ Création du réseau NetDevOps...\n")
    
    topo = SimpleTreeTopo()
    # Connexion au contrôleur Ryu Docker (port 6653)
    net = Mininet(topo=topo, switch=OVSKernelSwitch, controller=None)
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)
    
    net.start()
    
    info("*** ⏳ Attente de 15 secondes pour que Ryu et Ansible injectent les règles Firewall...\n")
    time.sleep(15)

    info("*** 🛡️ TEST 1: Vérification du blocage ICMP (Pingall)...\n")
    # On s'attend à 100% de perte (drop)
    dropped = net.pingAll()
    if dropped == 100.0:
        info("✅ TEST 1 RÉUSSI : Le pare-feu bloque bien l'ICMP (Zero Trust) !\n")
    else:
        info(f"❌ TEST 1 ÉCHOUÉ : Le ping est passé (Perte: {dropped}%). Le pare-feu a un problème.\n")

    info("*** 🌐 TEST 2: Vérification du trafic TCP (Web/Applicatif)...\n")
    h1, h4 = net.get('h1', 'h4')
    h4.cmd('iperf -s &') # Lance le serveur TCP en arrière-plan
    time.sleep(2)
    result = h1.cmd('iperf -c 10.0.0.4 -t 3') # Test client
    
    if "Connection failed" in result or "refused" in result:
        info("❌ TEST 2 ÉCHOUÉ : Le trafic TCP est bloqué.\n")
    else:
        info("✅ TEST 2 RÉUSSI : Le trafic TCP passe parfaitement (Règle ALLOW opérationnelle) !\n")

    info("*** 🛑 Arrêt du réseau virtuel...\n")
    net.stop()

if __name__ == '__main__':
    run_automated_tests()
