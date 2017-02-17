# coding=utf-8
#
# Assumptions:
#
# 1. An IATSW transaction has a match to an IATSA transaction.
#

from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime
from ft_converter.match import match, match_repeat
from ft_converter.ft_utility import convert_datetime_to_string
import csv



def read_record_file(filename):
	"""
	Read the records upload file, create a list of records.
	"""
	wb = open_workbook(filename=filename)
	ws = wb.sheet_by_index(0)

	fields = read_data_fields(ws, 0)
	
	row = 1
	output = []
	row_in_error = []
	while row < ws.nrows:
		if is_blank_line(ws, row):
			break

		line_info = read_line(ws, row, fields)
		try:
			output.append(line_info)
		except:
			row_in_error.append(row)

		row = row + 1
	# end of while loop

	return output, row_in_error



def read_line(ws, row, fields):
	"""
	Read a line, create a line_info object with the information read.
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



def read_data_fields(ws, row):
	column = 0
	fields = []
	while column < ws.ncols:
		cell_value = ws.cell_value(row, column)
		if is_empty_cell(ws, row, column):
			break

		fields.append(cell_value.strip())
		column = column + 1

	return fields



def is_blank_line(ws, row):
	for i in range(5):
		if not is_empty_cell(ws, row, i):
			return False

	return True



def is_empty_cell(ws, row, column):
	cell_value = ws.cell_value(row, column)
	if not isinstance(cell_value, str) or cell_value.strip() != '':
		return False
	else:
		return True



def refine_price_iatsw(record_list):
	"""
	Refine the price for internal transfer records. Since the price for the
	IATSW records are based on book value and not accurate, we match them
	to the IATSA records and update the price.

	Return the list of IATSW records updated.
	"""
	transfer_out, transfer_in = filter_iatsw_iatsa(record_list)
	records = []
	for (iatsw, iatsa) in match(transfer_out, transfer_in, map_iatsw_iatsa):
		# print('IATSW record {0} on {1} updated price from {2} to {3}'.
		# 		format(iatsw['Investment'], iatsw['EventDate'], iatsw['Price'], iatsa['Price']))
		iatsw['Price'] = iatsa['Price']
		records.append(iatsw)

	return records



def refine_price_csw(record_list):
	"""
	Refine the price for external transfer records. Since the price for the
	CSW records are based on book value and not accurate, we match them
	to the CSA records and update the price.

	Return the list of CSW records updated, and those not updated.
	"""
	transfer_out, transfer_in = filter_iatsw_iatsa(record_list)
	records = []
	for (csw, csa) in match(transfer_out, transfer_in, map_iatsw_iatsa):
		# print('IATSW record {0} on {1} updated price from {2} to {3}'.
		# 		format(iatsw['Investment'], iatsw['EventDate'], iatsw['Price'], iatsa['Price']))
		csw['Price'] = csa['Price']
		records.append(csw)

	return records



def filter_csw(record_list):
	csw_records = []
	for record in record_list:
		if '_CSW_Sell_' in record['KeyValue']:
			csw_records.append(record)
	
	return csw_records




def filter_csw_csa(record_list):
	# transfer_in = []
	# transfer_out = []
	# for record in record_list:
	# 	if '_CSA_Buy' in record['KeyValue']:
	# 		transfer_in.append(record)
	# 	elif '_CSW_Sell_' in record['KeyValue']:
	# 		transfer_out.append(record)
	
	# return transfer_out, transfer_in

	csw_csa_records = []
	for record in record_list:
		if '_CSA_Buy' in record['KeyValue'] or '_CSW_Sell_' in record['KeyValue']:
			csw_csa_records.append(record)
	
	return csw_csa_records



def filter_iatsw_iatsa(record_list):
	transfer_in = []
	transfer_out = []
	for record in record_list:
		if '_IATSA_Buy_' in record['KeyValue']:
			transfer_in.append(record)
		elif '_IATSW_Sell_' in record['KeyValue']:
			transfer_out.append(record)
	
	return transfer_out, transfer_in



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



def get_record_fields():
	return ['RecordType', 'RecordAction', 'KeyValue', 'KeyValue.KeyName', 
			'UserTranId1', 'Portfolio', 'LocationAccount', 'Strategy', 
			'Investment', 'Broker', 'EventDate', 'SettleDate', 
			'ActualSettleDate', 'Quantity', 'Price', 'PriceDenomination',
			'CounterInvestment', 'NetInvestmentAmount', 'NetCounterAmount', 
			'TradeFX', 'NotionalAmount', 'FundStructure', 'CounterFXDenomination',
			'CounterTDateFx', 'AccruedInterest', 'InvestmentAccruedInterest',
			'TradeExpenses.ExpenseNumber', 'TradeExpenses.ExpenseCode', 
			'TradeExpenses.ExpenseAmt']



def write_csv(file, record_fields, records):
	with open(file, 'w', newline='') as csvfile:
		file_writer = csv.writer(csvfile)
		file_writer.writerow(record_fields)

		for record in records:
			row = []
			for fld in record_fields:
				if fld in ['EventDate', 'SettleDate', 'ActualSettleDate']:
					row.append(convert_datetime_to_string(record[fld]))
				else:
					row.append(record[fld])
				
			file_writer.writerow(row)



def write_csv2(file, record_fields, records):
	with open(file, 'w', newline='') as csvfile:
		file_writer = csv.writer(csvfile)
		file_writer.writerow(record_fields)

		for record in records:
			row = []
			for fld in record_fields:
				if fld in ['EventDate', 'SettleDate', 'ActualSettleDate']:
					row.append(convert_datetime_to_string(record[fld]))
				elif fld == 'Investment':
					row.append(record[fld].split()[0])
				else:
					row.append(record[fld])
				
			file_writer.writerow(row)




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Filter the transfer records and correct some of their prices.')
	parser.add_argument('record_file')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.record_file):
		print('File does not exist: {0}'.format(args.record_file))
		sys.exit(1)

	# records, row_in_error = read_record_file(args.record_file)
	# write_csv('iatsw.csv', get_record_fields(), refine_price_iatsw(records))
	# if len(row_in_error) > 0:
	# 	print('some rows in error.')

	records, row_in_error = read_record_file(args.record_file)
	write_csv2('csw2.csv', get_record_fields(), filter_csw(records))
	if len(row_in_error) > 0:
		print('some rows in error.')


