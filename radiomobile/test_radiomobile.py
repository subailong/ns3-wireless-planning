#!/usr/bin/python
# -*- coding: utf-8 -*
import unittest
from datetime import datetime
from pprint import pprint

import radiomobile

class RadioMobileReportTest(unittest.TestCase):
    def setUp(self):
        self.report = radiomobile.RadioMobileReport("radiomobile_report_test.txt")
              
    def test_generated_on(self):
        self.assertEqual(datetime(2007, 4, 7, 17, 38, 51), self.report.generated_on)
                      
    def test_units(self):
        units = self.report.units
        expected_units = ['URPAY', 'HUIRACOCHAN', 'JOSJOJAHUARINA 1', 'JOSJOJAHUARINA 2'] 
        self.assertEqual(expected_units, units.keys())
    
    def test_unit_details(self):
        units = self.report.units
        urpay = units["URPAY"]        
        self.assertEqual("""13°42'42"S 071°39'55"W 19L BE 11727 82575""", urpay["location"]) 
        self.assertEqual("3420.0m", urpay["elevation"]) 
            
    def test_systems(self):
        systems = self.report.systems
        expected_systems = ['Uuario Final PCMCIA', 'Josjo 1 Sectorial PC', 
            'Josjo 1 Directiva PC', 'Josjo 2 Troncal', 'Huiracochan Troncal', 
            'Don Juan PCMCIA', 'wifi 5.8']
        self.assertEqual(expected_systems, systems.keys())

    def test_system_details(self):
        systems = self.report.systems
        huira = systems["Huiracochan Troncal"]
        self.assertEqual("0.200W", huira["pwr_tx"])
        self.assertEqual("2.9dB", huira["loss"]) 
        self.assertEqual("0.000dB/m", huira["loss_(+)"])
        self.assertEqual("93.0dBm", huira["rx_thr"])
        self.assertEqual("19.0dBi", huira["ant_g"])
        self.assertEqual("omni.ant", huira["ant_type"])

    def test_nets(self):
        nets = self.report.nets
        self.assertEqual(['Josjo1AP - Josjo2', 'Josjo1 AP - Huiracochan, Ur'], nets.keys())

    def test_net_details(self):
        nets = self.report.nets
        links = nets['Josjo1 AP - Huiracochan, Ur']
        
        self.assertEqual(2, len(links))
        link1, link2 = links
        
        self.assertEqual(50, link1["quality"])
        self.assertEqual(50, link1["max_quality"])
        expected_link1_node1 = {
            'antenna': '5.0m',
            'net_members': 'URPAY',
            'role': 'Terminal',
            'system': 'Uuario Final PCMCIA',
        }
        self.assertEqual(expected_link1_node1, link1["node1"])        
        expected_link1_node2 = {
            'antenna': '6.5m',
            'net_members': 'JOSJOJAHUARINA 1',
            'role': 'Node',
            'system': 'Josjo 1 Sectorial PC',
        }
        self.assertEqual(expected_link1_node2, link1["node2"])

                
if __name__ == '__main__':
    unittest.main()
