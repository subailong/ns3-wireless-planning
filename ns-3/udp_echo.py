import sys
import ns3
from pprint import pprint

import radiomobile

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)

class Struct:
    """Struct/record-like class."""
    def __init__(self, _name, **entries):
        self._name = _name
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

def add_devices_to_node(network, ns3node_to_node, nodes, devices):  
    for index in range(devices.GetN()):
        ns3_device = devices.Get(index)
        ns3_node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        node = ns3node_to_node[ns3_node.GetId()]
        system = network.net_members[node.name].system
        device = Struct("device", ns3_device=ns3_device, interfaces=[])
        node.devices[system] = device

def add_interfaces_to_device(network, ns3node_to_node, nodes, interfaces):
    for index in range(interfaces.GetN()):
        address = interfaces.GetAddress(index)
        ns3_node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        node = ns3node_to_node[ns3_node.GetId()]
        system = network.net_members[node.name].system
        interface = Struct("interface", address=address) 
        node.devices[system].interfaces.append(interface)

def create_network(report):
    # Build nodes 
    nodes = {}
    for name, attrs in report.units.iteritems():
        node = Struct("node", name=name, ns3_node=ns3.Node(), devices={})
        nodes[name] = node
    ns3node_to_node = dict((node.ns3_node.GetId(), node) for node in nodes.values())

    # Internet stack
    stack = ns3.InternetStackHelper()
    for name, node in nodes.iteritems():
        stack.Install(node.ns3_node)
    
    for net_index, (name, network) in enumerate(report.nets.iteritems()):
        node_member = radiomobile.get_units_for_network(network, "Node")[0]
        terminal_members = radiomobile.get_units_for_network(network, "Terminal")
        ap_node = nodes[node_member].ns3_node
        sta_nodes = ns3.NodeContainer()            
        debug("Add network '%s'\n  ap_node = '%s'\n  sta_nodes = %s" % 
            (name, node_member, terminal_members))
        for name in terminal_members:
            sta_nodes.Add(nodes[name].ns3_node)
                    
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
        add_devices_to_node(network, ns3node_to_node, sta_nodes, sta_devices)

        # AP devices
        mac = ns3.NqosWifiMacHelper.Default()
        mac.SetType ("ns3::NqapWifiMac", 
            "Ssid", ns3.SsidValue(ssid),
            "BeaconGeneration", ns3.BooleanValue(True),
            "BeaconInterval", ns3.TimeValue(ns3.Seconds(2.5)))
        ap_devices = wifi.Install(phy, mac, ap_node)
        add_devices_to_node(network, ns3node_to_node, ap_node, ap_devices)
        
        # Set IP addresses
        address = ns3.Ipv4AddressHelper()
        netaddr = "10.1.%d.0" % net_index
        address.SetBase(ns3.Ipv4Address(netaddr), ns3.Ipv4Mask("255.255.255.0"))
        ap_interfaces = address.Assign(ap_devices)
        sta_interfaces = address.Assign(sta_devices)
        add_interfaces_to_device(network, ns3node_to_node, ap_node, ap_interfaces)
        add_interfaces_to_device(network, ns3node_to_node, sta_nodes, sta_interfaces)

        # Mobility
        mobility = ns3.MobilityHelper()
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        mobility.Install(ap_node)
        
        mobility = ns3.MobilityHelper()
        mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
        mobility.Install(sta_nodes)

    ns3.Ipv4GlobalRoutingHelper.PopulateRoutingTables()
    return Struct("Network", nodes=nodes, phy=phy)
              
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
    report = radiomobile.parse_report(text_report_filename)
    network = create_network(report)
    
    # Applications
    server = network.nodes["CCATCCA"]
    client = network.nodes["URCOS"]
    set_udp_client_server(server.ns3_node, 
        server.devices["Uuario Final PCMCIA"].interfaces[0].address, 
        client.ns3_node)

    # Tracing
    josjo1 = network.nodes["JOSJOJAHUARINA 1"]
    device = josjo1.devices['Josjo 1 Sectorial PC'].ns3_device
    network.phy.EnablePcap("udp_echo", device)
    
    run_simulation(10.0)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
