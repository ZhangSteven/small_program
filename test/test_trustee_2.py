"""
Test the trustee_2.py
"""

import unittest2
from datetime import datetime
from os.path import join
from small_program.utility import get_current_path
from small_program.read_file import read_file
from small_program.trustee_2 import read_line_position, read_line_bond



class TestTrustee(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTrustee, self).__init__(*args, **kwargs)

    def setUp(self):
        """
            Run before a test function
        """
        pass

    def tearDown(self):
        """
            Run after a test finishes
        """
        pass



    def test_read_line_position(self):
        file = join(get_current_path(), 'samples', 'unmatched_position.xlsx')
        records, row_in_error = read_file(file, read_line_position)
        self.assertEqual(len(records), 151)
        self.assertEqual(len(row_in_error), 0)
        self.verify_position_record1(records[0])
        self.verify_position_record2(records[150])



    def test_read_line_bond(self):
        file1 = join(get_current_path(), 'samples', 'bond_issue.xlsx')
        records, row_in_error = read_file(file1, read_line_bond)
        self.assertEqual(len(records), 51)
        self.assertEqual(len(row_in_error), 0)
        self.verify_bond_record1(records[0])
        self.verify_bond_record2(records[47])



    # def test_map_trade_tax_lot(self):
    #     trustee_records, trade_records = self.read_both_files()
    #     self.assertEqual(len(trustee_records), 7)
    #     self.assertEqual(len(trade_records), 5)
    #     self.assertTrue(map_trade_tax_lot(trustee_records[1], trade_records[1]))
    #     self.assertFalse(map_trade_tax_lot(trustee_records[2], trade_records[1]))
    #     self.assertFalse(map_trade_tax_lot(trustee_records[2], trade_records[2]))
    #     self.assertTrue(map_trade_tax_lot(trustee_records[5], trade_records[4]))
    #     self.assertFalse(map_trade_tax_lot(trustee_records[5], trade_records[3]))



    # def test_create_tax_lot_date(self):
    #     trustee_records, trade_records = self.read_both_files()
    #     new_trustee_records, unmatched = create_tax_lot_date(trustee_records, trade_records)
    #     self.assertEqual(len(new_trustee_records), 7)
    #     self.assertEqual(len(unmatched), 5)
    #     self.assertEqual(new_trustee_records[0]['date'], '')
    #     self.assertEqual(new_trustee_records[1]['date'], '2009-6-2')
    #     self.assertEqual(new_trustee_records[2]['date'], '')
    #     self.assertEqual(new_trustee_records[5]['date'], '2016-12-14')
    #     self.assertEqual(new_trustee_records[6]['date'], '')
    #     self.assertEqual(unmatched[0]['Description'].split()[0], 'HK0000097490')
    #     self.assertEqual(unmatched[1]['Description'].split()[0], 'HK0000134780')
    #     self.assertEqual(unmatched[4]['Description'].split()[0], 'XS1529948934')



    # def read_both_files(self):
    #     trustee_file = join(get_current_path(), 'samples', '12229_match_sample.xlsx')
    #     trustee_records, row_in_error = read_file(trustee_file, read_line_trustee)
    #     trade_file = join(get_current_path(), 'samples', 'trade_upload_match_sample.xlsx')
    #     trade_records, row_in_error = read_file(trade_file, read_line_trade)
    #     return trustee_records, trade_records



    def verify_position_record1(self, record):
        self.assertEqual(len(record), 12)
        self.assertEqual(record['Description'], 'HK0000097490 CN Pwr N Energy6.5%')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertAlmostEqual(record['Average Cost'], 100)
        self.assertEqual(record['Maturity'], '2017-1-9')



    def verify_position_record2(self, record):
        self.assertEqual(len(record), 12)
        self.assertEqual(record['Description'], 'XS1529948934 DEUTSCHE BANK AG 5.2')
        self.assertEqual(record['Portfolio'], '12734')
        self.assertAlmostEqual(record['Average Cost'], 99.8357143)
        self.assertEqual(record['Interest Start Day'], '2016-12-14')



    def verify_bond_record1(self, record):
        self.assertEqual(len(record), 4)
        self.assertEqual(record['ISIN'], 'HK0000097490')
        self.assertEqual(record['Reoffer price'], '#N/A Field Not Applicable')
        self.assertAlmostEqual(record['Issue price'], 100)
        self.assertEqual(record['Issue date'], '2012-1-9')



    def verify_bond_record2(self, record):
        self.assertEqual(len(record), 4)
        self.assertEqual(record['ISIN'], 'US55608JAB44')
        self.assertAlmostEqual(record['Issue price'], 99.566)
        self.assertAlmostEqual(record['Reoffer price'], 99.566)
        self.assertEqual(record['Issue date'], '2009-8-13')



    # def verify_trade_record1(self, record):
    #     self.assertEqual(len(record), 23)
    #     self.assertEqual(record['RecordType'], 'Buy')
    #     self.assertEqual(record['Quantity'], 49600000)
    #     self.assertEqual(record['Investment'], 'FR0013101599 HTM')
    #     self.assertEqual(record['Portfolio'], '12229')
    #     self.assertEqual(record['EventDate'], datetime(2016, 1, 15))
    #     self.assertAlmostEqual(record['Price'], 98.233)



    # def verify_trade_record2(self, record):
    #     self.assertEqual(len(record), 23)
    #     self.assertEqual(record['RecordType'], 'Buy')
    #     self.assertEqual(record['Investment'], 'XS1529948934 HTM')
    #     self.assertEqual(record['Portfolio'], '12229')
    #     self.assertEqual(record['SettleDate'], datetime(2016, 12, 14))
    #     self.assertAlmostEqual(record['Price'], 100)
    #     self.assertAlmostEqual(record['CounterInvestment'], 'USD')