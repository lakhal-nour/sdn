
# topology/start_lab_topology.py
import time
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.log import setLogLevel, info
from topology.datacenter_topo import DatacenterTopo

def main():
    setLogLevel('info')
    info("*** Starting persistent datacenter topology...\n")

    topo = DatacenterTopo()
    net = Mininet(topo=topo, switch=OVSKernelSwitch, controller=None, autoSetMacs=True)

    c0 = net.addController(
        'c0',
        controller=RemoteController,
        ip='127.0.0.1',
        port=6633
    )

    net.start()
    info("*** Persistent lab topology is running.\n")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        info("*** Stopping persistent lab topology...\n")
        net.stop()

if __name__ == "__main__":
    main()