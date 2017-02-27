"""
Test the open_jpm.py
"""

import unittest2
from datetime import datetime
from os.path import join
from small_program.utility import get_current_path
from small_program.read_file import read_file
from small_program.match_trade import refine_price, read_line, read_line_ft, \
                                filter_transfer



class TestMatchTrade(unittest2.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestMatchTrade, self).__init__(*args, **kwargs)

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



    def test_refine_price(self):
        file = join(get_current_path(), 'samples', 'csa_upload_without_12528.xlsx')
        records, row_in_error = read_file(file, read_line)
        self.assertEqual(len(row_in_error), 0)
        self.assertEqual(len(filter_transfer(records)), 287)


        file = join(get_current_path(), 'samples', 'transfer transactions.xls')
        ft_records, row_in_error = read_file(file, read_line_ft)       
        self.assertEqual(len(row_in_error), 0)

        records = refine_price(records, ft_records)
        self.assertEqual(len(records), 296)

        r = filter_record(records, 'CSW', 'US46625HGY09', '12229', datetime(2009,12,29),  3000000)
        self.assertAlmostEqual(r['Price'], 107.8825)

        r = filter_record(records, 'CSA', 'US268317AB08', '12366', datetime(2012,8,23),  100000)
        self.assertAlmostEqual(r['Price'], 104.784)

        r = filter_record(records, 'IATSA', 'XS1189103382', '12366', datetime(2015,3,10),  3200000)
        self.assertAlmostEqual(r['Price'], 98.523)

        r = filter_record(records, 'CSA', 'XS0368899695', '12366', datetime(2009,12,29),  600000)
        self.assertAlmostEqual(r['Price'], 103.48)



def filter_record(record_list, action, isin, portfolio, trade_date, quantity):
    for record in record_list:
        if action in record['KeyValue'] \
            and portfolio == record['Portfolio'] \
            and isin == record['Investment'].split()[0] \
            and trade_date == record['EventDate'] \
            and quantity == record['Quantity']:

            return record

    return None # if nothing found