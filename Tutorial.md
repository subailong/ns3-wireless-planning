# Introduction #

This tutorial shows how to create and simulate the performance of a wireless WAN (containing WiFi and/or WiMAX networks). You will need a Unix-like operating system (Debian/Ubuntu will be assumed when necessary).

_ns3-wireless-planning_ goal is to easily integrate two powerful applications: [Radio Mobile](http://www.cplus.org/rmw/english1.html) (radio-systems simulator) and [ns-3](http://www.nsnam.org/) (discrete-event network simulator).

## Radio Mobile ##

Radio Mobile is a freeware tool for plotting RF patterns and predicting the performance of radio systems. It's able to draw maps using terrain elevation data (SRTM, DTED, BIL, or GTOPO30) for automatic extraction of path profile between an emitter and a receiver. This data is added to system, environmental and statistical parameters to feed the Irregular Terrain Model radio propagation model.

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-link.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-link.png)

The software also provides 3D views, stereoscopic views, and animation. Background picture can be merged with scanned map, satellite photo or military ADRG.

Radio Mobile has some serious drawbacks though: firstly, it's not [free software](http://www.gnu.org/philosophy/free-sw.html) but freeware, and the source code is not available. Secondly, it's written in Visual Basic, so it's not multi-platform. Fortunately it runs in [Wine](http://www.winehq.org/), so you don't need to dual-boot or use a virtual machine.

Here is a thorough [Tutorial](http://www.pizon.org/radio-mobile-tutorial/index.html).

## ns-3 ##

[ns-3](http://www.nsnam.org/) is a discrete-event network simulator for Internet systems. ns-3 is free software (GNU GPLv2 license) and is intended as an eventual replacement for the popular [ns-2 http://www.isi.edu/nsnam/ns/] simulator.

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/ns3-stats.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/ns3-stats.png)

ns-3 is written in C++ even though it's possible to write simulation in Python. Take a look at the [Tutorials](http://www.nsnam.org/tutorials.html) on how to use the simulator.

# Installation #

## Radio Mobile ##

  * Install wine:

```
$ apt-get install wine
```

  * Install Radio Mobile in some directory following these [install instructions](http://wireless.ictp.it/school_2005/download/radiomobile/index.html).

  * Try it:

```
$ cd path/to/radiomobile/
$ wine rmweng.exe
```

## ns-3 ##

  * Download the sources from our mercurial repository (it includes a vanilla ns-3 + _scratch_ module):

```
$ hg clone http://ns-3.ns3-wireless-planning.googlecode.com/hg/ ns-3
```

  * Compile:

```
$ cd ns-3
$ ./waf configure
$ ./waf build
```

**Download elevation data**

You can either download SRTM files ([mirror](http://dds.cr.usgs.gov/srtm/version1/)) to your hard-disk or, if you are in a high-speed network, let Radio Mobile download them when needed.

## ns-3-wireless-planning scripts ##

  * Download from sources:

```
$ hg clone http://ns3-wireless-planning.googlecode.com/hg/ ns3-wireless-planning 
```

# Usage #

We will use an example to demonstrate the whole process of creation and simulation of a network. The test network is part of a real [EHAS network](http://www.ehas.org/) deployed in the Peruvian Andes near Cusco. Some details:

  * 7 nodes (Josjojauarina1, Josjojauarina2, Ccatcca, Kcauri, Urpay, Huiracochan, Urcos).

  * 4 sub-networks: Josjojauarina2-Ccatcca-Kcauri (WiMAX), Josjojauarina1-Josjojauarina2 (WiFi), Josjojauarina1-Urpay-Huiracochan (WiFi), Huiracochan-Urcos (WiFi).

For the impatient, the Radio Mobile network file can be downloaded from the repository: [cusco-ne.net](http://ns3-wireless-planning.googlecode.com/hg/radiomobile/examples/cusco-ne/cusco-ne.net).

### Map and units ###

First create the nodes (units, in Radio Mobile terminology):

_File_ -> _Unit properties_

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map-units.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map-units.png)

And configure the map properties to use SRTM info:

_File_ -> _Map properties_

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map-properties.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map-properties.png)

Now you should be able to see the units located on the map:

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-map.png)

### Networks and systems ###

When the units are placed onto the map, we must specify the sub-networks (links) and systems (types of interface) that they will use.

Create the four networks, specifying the network type (_wifi_/_wimax_) between brackets in the network name.

_File_ -> _Network properties_

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-networks.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-networks.png)

WiFi modes must be shortened because Radio Mobile (not very wisely) cuts the name to 20 chars. Use this table to encode a WiFi/WiMAX mode:

| **Mode** | **System suffix** |
|:---------|:------------------|
| WiFi A 6Mbps | WFa6 |
| WiFi A 12Mbps | WFa12 |
| WiFi B 6Mbps | WFb1 |
| WiFi B 12Mbps | WFb2 |
| WiMAX BPSK 1/2 | WXbk12 |
| WiMAX QPSK 1/2 | WXqk12 |
| WiMAX QPSK 3/4 | WXqk34 |
| WiMAX 16 QAM 1/2 | WX16qm12 |
| WiMAX 16 QAM 3/4 | WX16qm34 |
| WiMAX 64 QAM 2/3 | WX64qm23 |
| WiMAX Base Station | WXall |

For example, if you created a system called originally _mysystem_ and you plan to use it with 802.11a at 18Mbps, you will set the system name to "_mysystem [WFa18](WFa18.md)_".

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-systems.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-systems.png)

Lastly, we need to define the topology of the network. Use role _Master_ for _Access Points_ (WiFi) or _Base Stations_ (WiMAX), and _Slave_ for _Stations_ (WiFi) and _Subscriber Stations_ (WiMAX):

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-membership.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-membership.png)

### Create the report ###

Extract all the relevant information of the network saving a text-file network report.

_Tools_ -> _Network report_ -> _File_

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-report.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/rmw-report.png)

## Convert the network report ##

The network report (_report.txt_) created by Radio Mobile must be converted to a _netinfo_ report that our module in ns-3 understands:

```
$ cd ns3-wireless-planning/ns-3
$ PYTHONPATH=../radiomobile python radiomobile_ns3_report.py report.txt > netinfo.txt
```

Take a look at the generated file (netinfo.txt) to see the information it contains.

## Simulate a network ##

Now it's time to start running simulations with ns-3. _ns3-wireless-planning_ adds some infrastructure to ns-3 (to the _scratch_ directory_) so it's possible to parse the_netinfo_file generated on the previous step automatically while we focus only in adding applications and traces. Let's simulate the performance of 2 flows running simultaneously (Urcos-Huiracochan and Urcos-Ccatcca)._

First of all, copy the _netinfo_ file to the ns-3 root directory:

```
$ cp /path/somewhere/netinfo.txt ns-3
$ cd ns-3
```

And create a simulation code name _scratch/wireless-planning-mysimulation.cc_ (be aware that you must keep the _wireless-planning_ prefix), change only the _mysimulation_ part:

```
#include "ns3/core-module.h"
#include "ns3/simulator-module.h"
#include "ns3/helper-module.h"

#include "wireless-planning/net-test.h"
#include "wireless-planning/create-network.h"
#include "wireless-planning/network-config.h" 
#include "wireless-planning/print.h"
#include "wireless-planning/netinfo-reader.h"
#include "wireless-planning/report-2-config-data.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("mysimulation");

int
main (int argc, char *argv[])
{
  Time eos = Seconds (5);

  /* Process command line options */
  CommandLine cmd;
  cmd.AddValue ("netinfo", "Network Information File", netInfoFile);
  cmd.Parse (argc, argv);

  /* Read netinfo and build network */
  NetDataStruct::NetData netData = NetinfoReader::Read ((netInfoFile));
  Print::Netinfo (netData);
  NetworkConfig::NetworkData networkData = Report2ConfigData::NetData2NetworkData (netData);
  Print::NetworkData (networkData);
  CreateNetwork createNetwork;
  NodeContainer nodes = createNetwork.Create (networkData);
  Print::NodeList (nodes);

  /* Setup simulation */
  NetTest netTest;
  netTest.EnablePcap("Josjojauarina 2", 1);
    
  netTest.ApplicationSetup ("Urcos", "Ccatcca", 1.0, 3.0, "10Mbps", 1452, NULL);
  netTest.ApplicationSetup ("Urcos", "Huiracochan", 2.0, 4.5, "10Mbps", 1452, NULL);

  std::vector < string > flowNames;
  flowNames.push_back ("Urcos-Ccatcca");
  flowNames.push_back ("Urcos-Huiracochan");

  /* Setup all the plot system: throughput measurement, gnuplot */
  NetMeasure netMeasure (eos, Seconds (0.1));
  netMeasure.SetupPlot ();
  netMeasure.SetFlowNames (flowNames);
  netMeasure.SetFlowMonitor (nodes);
  netMeasure.GetFlowStats ();

  Simulator::Stop (eos);
  
  NS_LOG_INFO ("Starting simulation...");
  Simulator::Run ();
  Simulator::Destroy ();
  NS_LOG_INFO ("Done.");
  
  return 0;
}
```

And start the simulation (we enables logs for _PacketSink_ to see what is going on, more info on the ns-3 tutorial):

```
$ export NS_LOG="PacketSink=level_all|prefix_time"
$ ./waf --run "scratch/wireless-planning-mysimulation --netinfo=netinfo.txt"
$ gnuplot *.plt
```

[gnuplot](http://www.gnuplot.info/) will create a PNG image for each plot generated by ns-3. In our example:

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_DelayHist.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_DelayHist.png)

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_DelayMean.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_DelayMean.png)

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_LostPackets.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_LostPackets.png)

![http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_Throughput.png](http://wiki.ns3-wireless-planning.googlecode.com/hg/img/net-measure_Throughput.png)