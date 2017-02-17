"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import join
from small_program.utility import get_current_path
from small_program.match_transfer import read_record_file, refine_price_iatsw



class TestMatchTransfer(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMatchTransfer, self).__init__(*args, **kwargs)

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



    def test_read_record_file(self):
        file = join(get_current_path(), 'samples', 'csa_upload_without_12528.xlsx')
        records, row_in_error = read_record_file(file)
        self.assertEqual(len(records), 296)
        self.assertEqual(len(row_in_error), 0)
        self.verify_record1(records[0])
        self.verify_record2(records[283])   # in row 285



    def test_refine_price_iatsw(self):
        file = join(get_current_path(), 'samples', 'csa_sample1.xlsx')
        records, row_in_error = read_record_file(file)
        iatsw_records = refine_price_iatsw(records)
        self.assertEqual(len(iatsw_records), 7)
        self.verify_iatsw_record1(iatsw_records[0])
        self.verify_iatsw_record2(iatsw_records[3])
        self.verify_iatsw_record3(iatsw_records[6])



    def verify_record1(self, record):
        self.assertEqual(len(record), 29)
        self.assertEqual(record['RecordType'], 'Buy')
        self.assertEqual(record['KeyValue'], '12229_2008-12-23_CSA_Buy_US02580ECC57_HTM_6138531899')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertEqual(record['LocationAccount'], 'BOCHK')
        self.assertEqual(record['EventDate'], datetime(2008, 12, 23))
        self.assertAlmostEqual(record['Quantity'], 80000)
        self.assertAlmostEqual(record['Price'], 99.0699375)
        self.assertEqual(record['Investment'], 'US02580ECC57 HTM')



    def verify_record2(self, record):
        self.assertEqual(len(record), 29)
        self.assertEqual(record['RecordType'], 'Sell')
        self.assertEqual(record['KeyValue'], '12630_2014-9-3_CALLED_Sell_US911271AB07_HTM_77503500600')
        self.assertEqual(record['Portfolio'], '12630')
        self.assertEqual(record['LocationAccount'], 'BOCHK')
        self.assertEqual(record['EventDate'], datetime(2014, 9, 3))
        self.assertAlmostEqual(record['Quantity'], 1000000)
        self.assertAlmostEqual(record['Price'], 99.9999999492085)
        self.assertEqual(record['Investment'], 'US911271AB07 HTM')



    def verify_iatsw_record1(self, record):
        self.assertEqual(len(record), 29)
        self.assertEqual(record['RecordType'], 'Sell')
        self.assertEqual(record['KeyValue'], '12229_2016-1-28_IATSW_Sell_FR0013101599_HTM_2144432284700')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertEqual(record['LocationAccount'], 'BOCHK')
        self.assertEqual(record['EventDate'], datetime(2016, 1, 28))
        self.assertAlmostEqual(record['Quantity'], 28000000)
        self.assertAlmostEqual(record['Price'], 98.233)
        self.assertEqual(record['Investment'], 'FR0013101599 HTM')



    def verify_iatsw_record2(self, record):
        self.assertEqual(len(record), 29)
        self.assertEqual(record['RecordType'], 'Sell')
        self.assertEqual(record['KeyValue'], '12229_2016-4-18_IATSW_Sell_XS1389124774_HTM_2947773999500')
        self.assertEqual(record['Portfolio'], '12229')
        self.assertEqual(record['LocationAccount'], 'BOCHK')
        self.assertEqual(record['EventDate'], datetime(2016, 4, 18))
        self.assertAlmostEqual(record['Quantity'], 38000000)
        self.assertAlmostEqual(record['Price'], 100)
        self.assertEqual(record['Investment'], 'XS1389124774 HTM')



    def verify_iatsw_record3(self, record):
        self.assertEqual(len(record), 29)
        self.assertEqual(record['RecordType'], 'Sell')
        self.assertEqual(record['KeyValue'], '12366_2016-8-11_IATSW_Sell_XS1389124774_HTM_77549004800')
        self.assertEqual(record['Portfolio'], '12366')
        self.assertEqual(record['LocationAccount'], 'BOCHK')
        self.assertEqual(record['EventDate'], datetime(2016, 8, 11))
        self.assertAlmostEqual(record['Quantity'], 1000000)
        self.assertAlmostEqual(record['Price'], 100)
        self.assertEqual(record['Investment'], 'XS1389124774 HTM')
