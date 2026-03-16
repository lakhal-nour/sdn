# Fichier: topology/datacenter_topo.py
from mininet.topo import Topo

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
        
        # 🚦 QOS APPLIQUÉE ICI : On limite le lien de h1 à 10 Mbps
        self.addLink(h1, leaf1, bw=10) 
        
        # Les autres liens n'ont pas de limite (1000 Mbps par défaut)
        self.addLink(h2, leaf1)
        self.addLink(h3, leaf2)
        self.addLink(h4, leaf2)
        
        self.addLink(leaf1, spine1)
        self.addLink(leaf1, spine2)
        self.addLink(leaf2, spine1)
        self.addLink(leaf2, spine2)