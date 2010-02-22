#!/usr/bin/python
import sys
import ns3
import optparse
from pprint import pprint

import radiomobile_ns3 as rmw_ns3

ns3.LogComponentEnable("UdpEchoClientApplication", ns3.LOG_LEVEL_INFO)
ns3.LogComponentEnable("UdpEchoServerApplication", ns3.LOG_LEVEL_INFO)

def run_simulation(network):
    # Applications
    server = network.nodes["CCATCCA"]    
    server_address = server.devices["Uuario Final PCMCIA"].interfaces[0].address
    echoServer = ns3.UdpEchoServerHelper(9)
    serverApps = echoServer.Install(server.ns3_node)
    serverApps.Start(ns3.Seconds(1.0))
    serverApps.Stop(ns3.Seconds(10.0))

    client = network.nodes["URCOS"]
    echoClient = ns3.UdpEchoClientHelper(server_address, 9)
    echoClient.SetAttribute("MaxPackets", ns3.UintegerValue(1))
    echoClient.SetAttribute("Interval", ns3.TimeValue(ns3.Seconds(1.0)))
    echoClient.SetAttribute("PacketSize", ns3.UintegerValue(1024))
    clientApps = echoClient.Install(client.ns3_node)
    clientApps.Start(ns3.Seconds(2.0))
    clientApps.Stop(ns3.Seconds(10.0))
    
    # Tracing
    josjo1 = network.nodes["JOSJOJAHUARINA 1"]
    device = josjo1.devices['Josjo 1 Sectorial PC'].ns3_device
    phy = josjo1.devices['Josjo 1 Sectorial PC'].phy_helper
    phy.EnablePcap("udp_echo", device)

    # Run simulation    
    ns3.Simulator.Stop(ns3.Seconds(10.0))
    ns3.Simulator.Run()
    ns3.Simulator.Destroy()
    
def main(args0):
    usage = """Usage: %prog [OPTIONS] radiomobile_report_path

    Run a UDP server/client simple example.""" 
    parser = optparse.OptionParser(usage)
    parser.add_option('-v', '--verbose', dest='vlevel', action="count",
      default=0, help='Increase verbose level)')
    options, args = parser.parse_args(args0)
    rmw_ns3.verbose_level = options.vlevel
    if len(args) != 1:
        parser.print_help()
        return 2
        
    text_report_filename, = args
    network = rmw_ns3.create_network_from_report_file(text_report_filename)
    run_simulation(network)    
    
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
