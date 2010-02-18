import sys
import ns3
import radiomobile
from pprint import pprint

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)

class Struct:
    """Struct/record-like class."""
    def __init__(self, name, **entries):
        self._name = name
        self.__dict__.update(entries)

    def __repr__(self):
        args = ('%s=%s' % (k, repr(v)) for (k, v) in 
            vars(self).iteritems() if not k.startswith("_"))
        return 'Struct %s (%s)' % (self._name, ', '.join(args))

def debug(line):
    """Output line to standard error."""
    sys.stderr.write(line + "\n")
    sys.stderr.flush()

def set_udp_client_server(server_node, server_address, client_node):
    echoServer = ns3.UdpEchoServerHelper(9)
    serverApps = echoServer.Install(server_node)
    serverApps.Start(ns3.Seconds(1.0))
    serverApps.Stop(ns3.Seconds(10.0))

    echoClient = ns3.UdpEchoClientHelper(server_address, 9)
    echoClient.SetAttribute("MaxPackets", ns3.UintegerValue(1))
    echoClient.SetAttribute("Interval", ns3.TimeValue(ns3.Seconds(1.0)))
    echoClient.SetAttribute("PacketSize", ns3.UintegerValue(1024))
    clientApps = echoClient.Install(client_node)
    clientApps.Start(ns3.Seconds(2.0))
    clientApps.Stop(ns3.Seconds(10.0))

def add_devices(nodeid2computer, nodes, devices):    
    for index in range(devices.GetN()):
        device = devices.Get(index)
        node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        computer = nodeid2computer[node.GetId()]
        computer.devices.append(device)

def add_interfaces(nodeid2computer, nodes, interfaces):
    for index in range(interfaces.GetN()):
        address = interfaces.GetAddress(index)
        node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        computer = nodeid2computer[node.GetId()]
        computer.addresses.append(address)

def create_network(report):
    computers = {}
    for name, attrs in report.units.iteritems():
        computer = Struct("computer", 
            node=ns3.Node(), 
            devices=[],
            addresses=[]) 
        computers[name] = computer
    nodeid2computer = dict((computer.node.GetId(), computer) 
        for computer in computers.values())

    # Internet stack
    stack = ns3.InternetStackHelper()
    for name, computer in computers.iteritems():
        stack.Install(computer.node)
    
    for net_index, (name, network) in enumerate(report.nets.iteritems()):
        ap_node = computers[network.node_member].node
        sta_nodes = ns3.NodeContainer()            
        debug("network '%s': ap_node='%s', sta_nodes=%s" % 
            (name, network.node_member, network.terminal_members))
        for name in network.terminal_members:
            sta_nodes.Add(computers[name].node)
                    
        # Wifi channel
        channel = ns3.YansWifiChannelHelper.Default()
        phy = ns3.YansWifiPhyHelper.Default()
        phy.SetChannel(channel.Create())

        # STA devices
        wifi = ns3.WifiHelper.Default()
        wifi.SetRemoteStationManager("ns3::AarfWifiManager")
        mac = ns3.NqosWifiMacHelper.Default()
        ssid = ns3.Ssid("ns-3-ssid")
        mac.SetType("ns3::NqstaWifiMac", 
            "Ssid", ns3.SsidValue(ssid),
            "ActiveProbing", ns3.BooleanValue(False))
        sta_devices = wifi.Install(phy, mac, sta_nodes)
        add_devices(nodeid2computer, sta_nodes, sta_devices)

        # AP devices
        mac = ns3.NqosWifiMacHelper.Default()
        mac.SetType ("ns3::NqapWifiMac", 
            "Ssid", ns3.SsidValue(ssid),
            "BeaconGeneration", ns3.BooleanValue(True),
            "BeaconInterval", ns3.TimeValue(ns3.Seconds(2.5)))
        ap_devices = wifi.Install(phy, mac, ap_node)
        add_devices(nodeid2computer, ap_node, ap_devices)
        
        # Set IP addresses
        address = ns3.Ipv4AddressHelper()
        netaddr = "10.1.%d.0" % net_index
        address.SetBase(ns3.Ipv4Address(netaddr), ns3.Ipv4Mask("255.255.255.0"))
        ap_interfaces = address.Assign(ap_devices)
        sta_interfaces = address.Assign(sta_devices)
        add_interfaces(nodeid2computer, ap_node, ap_interfaces)
        add_interfaces(nodeid2computer, sta_nodes, sta_interfaces)

        # Mobility
        mobility = ns3.MobilityHelper()
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        mobility.Install(ap_node)
        
        mobility = ns3.MobilityHelper()
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        mobility.Install(sta_nodes)

    ns3.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
              
    # Applications
    server = computers["CCATCCA"]
    client = computers["URCOS"]
    print
    pprint(computers)
    print "server:", server
    print "client:", client
    set_udp_client_server(server.node, server.addresses[0], client.node)
    #set_udp_client_server(server.node, server.interfaces["system"].address, client.node)

    # Tracing
    phy.EnablePcap("udp_echo", computers["JOSJOJAHUARINA 1"].devices[0])

def run_simulation(limit = None):
    if limit is not None:    
        ns3.Simulator.Stop(ns3.Seconds(limit))
    ns3.Simulator.Run()
    ns3.Simulator.Destroy()

def main(args):
    if len(args) != 1:
        debug("Usage: %s REPORT_TXT_PATH" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = radiomobile.RadioMobileReport(text_report_filename)
    create_network(report)
    run_simulation(10.0)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
