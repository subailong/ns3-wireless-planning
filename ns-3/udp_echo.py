import sys
import ns3
import radiomobile

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)

def debug(line):
    """Output line to standard error."""
    sys.stderr.write(line + "\n")
    sys.stderr.flush()

def create_network(report):
  sta_nodes = ns3.NodeContainer()
  sta_nodes.Create(3)
  ap_node = ns3.Node() # nodes.Get(0)
  
  channel = ns3.YansWifiChannelHelper.Default()
  phy = ns3.YansWifiPhyHelper.Default()
  phy.SetChannel(channel.Create())

  wifi = ns3.WifiHelper.Default()
  wifi.SetRemoteStationManager("ns3::AarfWifiManager")
  mac = ns3.NqosWifiMacHelper.Default()  
  ssid = ns3.Ssid("ns-3-ssid")
  mac.SetType("ns3::NqstaWifiMac", 
    "Ssid", ns3.SsidValue(ssid),
    "ActiveProbing", ns3.BooleanValue(False))
  sta_devices = wifi.Install(phy, mac, sta_nodes)

  mac = ns3.NqosWifiMacHelper.Default()
  mac.SetType ("ns3::NqapWifiMac", 
    "Ssid", ns3.SsidValue(ssid),
    "BeaconGeneration", ns3.BooleanValue(True),
    "BeaconInterval", ns3.TimeValue(ns3.Seconds(2.5)))
  ap_devices = wifi.Install(phy, mac, ap_node)
  
  stack = ns3.InternetStackHelper()
  stack.Install(sta_nodes)
  stack.Install(ap_node)

  address = ns3.Ipv4AddressHelper()
  address.SetBase(ns3.Ipv4Address("10.1.1.0"), ns3.Ipv4Mask("255.255.255.0"))

  ap_interfaces = address.Assign(ap_devices)
  sta_interfaces = address.Assign(sta_devices)

  mobility = ns3.MobilityHelper()
  mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
  mobility.Install(ap_node)
  
  mobility = ns3.MobilityHelper()
  mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel")
  mobility.Install(sta_nodes)
    
  phy.EnablePcap("main", ap_devices.Get(0));
  phy.EnablePcap("main", sta_devices.Get(0));
  
  # Applications
  
  echoServer = ns3.UdpEchoServerHelper(9)
  serverApps = echoServer.Install(ap_node)
  serverApps.Start(ns3.Seconds(1.0))
  serverApps.Stop(ns3.Seconds(10.0))

  echoClient = ns3.UdpEchoClientHelper(ap_interfaces.GetAddress(0), 9)
  echoClient.SetAttribute("MaxPackets", ns3.UintegerValue(1))
  echoClient.SetAttribute("Interval", ns3.TimeValue(ns3.Seconds(1.0)))
  echoClient.SetAttribute("PacketSize", ns3.UintegerValue(1024))
  clientApps = echoClient.Install(sta_nodes.Get(2))
  clientApps.Start(ns3.Seconds(2.0))
  clientApps.Stop(ns3.Seconds(10.0))

  ns3.Ipv4GlobalRoutingHelper.PopulateRoutingTables()


def run_simulation():
  ns3.Simulator.Stop(ns3.Seconds(10.0))
  ns3.Simulator.Run()
  ns3.Simulator.Destroy()

def main(args):
    if len(args) != 1:
        debug("Usage: %s REPORT_TXT_PATH" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = radiomobile.RadioMobileReport(text_report_filename)
    create_network(report)
    #nodes, devices, interfaces = create_network(report)
    #create_applications(nodes, devices, interfaces)
    run_simulation()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
