#!/usr/bin/python
# -*- coding: utf-8 -*
"""Parse radiomobile report.txt file."""
import os
import re
import sys
import itertools
from datetime import datetime
from pprint import pprint

from odict import odict

# Generic functions

def debug(line):
    """Output line to standard error."""
    sys.stderr.write(line + "\n")
    sys.stderr.flush()

def group(n, iterable, fillvalue=None):
    "group(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

def keyify(s):
    """Replaces spaces in string for underscores."""
    return re.sub("\s+", "_", s).replace(".", "").replace(":", "").lower() 

def split_iter(it, condition, skip_sep=False):
    """Split iterable yield elements grouped by condition."""
    for match, group in itertools.groupby(it, condition):
        if skip_sep and match:
            continue
        yield list(group)

def strip_iter(it, condition=bool):
    """Strip element in iterable."""
    return list(itertools.ifilter(condition, it))
    
def find_columns(line, fields):
    """Return list of pairs (field, index) for fields in line."""
    return [(field, line.index(field)) for field in fields]

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def parse_table(lines, fields, keyify_cb=None):
    """Parse table and yield dictionaries containing the row info."""
    header, units = lines[0], lines[1:]
    columns = find_columns(header, fields)
    fields, indexes = zip(*columns)
    for line in strip_iter(units):
        def _generator():
            for (field, (start, end)) in zip(fields, pairwise(indexes+(None,))):
                key = (keyify(field) if (not keyify_cb or keyify_cb(field)) else field)
                value = line[start:end].strip()
                yield (key, value)
        yield dict(_generator())        

def iter_block(lines, startre, endre):
    """Yield lines whose bounds are defined by a start/end regular expressions."""
    for line in itertools.dropwhile(lambda s: not re.match(startre, s), lines):
        yield line
        if re.match(endre, line):
            break
    
# Radiomobile functions

def create_odict_from_items(key, dictlst):
    """
    Construct an ordered dictionary from a list of dictionaries, using 
    the key from the dictionary.
    """
    def _generator():
        for delement in dictlst:        
            values = dict((k, v) for (k, v) in delement.iteritems() if k != key)
            yield (delement[key], values)
    return odict(_generator())      
    
def parse_header(lines):
    """
    Check that the headers contain a valid RadioMobile identifier and return
    the generation report date.
    """     
    title, generated = strip_iter(lines)
    expected_title = "Radio Mobile" 
    if title != expected_title:
        raise ValueError, "Unknown header: %s (expected: %s)" % (title, expected_title)
    info = " ".join(generated.split()[-3:])
    return datetime.strptime(info, "%H:%M:%S on %d-%m-%Y")

def parse_active_units(lines):
    """Return orderect dict containing (name, attributes) pairs for units."""
    headers = ["Name", "Location", "Elevation"]
    return create_odict_from_items("name", parse_table(lines, headers))
            
def parse_systems(lines):
    """Return orderect dict containing (name, attributes) pairs for systems."""
    headers = ["Name", "Pwr Tx", "Loss", "Loss (+)", "Rx thr.", "Ant. G.", "Ant. Type"]
    return create_odict_from_items("name", parse_table(lines, headers))

def get_net_links(rows, grid_field, max_quality):
    """Parse a quality grid and return dictionary with information.""" 
    def get_quality(lst):
        s = "".join(lst)
        return (int(s) if s.strip() else None)
    def clean_node(node):
        return dict((k, v) for (k, v) in node.iteritems() if not k.startswith("#"))
    
    for nrow, row in enumerate(rows):
        qualities = map(get_quality, group(3, row[grid_field][3:], ''))
        for npeer_row, quality in enumerate(qualities):
            if not quality or nrow >= npeer_row:
                continue
            peer_row = rows[npeer_row]
            link = {            
                "quality": quality,
                "max_quality": max_quality,
                "node1": clean_node(row),
                "node2": clean_node(peer_row),
            }
            yield link

def parse_active_nets(lines):
    """Return an orderd dict with nets, each containing a list of links.""" 
    nets_lines = list(split_iter(lines[1:], lambda s: re.match("\d+\. ", s)))
    nets = odict()
    for header, info in group(2, nets_lines):
        index, name = map(str.strip, header[0].split(". ", 1))
        block = list(iter_block(info, r"Net members:", r"\s.*Quality ="))
        table, quality_line = block[:-2], block[-1]
        max_quality = int(re.search("Quality = (\d+)", quality_line).group(1))
        grid_field = re.match("Net members:\s*(.*?)\s*Role:", table[0]).group(1)
        grid_fields = ["Net members:", grid_field, "Role:", "System:", "Antenna:"]    
        rows = list(parse_table(table, grid_fields, lambda s: not s.startswith('#')))
        links = list(get_net_links(rows, grid_field, max_quality))        
        nets[name] = links
    return nets                

class RadioMobileReport:
    """
    Read and parse a Radiomobile report.txt file.
    
    >>> report = RadioMobileReport("report.txt")
    >>> report.nets
    >>> report.systems
    >>> report.units
    """
    def __init__(self, filename):
        lines = open(filename).read().splitlines()
        splitted_lines = list(split_iter(lines, lambda s: s.startswith("---"), skip_sep=True))
        generated_on = parse_header(splitted_lines[0])
        sections = dict((keyify(key[0]), val) for (key, val) in group(2, splitted_lines[1:]))
        
        self.generated_on = generated_on
        self.general_information = sections["general_information"]
        self.units = parse_active_units(sections["active_units_information"])
        self.systems = parse_systems(sections["systems"])
        self.nets = parse_active_nets(sections["active_nets_information"])


def main(args):
    """Print basic information of a report.txt."""
    if not args:
        debug("Usage: %s REPORT_TXT_PATH" % os.path.basename(sys.argv[0]))
        return 2
    text_report_filename, = args
    report = RadioMobileReport(text_report_filename)
    print "--- Generated on: %s" % report.generated_on
    print "--- Units:"
    report.units.pprint()
    print "--- Systems:"
    report.systems.pprint()
    print "--- Nets:"
    report.nets.pprint()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
