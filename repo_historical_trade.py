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
from datetime import datetime



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



def repoMasterXml(position):
	"""
	[Dictionary] position (from XFIN file with repo name and collateral ticket#)
		=> [String] xml content for repo master 
	"""
	repoName = position['Repo Name'].strip()
	currency = position['Curr'].strip()
	if position['Day Count'] != 'ACT/360':
		print('invalid day count: {0}'.format(position))
		raise ValueError


	return \
	'<Bond_InsertUpdate>' + '\n' + \
	'<KeyValue KeyName="Code">{0}</KeyValue>'.format(repoName) + '\n' + \
	'<Code>{0}</Code>'.format(repoName) + '\n' + \
	'<Description>{0}</Description>'.format(repoName) + '\n' + \
	'<AssetType>FI</AssetType>' + '\n' + \
	'<BifurcationCurrency>{0}</BifurcationCurrency>'.format(currency) + '\n' + \
	'<CouponFreq>Annual</CouponFreq>' + '\n' + \
	'<DatedDate>2001-01-01T00:00:00</DatedDate>' + '\n' + \
	'<Exchange>OTC</Exchange>' + '\n' + \
	'<IncomeCurrency>{0}</IncomeCurrency>'.format(currency) + '\n' + \
	'<InvestmentType>REPO</InvestmentType>' + '\n' + \
	'<IssueCountry>HK</IssueCountry>' + '\n' + \
	'<IssueDate>2001-01-01T00:00:00</IssueDate>' + '\n' + \
	'<MaturityDate>2199-12-31T00:00:00</MaturityDate>' + '\n' + \
	'<PricingFactor>0.01</PricingFactor>' + '\n' + \
	'<PrincipalCurrency>{0}</PrincipalCurrency>'.format(currency) + '\n' + \
	'<QuantityPrecision>0</QuantityPrecision>' + '\n' + \
	'<RiskCurrency>{0}</RiskCurrency>'.format(currency) + '\n' + \
	'<TradingFactor>1</TradingFactor>' + '\n' + \
	'<AccrualDaysPerMonth>Actual</AccrualDaysPerMonth>' + '\n' + \
	'<AccrualDaysPerYear>360</AccrualDaysPerYear>' + '\n' + \
	'<RepoAgreementFlag>1</RepoAgreementFlag>' + '\n' + \
	'</Bond_InsertUpdate>'
# End of repoMasterXml()



def createRepoMasterXmlFile(file):
	"""
	[String] XFIN file with repo name and collateral ticket#
		=> [String] repo master xml file (without headers)

	Side effect: write an XML file in the local directory.
	"""
	def getMasterXmlContent(file):
		return \
		compose(
			lambda L: '\n'.join(L)
		  , partial(map, repoMasterXml)
		  , getRawPositionsFromFile
		)(file)


	with open('repoMaster_historical.xml', 'w') as outputFile:
		outputFile.write(getMasterXmlContent(file))




def repoTradeXml(position):
	"""
	[Dictionary] position (from XFIN file with repo name and collateral ticket#)
		=> [String] xml content for repo trade 
	"""
	toDateString = compose(
		lambda s: s + 'T00:00:00'
	  , lambda d: d.strftime('%Y-%m-%d')
	  , lambda s: datetime.strptime(s, '%m/%d/%y')
	  , lambda s: s.strip()
	)

	toStringIfFloat = lambda x: \
		str(int(x)) if isinstance(x, float) else x.strip()

	def getLocationAccount(broker):
		d = { 'SOCG-REPO': 'SocGen Repo'
			, 'HSBC-REPO': 'HSBC Repo'
			, 'BNP-REPO' : 'BNP Repo'
			, 'JPM-REPO' : 'JPM Repo'
			}
		return d.get(broker.strip(), 'CUS_REPO')


	if position['Tran Type'] != 'RR' or position['TermDt'] != 'OPEN' \
		or position['Day Count'] != 'ACT/360':
		print('invalid repo type: {0}'.format(position))
		raise ValueError

	keyValue = str(int(position['RT Ticket']))

	return \
	'<ReverseRepo_InsertUpdate>' + '\n' + \
	'<KeyValue KeyName="UserTranId1">{0}</KeyValue>'.format(keyValue) + '\n' + \
	'<UserTranId1>{0}</UserTranId1>'.format(keyValue) + '\n' + \
	'<Portfolio>{0}</Portfolio>'.format(toStringIfFloat(position['Account'])) + '\n' + \
	'<LocationAccount>{0}</LocationAccount>'.format(getLocationAccount(position['Broker'])) + '\n' + \
	'<Investment>Isin={0}</Investment>'.format(position['Identifier'].strip()) + '\n' + \
	'<EventDate>{0}</EventDate>'.format(toDateString(position['As Of Date'])) + '\n' + \
	'<SettleDate>{0}</SettleDate>'.format(toDateString(position['SetDt'])) + '\n' + \
	'<ActualSettleDate>CALC</ActualSettleDate>' + '\n' + \
	'<OpenEnded>CALC</OpenEnded>' + '\n' + \
	'<Quantity>{0}</Quantity>'.format(1000*position['Quantity']) + '\n' + \
	'<CounterInvestment>{0}</CounterInvestment>'.format(position['Curr'].strip()) + '\n' + \
	'<Price>99.99</Price>' + '\n' + \
	'<NetCounterAmount>{0}</NetCounterAmount>'.format(position['Money']) + '\n' + \
	'<RepoName>{0}</RepoName>'.format(position['Repo Name']) + '\n' + \
	'<Strategy>Default</Strategy>' + '\n' + \
	'<Coupon>{0}</Coupon>'.format(position['Rate']) + '\n' + \
	'<LoanAmount>{0}</LoanAmount>'.format(position['Money']) + '\n' + \
	'<Broker>{0}</Broker>'.format(position['Broker'].strip()) + '\n' + \
	'<AccrualDaysPerMonth>Actual</AccrualDaysPerMonth>' + '\n' + \
	'<AccrualDaysPerYear>360</AccrualDaysPerYear>' + '\n' + \
	'<FundStructure>CALC</FundStructure>' + '\n' + \
	'</ReverseRepo_InsertUpdate>'
# End of repoTradeXml()



def createRepoTradeXmlFile(file):
	"""
	[String] XFIN file with repo name and collateral ticket#
		=> [String] repo trade xml file (without headers)

	Side effect: write an XML file in the local directory.
	"""
	def getXmlContent(file):
		return \
		compose(
			lambda L: '\n'.join(L)
		  , partial(map, repoTradeXml)
		  , getRawPositionsFromFile
		)(file)


	with open('repoTrade_historical.xml', 'w') as outputFile:
		outputFile.write(getXmlContent(file))




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(description='Load historical report trades.')
	parser.add_argument('file')
	args = parser.parse_args()

	# write master ticket to collateral ticket mapping to csv
	# input is a THRP repo trade report.
	# 
	# writeCsv( 'repo_tickets.csv'
	# 		, chain( [('MRC Ticket', 'RT Ticket')]
	# 			   , loadTicketMapping(args.file)
	# 			   )
	# 		)


	# createRepoMasterXmlFile(args.file)
	createRepoTradeXmlFile(args.file)