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
    return itertools.izip(*[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)

def split_iter(it, condition, skip_sep=False):
    """Split iterable yield elements grouped by condition."""
    for match, group in itertools.groupby(it, condition):
        if skip_sep and match:
            continue
        yield list(group)

class RadioMobileReportTest(unittest.TestCase):
    def setUp(self):
        filename = "cusco-nw-report.txt"
        path = os.path.join(os.path.dirname(__file__), filename)
        self.report = radiomobile.parse_report(path)
        data = radiomobile_ns3_report.generate_simple_text_report(self.report)
        self.sections = list(grouper(2, split_iter(data.splitlines(), lambda s: s.startswith("= "))))

    def test_general_information(self):
        title, contents = self.sections[0]
        self.assertEqual("= Network General information", title[0])
        self.assertEqual(["", "Netfile: CUSCO-NW.NET", "Generated: 2010-02-23T12:13:46", ""],
            contents)

    def test_nodes(self):
        title, contents = self.sections[1]
        self.assertEqual("= Nodes", title[0])
        self.assertEqual(["", "Josjojauarina 1", "Josjojauarina 2", "Ccatcca",
            "Kcauri", "Urpay", "Huiracochan", "Urcos", ""], contents)

    def test_nets(self):
        title, contents = self.sections[2]
        self.assertEqual("= Nets", title[0])
        nets = list(grouper(2, split_iter(contents[1:], lambda s: s.startswith("== "))))
        net1_title, net1_contents = nets[0]
        self.assertEqual("== Josjo1-Josjo2", net1_title[0])
        self.assertEqual(['', 'Mode: wifia-6m', '', 
            'Node\tRole\tDistance to AP [km]',
            'Josjojauarina 1\tAP\t0.00',
            'Josjojauarina 2\tSTA\t22.48', ''], net1_contents)


if __name__ == '__main__':
    unittest.main()