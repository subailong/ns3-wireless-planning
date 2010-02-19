#!/usr/bin/python
# -*- coding: utf-8 -*
import os
import unittest
from datetime import datetime
from pprint import pprint

import radiomobile

class RadioMobileReportTest(unittest.TestCase):
    def setUp(self):
        filename = "radiomobile_report_test.txt"
        path = os.path.join(os.path.dirname(__file__), filename)
        self.report = radiomobile.parse_report(path)
              
    def test_generated_on(self):
        self.assertEqual(datetime(2007, 4, 7, 17, 38, 51), self.report.generated_on)
                      
    def test_units(self):
        units = self.report.units
        expected_units = ['URPAY', 'HUIRACOCHAN', 'JOSJOJAHUARINA 1', 'JOSJOJAHUARINA 2'] 
        self.assertEqual(expected_units, units.keys())
    
    def test_unit_details(self):
        units = self.report.units
        urpay = units["URPAY"]        
        self.assertEqual("""13°42'42"S 071°39'55"W 19L BE 11727 82575""", urpay.location) 
        self.assertEqual("3420.0m", urpay.elevation) 
            
    def test_systems(self):
        systems = self.report.systems
        expected_systems = ['Uuario Final PCMCIA', 'Josjo 1 Sectorial PC', 
            'Josjo 1 Directiva PC', 'Josjo 2 Troncal', 'Huiracochan Troncal', 
            'Don Juan PCMCIA', 'wifi 5.8']
        self.assertEqual(expected_systems, systems.keys())

    def test_system_details(self):
        systems = self.report.systems
        huira = systems["Huiracochan Troncal"]
        self.assertEqual("0.200W", huira.pwr_tx)
        self.assertEqual("2.9dB", huira.loss) 
        self.assertEqual("0.000dB/m", getattr(huira, "loss_(+)"))
        self.assertEqual("93.0dBm", huira.rx_thr)
        self.assertEqual("19.0dBi", huira.ant_g)
        self.assertEqual("omni.ant", huira.ant_type)

    def test_nets(self):
        nets = self.report.nets
        self.assertEqual(['Josjo1AP - Josjo2', 'Josjo1 AP - Huiracochan, Ur'], nets.keys())

    def test_net_details(self):
        nets = self.report.nets
        net1 = nets['Josjo1 AP - Huiracochan, Ur']
        links = net1.links        
        self.assertEqual(50, net1.max_quality)
        self.assertEqual(2, len(links))
        
        link1, link2 = links       
        self.assertEqual(50, link1.quality)
        self.assertEqual(('URPAY', 'JOSJOJAHUARINA 1'), link1.peers)

        self.assertEqual(50, link2.quality)        
        self.assertEqual(('HUIRACOCHAN', 'JOSJOJAHUARINA 1'), link2.peers)
        
        urpay_member = net1.net_members["URPAY"]
        self.assertEqual("Terminal", urpay_member.role)
        self.assertEqual("5.0m", urpay_member.antenna) 

    def test_get_units_for_network(self):
        net2 = self.report.nets.values()[1]
        self.assertEqual(['JOSJOJAHUARINA 1'],
            list(radiomobile.get_units_for_network(net2, "Node")))
        self.assertEqual(['URPAY', 'HUIRACOCHAN'],
            list(radiomobile.get_units_for_network(net2, "Terminal")))
                
if __name__ == '__main__':
    unittest.main()
