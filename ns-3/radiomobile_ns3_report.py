#!/usr/bin/python
# -*- coding: utf-8 -*
"""
Parse radiomobile report.txt file and generate a simple txt file, showing:
    
- General information
- Nodes (name, WSG84 coordinates, XY-meter positions)
- Networks (name, node members/roles/distance to AP.

Example:
    
= General information

Netfile: CUSCO-NW.NET
Generated: 2010-02-23T12:13:46

= Nodes

Josjojauarina 1	280	-9.31972,-75.14583	0,0
Josjojauarina 2	217	-9.26694,-74.94806	21728,5837
Ccatcca	367	-9.20917,-74.81833	35979,12228
Kcauri	839	-9.31278,-74.81306	36559,768

= Nets

== Josjo1-Josjo2

Mode: wifi

Node	Role	Distance to AP Mode  
Josjojauarina 1	AP	0   wifib-2m
Josjojauarina 2	STA	22480   wifib-2m

== Josjo2

Mode: wimax

Node	Role	Distance to BS  Mode
Josjojauarina 2	BS	0   wimax-
Ccatcca	SS	15620   wimax-all
Kcauri	SS	15670   wimax-qpsk3/4
"""
import os
import re
import sys
import math
import itertools
from datetime import datetime
import pprint

import radiomobile
      
def build_output_from_sections(sections):
    """Build a string from list of sections with tuple (title, lines). Output is:
        
    = section1 title
    [blank space]
    line1
    line2
    [blank space]
    = section2 title
    [...]
    """
    def _section(name, lines):
        return ["= %s" % name, ""] + list(lines)
    sections_output = ("\n".join(_section(name, lines)) for (name, lines) in sections)
    return "\n\n".join(sections_output) + "\n"

def join_list(lstlst, joinval):
    """Join list of list with a join value and return a 1-level flattened list."""
    for index, lst in enumerate(lstlst):
        for x in lst:
            yield x
        if index < len(lstlst)-1:
            yield joinval 
        
def generate_simple_text_report(report):
    """Return string containing a simple text report from Radiomobile report."""        
    sections = []
    
    # General information
    netfile = re.match(r"Net file\s+.*\\(.*)$", report.general_information[0]).group(1)
    information = []
    information.append("Netfile: %s" % netfile)
    generated = report.generated_on.isoformat()
    information.append("Generated: %s" % generated)
    
    sections.append(["General information", information])
    
    # Nodes
    nodes = []
    for name, unit in report.units.iteritems():
        coords = ",".join(["%0.5f" % x for x in unit.location_coords])
        position = ",".join(map(str, unit.location_meters))
        nodes.append("\t".join([name, str(unit.elevation), coords, position]))
    sections.append(["Nodes", nodes])               

    # Active networks
    roles_table = {
        "wifi": {
            "Master": "AP",
            "Node": "AP",
            "Slave": "STA",
            "Terminal": "STA",
        },
        "wimax": {
            "Master": "BS",
            "Node": "BS",
            "Slave": "SS",
            "Terminal": "SS",                
        }            
    }
    
    nets = []
    for complete_name, attrs in report.nets.iteritems():
        match = re.match("^(.*?)\s*\[(.*)\]$", complete_name)
        if not match:
            raise ValueError, "Wrong name for network. Expected: 'Netname [ns3linkname]'"
        name, options = match.groups()
        mode = options        
        net = []
        net.extend(["== " + name, ""])
        net.extend(["Mode: %s" % mode, ""])
        masters = radiomobile.get_units_for_network(attrs, 'Master') + \
         radiomobile.get_units_for_network(attrs, 'Nodes')
        assert (len(masters) == 1), "Need one and only one master/node in a network"
        master = masters[0]
        slaves = radiomobile.get_units_for_network(attrs, 'Slave') + \
            radiomobile.get_units_for_network(attrs, 'Terminal')
        assert (len(slaves) >= 1), "Need at least one slave/terminal in a network"
        master_name = roles_table[mode]["Master"]
        net.append("\t".join(["Node", "Role", "Distance to %s" % master_name, "Mode"]))
        master_location = report.units[master].location
        for member_name, member_attrs in attrs.net_members.iteritems():
            if member_name not in report.units:
                raise ValueError, "Member of net not found in units: %s" % member_name
            member_location = report.units[member_name].location
            if member_name != master:
                distance = radiomobile.get_distance_between_locations(
                    master_location, member_location)
            else:
                distance = 0            
            if mode not in roles_table:
                raise ValueError, "Known modes are 'wifi' and 'wimax': %s" % mode
            roles = roles_table[mode]
            member_mode = member_attrs.system.split(" - ")[-1]
            member_info = [
                member_name, 
                roles[member_attrs.role], 
                str(distance),
                member_mode,
            ]
            net.append("\t".join(member_info))
        nets.append(net)
    sections.append(["Nets", join_list(nets, "")])

    return build_output_from_sections(sections)   
          
  
def main(args):    
    if len(args) != 1:
        debug("Usage: %s RADIOMOBILE_REPORT_FILE" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = radiomobile.parse_report(text_report_filename)
    sys.stdout.write(generate_simple_text_report(report))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
