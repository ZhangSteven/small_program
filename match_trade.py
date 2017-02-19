# coding=utf-8
#
# Match the transfer record to the overall transfer transaction file
# from FT, correct their prices if necessary.
#

from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime
from ft_converter.match import match, match_repeat
from ft_converter.ft_utility import convert_datetime_to_string, \
		convert_float_to_datetime
from small_program.match_transfer import read_line, get_record_fields, \
		write_csv
from small_program.read_file import read_file
import csv



class InvalidLineInfo(Exception):
	pass



def refine_price(record_list, ft_records):
	"""
	Refine the price for all transfer records. Here we expect the CSA,
	IATSA prices are the same as in the transaction file, but CSW and
	IATSW prices are different because the latter uses book value to 
	derive the price.

	Return the updated list of CSA/CSW/IATSA/IATSW records. Other types
	of records (CALL, TNDL) are ignored.
	"""
	for (transfer, ft_transfer) in match(filter_transfer(record_list), 
											ft_records, map_transfer):
		if ft_transfer['TRADEPRC'] > 0:			
			transfer['Price'] = ft_transfer['TRADEPRC']
		else:
			transfer['Price'] = (abs(ft_transfer['CPTLAWLCL']) - abs(ft_transfer['ACCRBAS']*ft_transfer['FXRATE']))/ft_transfer['QTY']*100

	return record_list



def read_line_ft(ws, row, fields):
	"""
	Read a line in the FT transfer records file, return a transfer record.
	"""
	line_info = {}
	column = 0

	for fld in fields:
		cell_value = ws.cell_value(row, column)
		if isinstance(cell_value, str):
			cell_value = cell_value.strip()

		if fld in ['ACCT_ACNO', 'SCTYID_ISIN'] and isinstance(cell_value, float):
			cell_value = str(int(cell_value))
		
		if fld in ['TRDDATE', 'STLDATE', 'ENTRDATE']:
			cell_value = convert_float_to_datetime(cell_value)

		line_info[fld] = cell_value
		column = column + 1
	# end of for loop

	return line_info



def validate_line(line_info):
	# if line_info['TRADEPRC'] > 0:
	# 	print(abs(line_info['CPTLAWLCL']/line_info['QTY']*100.0))
	# 	if abs(line_info['CPTLAWLCL']/line_info['QTY']*100.0 - line_info['TRADEPRC']) > 0.01:
	# 		print('bond {0} has inconsistent price, on {1}'.
	# 				format(line_info['SCTYID_ISIN'], line_info['TRDDATE']))
	# 		raise InvalidLineInfo
	pass



def filter_transfer(record_list):
	"""
	Filter out bond transfer records from the record list. Bond call and 
	tender offer records will be filtered out.
	"""
	records = []
	for record in record_list:
		if '_CALLED_Sell_' in record['KeyValue'] or '_TNDRL_Sell_' in record['KeyValue']:
			continue

		records.append(record)
	
	return records



def map_transfer(record, ft_record):
	"""
	Map a transfer record to a FT transfer record.
	"""
	if ft_record['TRANCOD'] in record['KeyValue'] \
		and record['Portfolio'] == ft_record['ACCT_ACNO'] \
		and record['Investment'].split()[0] == ft_record['SCTYID_ISIN'] \
		and record['EventDate'] == ft_record['TRDDATE'] \
		and record['Quantity'] == ft_record['QTY']:
		return True

	return False




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Match the transfer records to FT transactions file and correct some of their prices.')
	parser.add_argument('record_file')
	parser.add_argument('ft_transfer_file')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.record_file):
		print('File does not exist: {0}'.format(args.record_file))
		sys.exit(1)

	records, row_in_error = read_file(args.record_file, read_line)
	if len(row_in_error) > 0:
		print('some rows in error for record file.')

	ft_records, row_in_error = read_file(args.ft_transfer_file, read_line_ft, validate_line)
	print(len(ft_records))
	if len(row_in_error) > 0:
		print('some rows in error for ft record file.')

	write_csv('refined_records.csv', get_record_fields(), refine_price(records, ft_records))



