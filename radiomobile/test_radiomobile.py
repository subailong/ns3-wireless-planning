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

    def test_get_position_from_reference(self):
      unit1 = (40.86, 0.16)
      unit2 = (41.38, 2.17)
      reference = radiomobile.get_reference(unit1)
      position1 = radiomobile.get_position_from_reference(unit1, reference)
      self.assertEqual(position1, (0.0, 0.0))
      position2 = radiomobile.get_position_from_reference(unit2, reference)
      self.assertEqual(position2, (169469, 57747))
              
    def test_generated_on(self):
        self.assertEqual(datetime(2007, 7, 4, 17, 38, 51), self.report.generated_on)
                      
    def test_units(self):
        units = self.report.units
        expected_units = ['URPAY', 'HUIRACOCHAN', 'JOSJOJAHUARINA 1', 'JOSJOJAHUARINA 2'] 
        self.assertEqual(expected_units, units.keys())
    
    def test_unit_details(self):
        units = self.report.units
        urpay = units["URPAY"]        
        self.assertEqual("""13°42'42"S 071°39'55"W 19L BE 11727 82575""", urpay.location) 
        self.assertEqual(3420, urpay.elevation) 
            
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
        self.assertEqual(['1. Josjo1AP - Josjo2', '2. Josjo1 AP - Huiracochan, Ur'], nets.keys())
        
        net1 = nets['2. Josjo1 AP - Huiracochan, Ur']
        self.assertEqual(50, net1.max_quality)
        self.assertEqual(2, len(net1.links))

    def test_net_details(self):
        net1 = self.report.nets['2. Josjo1 AP - Huiracochan, Ur']
        links = net1.links
        
        link1, link2 = links       
        self.assertEqual(10756, link1.distance)
        self.assertEqual(50, link1.quality)
        self.assertEqual(('URPAY', 'JOSJOJAHUARINA 1'), link1.peers)        

        self.assertEqual(50, link2.quality)        
        self.assertEqual(('HUIRACOCHAN', 'JOSJOJAHUARINA 1'), link2.peers)
        
        member1 = net1.net_members["URPAY"]
        self.assertEqual("Terminal", member1.role)
        self.assertEqual("5.0m", member1.antenna) 

        member2 = net1.net_members["HUIRACOCHAN"]
        self.assertEqual("12.0m", member2.antenna) 
        self.assertEqual("Terminal", member2.role)

    def test_get_units_for_network(self):
        net2 = self.report.nets.values()[1]
        self.assertEqual(['JOSJOJAHUARINA 1'],
            list(radiomobile.get_units_for_network(net2, "Node")))
        self.assertEqual(['URPAY', 'HUIRACOCHAN'],
            list(radiomobile.get_units_for_network(net2, "Terminal")))
                
if __name__ == '__main__':
    unittest.main()
