#!/usr/bin/python
# -*- coding: utf-8 -*
"""Parse radiomobile report.txt file and generate a simple txt file."""
import os
import re
import sys
import itertools
from datetime import datetime
import pprint

import radiomobile

def build_output_from_sections(sections):
    def _section(name, lines):
        return ["= %s" % name, ""] + list(lines)
    sections_output = ("\n".join(_section(name, lines)) for (name, lines) in sections)
    return "\n\n".join(sections_output) + "\n"

def join_list(lstlst, joinval):
    for index, lst in enumerate(lstlst):
        for x in lst:
            yield x
        if index < len(lstlst)-1:
            yield joinval 
        
def generate_simple_text_report(report):
    sections = []
    
    # General information
    netfile = re.match(r"Net file\s+.*\\(.*)$", report.general_information[0]).group(1)
    information = []
    information.append("Netfile: %s" % netfile)
    generated = report.generated_on.isoformat()
    information.append("Generated: %s" % generated)
    
    sections.append(["Network General information", information])
    
    # Nodes
    sections.append(["Nodes", report.units.keys()])               

    # Active networks
    nets = []
    for complete_name, attrs in report.nets.iteritems():
        name, options = re.match("^(.*?)\s*\[(.*)\]$", complete_name).groups()
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
        net.append("\t".join(["Node", "Role", "Distance to Master [km]"]))
        master_location = report.units[master].location
        for member_name, member_attrs in attrs.net_members.iteritems():
            member_location = report.units[member_name].location
            if member_name != master:
                distance = radiomobile.get_distance_between_locations(
                    master_location, member_location)
            else:
                distance = 0.0
            droles = {
                "Master": "AP",
                "Node": "AP",
                "Slave": "STA",
                "Terminal": "STA",            
            }
            assert (member_attrs.role in droles), "Role should be one of: %s" \
                ", ".join(droles.keys())
            role = droles[member_attrs.role]  
            member_info = [member_name, role, "%0.2f" % distance]
            net.append("\t".join(member_info))
        nets.append(net)
    sections.append(["Nets", join_list(nets, "")])

    return build_output_from_sections(sections)   
          
  
def main(args):    
    if len(args) != 1:
        debug("Usage: %s REPORT_TXT_PATH" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = radiomobile.parse_report(text_report_filename)
    sys.stdout.write(generate_simple_text_report(report))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
