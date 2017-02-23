"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import join
from small_program.utility import get_current_path
from small_program.read_file import read_file
from small_program.trustee import read_line_trustee, read_line_trade, \
                                    create_tax_lot_date, map_trade_tax_lot



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



    def test_read_line_trustee(self):
        trustee_file = join(get_current_path(), 'samples', '12229_sample.xlsx')
        records, row_in_error = read_file(trustee_file, read_line_trustee)
        self.assertEqual(len(records), 7)
        self.assertEqual(len(row_in_error), 0)
        self.verify_trustee_record1(records[0])
        self.verify_trustee_record2(records[6])



    def test_read_line_trade(self):
        trade_file = join(get_current_path(), 'samples', 'trade_upload_sample.xlsx')
        records, row_in_error = read_file(trade_file, read_line_trade)
        self.assertEqual(len(records), 5)
        self.assertEqual(len(row_in_error), 0)
        self.verify_trade_record1(records[0])
        self.verify_trade_record2(records[4])



    def test_map_trade_tax_lot(self):
        trustee_records, trade_records = self.read_both_files()
        self.assertEqual(len(trustee_records), 7)
        self.assertEqual(len(trade_records), 5)
        self.assertTrue(map_trade_tax_lot(trustee_records[1], trade_records[1]))
        self.assertFalse(map_trade_tax_lot(trustee_records[2], trade_records[1]))
        self.assertFalse(map_trade_tax_lot(trustee_records[2], trade_records[2]))
        self.assertTrue(map_trade_tax_lot(trustee_records[5], trade_records[4]))
        self.assertFalse(map_trade_tax_lot(trustee_records[5], trade_records[3]))



    def test_create_tax_lot_date(self):
        trustee_records, trade_records = self.read_both_files()
        new_trustee_records, unmatched_isin = create_tax_lot_date(trustee_records, trade_records)
        self.assertEqual(len(new_trustee_records), 7)
        self.assertEqual(len(unmatched_isin), 5)
        self.assertEqual(new_trustee_records[0]['date'], '')
        self.assertEqual(new_trustee_records[1]['date'], '2009-6-2')
        self.assertEqual(new_trustee_records[2]['date'], '')
        self.assertEqual(new_trustee_records[5]['date'], '2016-12-14')
        self.assertEqual(new_trustee_records[6]['date'], '')
        self.assertEqual(unmatched_isin[0], 'HK0000097490')
        self.assertEqual(unmatched_isin[1], 'HK0000134780')
        self.assertEqual(unmatched_isin[4], 'XS1529948934')
        self.assertFalse('XS1523197892' in unmatched_isin)



    def read_both_files(self):
        trustee_file = join(get_current_path(), 'samples', '12229_match_sample.xlsx')
        trustee_records, row_in_error = read_file(trustee_file, read_line_trustee)
        trade_file = join(get_current_path(), 'samples', 'trade_upload_match_sample.xlsx')
        trade_records, row_in_error = read_file(trade_file, read_line_trade)
        return trustee_records, trade_records



    def verify_trustee_record1(self, record):
        self.assertEqual(len(record), 18)
        self.assertEqual(record['Description'], 'HK0000097490 CN Pwr N Energy6.5%')
        self.assertAlmostEqual(record['Average Cost'], 100)
        self.assertEqual(record['Currency'], 'CNY')



    def verify_trustee_record2(self, record):
        self.assertEqual(len(record), 18)
        self.assertEqual(record['Description'], 'XS1529948934 DEUTSCHE BANK AG 5.2')
        self.assertAlmostEqual(record['Coupon'], 5.2)
        self.assertEqual(record['Interest Start Day'], '2016-12-14')



    def verify_trade_record1(self, record):
        self.assertEqual(len(record), 23)
        self.assertEqual(record['RecordType'], 'Buy')
        self.assertEqual(record['Quantity'], 49600000)
        self.assertEqual(record['Investment'], 'FR0013101599 HTM')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertEqual(record['EventDate'], datetime(2016, 1, 15))
        self.assertAlmostEqual(record['Price'], 98.233)



    def verify_trade_record2(self, record):
        self.assertEqual(len(record), 23)
        self.assertEqual(record['RecordType'], 'Buy')
        self.assertEqual(record['Investment'], 'XS1529948934 HTM')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertEqual(record['SettleDate'], datetime(2016, 12, 14))
        self.assertAlmostEqual(record['Price'], 100)
        self.assertAlmostEqual(record['CounterInvestment'], 'USD')