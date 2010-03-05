#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import unittest
import itertools
from datetime import datetime
from pprint import pprint

import radiomobile
import radiomobile_ns3_report

def grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return itertools.izip(*[itertools.chain(iterable, 
        itertools.repeat(padvalue, n-1))]*n)

def split_iter(it, condition, skip_sep=False):
    """Split iterable yield elements grouped by condition."""
    for match, group in itertools.groupby(it, condition):
        if skip_sep and match:
            continue
        yield list(group)

class RadioMobileReportTest(unittest.TestCase):
    def setUp(self):
        filename = "example.report.txt"
        path = os.path.join(os.path.dirname(__file__), filename)
        self.report = radiomobile.parse_report(path)
        data = radiomobile_ns3_report.generate_simple_text_report(self.report)
        self.sections = list(grouper(2, split_iter(data.splitlines(), 
            lambda s: s.startswith("= "))))

    def get_nets(self):
        title, contents = self.sections[2]
        self.assertEqual("= Nets", title[0])
        nets = list(grouper(2, split_iter(contents[1:], 
            lambda s: s.startswith("== "))))
        return nets

    # Tests
    
    def test_general_information(self):
        title, contents = self.sections[0]
        self.assertEqual("= General information", title[0])
        self.assertEqual(
            ["", "Netfile: CUSCO-NW.NET", "Generated: 2010-02-23T12:13:46", ""],
            contents)

    def test_nodes(self):
        title, contents = self.sections[1]
        self.assertEqual("= Nodes", title[0])
        self.assertEqual(["Josjojauarina 1", "Josjojauarina 2", "Ccatcca",
            "Kcauri", "Urpay", "Huiracochan", "Urcos"], 
            [s.split("\t")[0] for s in contents[1:-1]])
        self.assertEqual(
            ['Josjojauarina 1', '280', '-9.31972,-75.14583', '0,0'], 
            contents[1].split("\t"))

    def test_nets(self):
        title, contents = self.sections[2]
        self.assertEqual("= Nets", title[0])
        nets = list(grouper(2, split_iter(contents[1:], 
            lambda s: s.startswith("== "))))
        
    def test_wifi_nets(self):
        nets = self.get_nets()
        net1_title, net1_contents = nets[0]
        self.assertEqual("== Josjo1-Josjo2", net1_title[0])
        self.assertEqual(['', 'Mode: wifi', '', 
            'Node\tRole\tDistance to AP\tMode',
            'Josjojauarina 1\tAP\t0\twifia-5mb',
            'Josjojauarina 2\tSTA\t22482\twifia-5mb', ''], net1_contents)

    def test_wimax_nets(self):
        nets = self.get_nets()
        net1_title, net1_contents = nets[3]
        self.assertEqual("== Huiracochan", net1_title[0])
        self.assertEqual(['', 'Mode: wimax', '', 
            'Node\tRole\tDistance to BS\tMode',
            'Huiracochan\tBS\t0\twimax-16qam1/2',
            'Urcos\tSS\t12892\twimax-16qam1/2'], net1_contents)


if __name__ == '__main__':
    unittest.main()
