# coding=utf-8
#
# A generic read excel file module.
#

from xlrd import open_workbook



def read_file(filename, read_line_function, validate_function=None, starting_row=0):
	"""
	A generic function to read an excel file and create a list of records.

	Assumptions:

	1. The file has only one sheet.
	2. The file format: the 'starting_row' line contain the column names 
		(data fields), second line onwards are the data.
	3. When a blank line (5 consecutive blank cells) appears, the reading
		stops.
	"""
	wb = open_workbook(filename=filename)
	ws = wb.sheet_by_index(0)

	fields = read_data_fields(ws, starting_row)
	
	row = starting_row + 1
	output = []
	row_in_error = []
	while row < ws.nrows:
		if is_blank_line(ws, row):
			break

		line_info = read_line_function(ws, row, fields)
		if not validate_function is None:
			try:
				validate_function(line_info)
				output.append(line_info)
			except:
				row_in_error.append(row)
		else:
			output.append(line_info)

		# try:
		# 	output.append(line_info)
		# 	if not validate_function is None:
		# 		validate_function(line_info)
		# except:
		# 	row_in_error.append(row)

		row = row + 1
	# end of while loop

	return output, row_in_error



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