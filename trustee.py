# coding=utf-8
#
# Read the trustee file (12229.xls) and match the record there to the buy
# records from FT.
#

from xlrd.xldate import xldate_as_datetime
from ft_converter.match import match_repeat
from ft_converter.ft_utility import convert_datetime_to_string
from small_program.match_transfer import write_csv
from small_program.read_file import read_file
from small_program.utility import get_current_path
import csv



def create_tax_lot_date(trustee_records, trade_records):
	"""
	Match tax lots in trustee records to buy trade records, so that we can
	populate the date of the matched tax lots to the settlement date of
	the trade record.
	"""
	matched, unmatched = match_repeat(trustee_records, trade_records, map_trade_tax_lot)
	for (trustee_record, trade_record) in matched:
		trustee_record['date'] = convert_datetime_to_string(trade_record['SettleDate'])

	unmatched_isin = []
	for trustee_record in unmatched:
		trustee_record['date'] = ''

		isin = trustee_record['Description'].split()[0]
		if not isin in unmatched_isin: 
			unmatched_isin.append(isin)

	return trustee_records, unmatched_isin



def read_line_trustee(ws, row, fields):
	"""
	Read a line in the trustee NAV records file, return a tax lot record.
	"""
	line_info = {}
	column = 0

	for fld in fields:
		if fld == '':
			continue

		cell_value = ws.cell_value(row, column)
		if isinstance(cell_value, str):
			cell_value = cell_value.strip()

		if fld in ['Interest Start Day', 'Maturity']:
			cell_value = convert_datetime_to_string(xldate_as_datetime(cell_value, 0))

		line_info[fld] = cell_value
		column = column + 1
	# end of for loop

	return line_info



def read_line_trade(ws, row, fields):
	"""
	Read a line in the trade upload file, return a trade record.
	"""
	line_info = {}
	column = 0

	for fld in fields:
		cell_value = ws.cell_value(row, column)
		if isinstance(cell_value, str):
			cell_value = cell_value.strip()

		if fld == 'Portfolio' and isinstance(cell_value, float):
			cell_value = str(int(cell_value))
		
		if fld in ['EventDate', 'SettleDate', 'ActualSettleDate']:
			cell_value = xldate_as_datetime(cell_value, 0)

		line_info[fld] = cell_value
		column = column + 1
	# end of for loop

	return line_info



def map_trade_tax_lot(trustee_record, trade_record):
	"""
	Map a tax lot (trustee record) to a buy trade record.
	"""
	# print(trustee_record['Description'].split()[0])
	# print(trade_record['Investment'].split()[0])
	# print(abs(trustee_record['Average Cost'] - trade_record['Price']))
	if trade_record['RecordType'] == 'Buy' \
		and trustee_record['Description'].split()[0] == trade_record['Investment'].split()[0] \
		and abs(trustee_record['Average Cost'] - trade_record['Price']) < 0.0001:
		return True

	return False



def get_record_fields():
	return ['Description', 'Currency', 'Par Amount', 'Coupon', 
			'Interest Start Day', 'Maturity', 'date', 'Average Cost', 
			'Amortized Price',	'Cost', 'Accrued Interest']



if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Match the trustee records to FT buy records to determine the tax lot dates.')
	parser.add_argument('ft_trade_file')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.ft_trade_file):
		print('File does not exist: {0} or {1}'.format(args.trustee_file, args.ft_trade_file))
		sys.exit(1)

	trade_records, row_in_error = read_file(args.ft_trade_file, read_line_trade)
	if len(row_in_error) > 0:
		print('Some rows in error when reading trade record file.')

	portfolios = ['12229', '12366', '12528', '12548', '12630', '12732', '12733', '12734']
	total_unmatched_isin = []
	for p in portfolios:
		trustee_records, row_in_error = read_file('trustee\\{0}.xlsx'.format(p), read_line_trustee)
		if len(row_in_error) > 0:
			print('Some rows in error when reading trustee record {0}'.format(p))

		trustee_records, unmatched_isin = create_tax_lot_date(trustee_records, trade_records)
		write_csv('{0}_refined.csv'.format(p), get_record_fields(), trustee_records)
		
		# end of for loop

