import sys
import ns3
from pprint import pprint

import radiomobile

verbose_level = 0

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
    if verbose_level > 0:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()

def add_devices_to_node(network, ns3node_to_node, nodes, devices, phy_helper):
    """Add new devices to node.devices dictionary."""
    for index in range(devices.GetN()):
        ns3_device = devices.Get(index)
        ns3_node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        node = ns3node_to_node[ns3_node.GetId()]
        system = network.net_members[node.name].system
        device = Struct("Device",
            ns3_device=ns3_device,
            phy_helper=phy_helper,
            interfaces=[])
        node.devices[system] = device

def add_interfaces_to_device(network, ns3node_to_node, nodes, interfaces):
    """Add new devices to node.devices[system].interfaces list."""
    for index in range(interfaces.GetN()):
        address = interfaces.GetAddress(index)
        ns3_node = (nodes if type(nodes) == ns3.Node else nodes.Get(index))
        node = ns3node_to_node[ns3_node.GetId()]
        system = network.net_members[node.name].system
        interface = Struct("Interface", address=address) 
        node.devices[system].interfaces.append(interface)

def create_network_from_report_file(filename):
    """Create a network Struct from a RadioMobile text-report filename."""
    report = radiomobile.parse_report(filename)
    return create_network(report) 

def create_network(report):
    """Create a network Struct from a RadioMobile parsed text report."""
    nodes = {}
    for name, attrs in report.units.iteritems():
        node = Struct("Node", name=name, ns3_node=ns3.Node(), devices={})
        nodes[name] = node
    ns3node_to_node = dict((node.ns3_node.GetId(), node) for node in nodes.values())

    # Internet stack
    stack = ns3.InternetStackHelper()
    for name, node in nodes.iteritems():
        stack.Install(node.ns3_node)
    
    for net_index, (name, network) in enumerate(report.nets.iteritems()):
        node_members = radiomobile.get_units_for_network(network, "Node")
        if not node_members:
            continue        
        node_member = node_members[0]
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
        add_devices_to_node(network, ns3node_to_node, sta_nodes, sta_devices, phy)

        # AP devices
        mac = ns3.NqosWifiMacHelper.Default()
        mac.SetType ("ns3::NqapWifiMac", 
            "Ssid", ns3.SsidValue(ssid),
            "BeaconGeneration", ns3.BooleanValue(True),
            "BeaconInterval", ns3.TimeValue(ns3.Seconds(2.5)))
        ap_devices = wifi.Install(phy, mac, ap_node)
        add_devices_to_node(network, ns3node_to_node, ap_node, ap_devices, phy)
        
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
