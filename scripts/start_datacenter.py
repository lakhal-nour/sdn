# Fichier: scripts/start_datacenter.py
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from functools import partial
import sys

# Import de ta topologie
sys.path.append('.')
from topology.datacenter_topo import DatacenterTopo

def start_prod():
    setLogLevel('info')
    info("*** 🏗️ Démarrage du Datacenter (Environnement de Production)...\n")
    
    topo = DatacenterTopo()
    switch_of13 = partial(OVSKernelSwitch, protocols='OpenFlow13')
    
    # Création du réseau avec QoS activée (TCLink)
    net = Mininet(topo=topo, link=TCLink, controller=None) # On ne laisse pas Mininet choisir
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6633)
    c0.start()
    net.start()
    # FORCE OPENFLOW 1.3 SUR TOUS LES SWITCHS
    for switch in net.switches:
        switch.cmd('ovs-vsctl set bridge', switch, 'protocols=OpenFlow13')
    
    info("\n" + "="*60 + "\n")
    info("🟢 DATACENTER EN LIGNE ET OPÉRATIONNEL !\n")
    info("👉 Le réseau tourne. En attente des règles du pipeline CI/CD...\n")
    info("👉 Tape 'exit' uniquement quand tu as fini ta journée.\n")
    info("="*60 + "\n")
    
    # Maintient le réseau en vie et ouvre la console
    CLI(net)
    
    net.stop()

if __name__ == '__main__':
    start_prod()