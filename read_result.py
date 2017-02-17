# coding=utf-8
# 
# Read result of trade import from Geneva system.
#
from xlrd import open_workbook
from small_program.utility import is_blank_line, is_empty_cell



def find_fail_isin(file):
	"""
	Read the result file, find the ISIN code of the failure imports.
	"""
	wb = open_workbook(filename=file)
	ws = wb.sheet_by_index(0)
	row = 1
	failure = 0
	isin_list = []
	while row < ws.nrows:
		if is_blank_line(ws, row):
			break

		if ws.cell_value(row, 29).strip() == 'Failure':
			failure = failure + 1
			isin = ws.cell_value(row, 8).strip().split()[0]
			if not isin in isin_list:
				isin_list.append(isin)

		row = row + 1
	# end of while loop

	# print(isin_list)
	print('{0} isin code found for {1} failed trade imports'.
			format(len(isin_list), failure))
	with open('bondmaster.txt', 'w') as textfile:
		for isin in isin_list:
			textfile.write('{0},Isin,,;\n'.format(isin))




if __name__ == '__main__':
	# find_fail_isin('import_result.xlsx')
	find_fail_isin('import failure csa.xlsx')