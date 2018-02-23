import json
import urllib2

def main():

	eSearch = urllib2.urlopen('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&retmode=json&retmax=100000&term=((neur*)+OR+brain)+AND+Montreal')
	eSearchJSON = eSearch.read()
	eSearchData = json.loads(eSearchJSON)
	
	idList = eSearchData['esearchresult']['idlist']
	chunks = [idList[x:x+50] for x in xrange(0, len(idList), 50)]

	eSummaryUrlList = []
	eSummaryPrefix = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&retmode=xml&id='
	
	for chunk in chunks:
		url = eSummaryPrefix + ','.join(chunk)
		eSummaryUrlList.append(url)

	eSummary = urllib2.urlopen(eSummaryUrlList[0])
	eSummaryJSON = eSummary.read()
	
	print(eSummary)
	'''
	eSummaryData = {}
	for url in eSummaryUrlList:
		eSummary = urllib2.urlopen(url)
		eSummaryJSON = eSummary.read()
		eSummaryData = json.loads(eSummaryJSON)
	'''



	#print(eSummaryUrlList[0])





if __name__ == '__main__':
	main()