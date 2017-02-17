# coding=utf-8
# 
# Read mismatch results from Geneva position recon.
#
from xlrd import open_workbook
from small_program.utility import is_blank_line, is_empty_cell



def read_fields(file):
	wb = open_workbook(filename=file)
	ws = wb.sheet_by_index(0)
	column = 0
	fields = []
	while column < ws.ncols:
		if is_empty_cell(ws, 0, column):
			break

		fields.append(ws.cell_value(0, column).strip())
		column = column + 1

	return fields



def find_mismatch(file):
	"""
	Read the position recon file, find mismatches.
	"""
	wb = open_workbook(filename=file)
	ws = wb.sheet_by_index(0)
	row = 1
	mismatches = {}

	while row < ws.nrows:
		if is_blank_line(ws, row):
			break

		for fld in read_fields(file):
			
		row = row + 1
	# end of while loop




if __name__ == '__main__':
	print(read_fields('mismatch/12229 match results 0118 morning.xlsx'))