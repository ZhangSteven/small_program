# coding=utf-8
#
# Generate repo historical trades (repo master, repo trade XML files) from the input
# Excel file.
# 
#
from steven_utils.excel import getRawPositionsFromFile
from steven_utils.utility import writeCsv
from toolz.itertoolz import groupby as groupbyToolz
from toolz.functoolz import compose
from functools import partial
from itertools import chain



def loadTicketMapping(file):
	"""
	[String] file 
		=> [Iterable] ([String] master ticket, [String] collateral ticket)
	"""
	def sameRepoTrade(p):
		"""
		[Dictionary] repo position => [String] key
		"""
		return \
		str(p['Fund']) + str(p['As of Dt']) + str(p['Trd Dt']) + str(p['Stl Date']) + \
		p['Crcy'] + p['Broker ID'] + str(p['Repo Rte']) + p['Repo'] + \
		str(int(100 * p['Loan Amount'])) + str(int(100 * p['Accrued 4 Repo']))


	def getTicketTuple(group):
		"""
		[List] group => [Tuple] ([String] MRC ticket, [String] RT ticket)
		"""
		return \
		( str(int(list(filter(lambda p: p['Type'] == 'MRC', group))[0]['Tkt #']))
		, str(int(list(filter(lambda p: p['Type'] == 'RT', group))[0]['Tkt #']))
		)


	def checkGroup(group):
		"""
		[List] group => [List] group

		if nothing is wrong, return it as is
		"""
		if sorted(map(lambda p: p['Type'], group)) == ['ARC', 'MRC', 'RT']:
			return group
		else:
			print(group)
			print('\nThis group does not quality')
			raise ValueError


	return \
	compose(
		partial(map, getTicketTuple)
	  , partial(map, checkGroup)
	  , lambda d: d.values()
	  , partial(groupbyToolz, sameRepoTrade)
	  , partial(filter, lambda p: p['Repo Sta'] == 'Active')
	  , getRawPositionsFromFile
	)(file)




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Load historical report trades.')
	parser.add_argument('file')
	args = parser.parse_args()

	writeCsv( 'repo_tickets.csv'
			, chain( [('MRC Ticket', 'RT Ticket')]
				   , loadTicketMapping(args.file)
				   )
			)