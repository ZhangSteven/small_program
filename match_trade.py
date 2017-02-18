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



def refine_price(record_list, ft_transfer_file):
	"""
	Refine the price for all transfer records. Here we expect the CSA,
	IATSA prices are the same as in the transaction file, but CSW and
	IATSW prices are different because the latter uses book value to 
	derive the price.

	Return the updated list of CSA/CSW/IATSA/IATSW records. Other types
	of records (CALL, TNDL) are ignored.
	"""
	for (transfer, ft_transfer) in match(filter_transfer(record_list), 
											read_file(ft_transfer_file, read_line_ft, validate_line), 
											map_transfer):
		transfer['Price'] = ft_transfer['Price']

	return record_list



def read_line_ft(ws, row):
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
	if line_info['TRADEPRC'] > 0:
		if abs(line_info['CPTLAWLCL']/line_info['QTY']*100.0 - line_info['TRADEPRC']) > 0.000001:
			print('bond {0} has inconsistent price, on {1}'.
					format(line_info['SCTYID_ISIN'], line_info['TRDDATE']))
			raise InvalidLineInfo



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



def map_csw_csa(transfer_out, transfer_in):
	"""
	Map a CSW record to a CSA record.
	"""
	if transfer_out['EventDate'] == transfer_in['EventDate'] \
		and transfer_out['Investment'] == transfer_in['Investment']:
		return True

	return False



def map_iatsw_iatsa(transfer_out, transfer_in):
	"""
	Map an IATSW record to an IATSA record.
	"""
	if transfer_out['EventDate'] == transfer_in['EventDate'] \
		and transfer_out['Investment'] == transfer_in['Investment'] \
		and transfer_out['Quantity'] == transfer_in['Quantity'] \
		and transfer_out['Portfolio'] != transfer_in['Portfolio']:
		return True

	return False




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Match the transfer records to FT transactions file and correct some of their prices.')
	parser.add_argument('record_file')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.record_file):
		print('File does not exist: {0}'.format(args.record_file))
		sys.exit(1)

	records, row_in_error = read_file(args.record_file, read_line)
	# write_csv('iatsw.csv', get_record_fields(), refine_price(records))
	# if len(row_in_error) > 0:
	# 	print('some rows in error.')



