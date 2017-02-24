# coding=utf-8
#
# Read the unmatched_position.xlsx file and the bond_issue.xlsx file,
# find out whether the unmatched positions are bought when the bond are
# issued.
#

from xlrd.xldate import xldate_as_datetime
from ft_converter.match import match_repeat
from ft_converter.ft_utility import convert_datetime_to_string
from small_program.match_transfer import write_csv
from small_program.read_file import read_file
from small_program.utility import get_current_path
import csv



def create_position_date(positions, bond_issues):
	"""
	Match tax lots in trustee records to buy trade records, so that we can
	populate the date of the matched tax lots to the settlement date of
	the trade record.
	"""
	matched, unmatched = match_repeat(positions, bond_issues, map_position_bond_issue)
	for (position, bond_issue) in matched:
		position['date'] = bond_issue['Issue date']

	# for position in positions:
	# 	position['Portfolio'] = map_portfolio_code(position['Portfolio'])

	return positions, unmatched



def read_line_position(ws, row, fields):
	"""
	Read a line in the unmatched position file, return a position record.
	"""
	line_info = {}
	column = 0

	for fld in fields:

		cell_value = ws.cell_value(row, column)
		if isinstance(cell_value, str):
			cell_value = cell_value.strip()

		if fld == 'Portfolio' and isinstance(cell_value, float):
			cell_value = str(int(cell_value))

		if fld in ['Interest Start Day', 'Maturity']:
			cell_value = convert_datetime_to_string(xldate_as_datetime(cell_value, 0))

		line_info[fld] = cell_value
		column = column + 1
	# end of for loop

	return line_info



def read_line_bond(ws, row, fields):
	"""
	Read a line in the bond issue file, return a bond issue record.
	"""
	line_info = {}
	column = 0

	for fld in fields:
		cell_value = ws.cell_value(row, column)
		if isinstance(cell_value, str):
			cell_value = cell_value.strip()
		
		if fld == 'Issue date':
			# print(cell_value)
			day, month, year = cell_value.split('/')
			cell_value = year + '-' + month + '-' + day

		line_info[fld] = cell_value
		column = column + 1
	# end of for loop

	return line_info



def map_position_bond_issue(position, bond_issue):
	if isinstance(bond_issue['Reoffer price'], float):
		price = bond_issue['Reoffer price']
	elif isinstance(bond_issue['Issue price'], float):
		price = bond_issue['Issue price']

	if position['Description'].split()[0] == bond_issue['ISIN'] \
		and abs(position['Average Cost'] - price) < 0.0001:
		return True

	return False



def get_record_fields():
	return ['Portfolio', 'Description', 'Currency', 'Par Amount', 'Coupon', 
			'Interest Start Day', 'Maturity', 'date', 'Average Cost', 
			'Amortized Price',	'Cost', 'Accrued Interest']



def get_isin_list(unmatched):
	unmatched_isin = []
	for record in unmatched:
		isin = record['Description'].split()[0]
		if not isin in unmatched_isin:
			unmatched_isin.append(isin)

	return unmatched_isin



def map_portfolio_code(portfolio_id):
	port_name_map = {
		'12229':'CLT-CLI HK BR (CLASS A - HK) TRUST FUND (SUB-FUND-BOND)',
		'12630':'CLT-CLI HK BR (CLASS G - HK) TRUST FUND (SUB-FUND-BOND)',
		'12366':'CLT-CLI MACAU BR (CLASS A - MC) TRUST FUND (SUB-FUND-BOND)',
		'12548':'CLT-CLI MACAU BR (CLASS G - MC) TRUST FUND (SUB-FUND-BOND)',
		'12528':'CLT-CLI HK BR (CLASS A - HK) TRUST FUND (SUB-FUND - TRADING BOND)',
		'12732':'CLT-CLI HK BR TRUST FUND (Capital) (Sub Fund Bond)',
		'12733':'CLT-CLI Overseas TRUST FUND (Capital) (Sub Fund Bond)',
		'12734':'CLT-CLI HK BR (Class A-HK) Trust Fund - Sub Fund I'
	}

	return port_name_map[portfolio_id]




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Match the unmatched position to bond issue records to determine the tax lot dates.')
	parser.add_argument('unmatched_position')
	parser.add_argument('bond_issue')
	args = parser.parse_args()

	import os, sys
	if not os.path.exists(args.unmatched_position) or not os.path.exists(args.bond_issue):
		print('File does not exist: {0} or {1}'.format(args.unmatched_position, args.bond_issue))
		sys.exit(1)

	positions, row_in_error = read_file(args.unmatched_position, read_line_position)
	if len(row_in_error) > 0:
		print('Some rows in error when reading unmatched record file.')

	bond_issues, row_in_error = read_file(args.bond_issue, read_line_bond)
	if len(row_in_error) > 0:
		print('Some rows in error when reading bond issue file.')

	positions, unmatched = create_position_date(positions, bond_issues)
	write_csv('unmatched_position_refined.csv', get_record_fields(), positions)

	write_csv('unmatched_isin_2.csv', ['isin'], 
				[{'isin':x} for x in get_isin_list(unmatched)])