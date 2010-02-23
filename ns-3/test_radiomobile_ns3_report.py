#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import unittest
import itertools
from datetime import datetime
from pprint import pprint

import radiomobile
import radiomobile_ns3_report as rnr

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
        data = rnr.generate_simple_text_report(self.report)
        self.sections = list(grouper(2, split_iter(data.splitlines(), lambda s: s.startswith("= "))))

    def test_general_information(self):
        title, contents = self.sections[0]
        self.assertEqual("= Network General information", title[0])
        self.assertEqual(["", "Netfile: CUSCO-NW.NET", "Generated: 2010-02-23T12:13:46", ""],
            contents)

                
if __name__ == '__main__':
    unittest.main()
