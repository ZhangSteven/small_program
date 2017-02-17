# coding=utf-8
#
# Change the CSA upload to a format Terence Chau can understand.
#

from xlrd import open_workbook
from xlrd.xldate import xldate_as_datetime
from ft_converter.match import match, match_repeat
from ft_converter.ft_utility import convert_datetime_to_string
from ft_converter.ft_main import read_transaction_file
import csv, os



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



def change_records(record_list, bond_name_map):
	"""
	"""
	port_name_map = {
		'12229':'CLT-CLI HK BR (CLASS A - HK) TRUST FUND (SUB-FUND-BOND)',
		'12630':'CLT-CLI HK BR (CLASS G - HK) TRUST FUND (SUB-FUND-BOND)',
		'12366':'CLT-CLI MACAU BR (CLASS A - MC) TRUST FUND (SUB-FUND-BOND)',
		'12548':'CLT-CLI MACAU BR (CLASS G - MC) TRUST FUND (SUB-FUND-BOND)',
		'12528':'CLT-CLI HK BR (CLASS A - HK) TRUST FUND (SUB-FUND - TRADING BOND)',
		'12732':'CLT-CLI HK BR TRUST FUND (Capital) (Sub Fund Bond)',
		'12733':'CLT-CLI Overseas TRUST FUND (Capital) (Sub Fund Bond)'
	}

	for record in record_list:
		if 'CSA_Buy' in record['KeyValue']:
			record['RecordType'] = 'Transfer In (external)'
		elif 'CSW_Sell' in record['KeyValue']:
			record['RecordType'] = 'Transfer Out (external)'
		elif 'IATSA_Buy' in record['KeyValue']:
			record['RecordType'] = 'Transfer In (internal)'
		elif 'IATSW_Sell' in record['KeyValue']:
			record['RecordType'] = 'Transfer Out (internal)'

		record['PortfolioName'] = port_name_map[record['Portfolio']]
		record['Investment'] = record['Investment'].split()[0]
		record['BondName'] = bond_name_map[record['Investment']]



def get_record_fields():
	return ['RecordType', 'RecordAction', 'KeyValue', 'KeyValue.KeyName', 
			'UserTranId1', 'Portfolio', 'PortfolioName', 'LocationAccount', 'Strategy', 
			'Investment', 'BondName', 'Broker', 'EventDate', 'SettleDate', 
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



def create_bond_name_map():
	"""
	Map ISIN code to bond name.
	"""
	input_directory = r'C:\Users\steven.zhang\Desktop\data conversion\CLO Bond'
	portfolios = ['12229', '12366', '12528', '12548', '12630', '12732', '12733']
	name_map = {}

	for portfolio in portfolios:
		transaction_file = os.path.join(input_directory, 'transactions {0} no initial pos.xls'.format(portfolio))
		output, row_in_error = read_transaction_file(transaction_file)
		for transaction in output:
			if transaction['TRANTYP'] in ['CALLED', 'CSA', 'CSW', 'IATSA', 
											'IATSW', 'SACA', 'SWCA', 'Purch', 
											'Sale', 'SctyAdd', 'SCTYWTH', 'SWCA', 
											'TNDRL']:
				if transaction['SCTYID_ISIN'] != '':
					if not transaction['SCTYID_ISIN'] in name_map:
						name_map[transaction['SCTYID_ISIN']] = transaction['SCTYNM']
				else:
					print('bond:{0} does not have an ISIN code'.format(transaction['SCTYNM']))						

	return name_map



if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Filter the transfer records and correct some of their prices.')
	parser.add_argument('record_file')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.record_file):
		print('File does not exist: {0}'.format(args.record_file))
		sys.exit(1)

	records, row_in_error = read_record_file(args.record_file)
	change_records(records, create_bond_name_map())
	write_csv('transfer_records.csv', get_record_fields(), records)
	if len(row_in_error) > 0:
		print('some rows in error.')


