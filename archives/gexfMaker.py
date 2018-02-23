import csv
import os
import re
import itertools
import xml.etree.ElementTree as ET

domainList = [
	'concordia',
	'douglasmcgill',
	'etsmtl', 'mtsmt1',
	'hec',
	'inrs',
	'mc-gill', 'mcgi1l', 'mcgifl', 'mcgill', 'mcgitl', 'megill',
	'plymtl',
	'qc.ca',
	'umnontreal',
	'umoncton',
	'umontreal',
	'uqam',
	'uquebec',
	'usherbrook'
]

def extractFieldToSet(row, fieldname):
	infoList = []

	content = row.get(fieldname, '').lower().split(';')
	for c in content:
		c = c.strip()
		if len(c) > 0:
			infoList.append(c)

	return set(infoList)

def readRawFiles(filenames):
	authorDict = {}
	count = 0
	for file in filenames:
		with open('raw/%s' % file, 'rb') as textFile:
			print('Processing file: %s...' % (file,))

			reader = csv.reader(textFile, dialect='excel-tab')
			fieldnames = reader.next()

			csvDictReader = csv.DictReader(textFile, fieldnames, restval='', dialect='excel-tab')
			csvDictReader.next()  # To skip the first line (header)

			for row in csvDictReader:

				AF = extractFieldToSet(row, 'AF')
				EM = extractFieldToSet(row, 'EM')
				TI = extractFieldToSet(row, 'TI')
				DE = extractFieldToSet(row, 'DE')
				ID = extractFieldToSet(row, 'ID')
				KW = DE.union(ID)

				for name in AF:
					for email in EM:
						nameParts = name.split(', ')
						emailParts = re.split('[@\.]', email)
						if any(map(lambda domain: domain in domainList, emailParts)):
							if any(map(lambda prefix: prefix in nameParts, emailParts)):
								index = len(emailParts)
								affiliation = (emailParts[index-2]).lower()
								collabs = AF.copy() - {name}
								if authorDict.has_key(name):
									# Author already exists
									authorDict.update({
										name: {
											'author': name,
											'email':authorDict[name].get('email').union({email}),
											'collabs':authorDict[name].get('collabs').union(collabs),
											'publications':authorDict[name].get('publications').union(TI),
											'keywords':authorDict[name].get('keywords').union(KW),
											'affiliation':authorDict[name].get('affiliation').union({affiliation}),
										}
									})
								else:
									# New author
									authorDict.update({
										name:{
											'author': name,
											'email': {email},
											'collabs': collabs,
											'publications': TI,
											'keywords': KW,
											'affiliation': {affiliation},
										}
									})
								count += 1
			print('Done.')
	return authorDict

def writeAllData(filename, authorDict):
	with open(filename, 'wb') as csvFile:

		focus = ['author', 'email', 'collabs', 'publications', 'keywords',]
		csvDictWriter = csv.DictWriter(csvFile, focus, restval='')
		csvDictWriter.writeheader()

		for authorname in authorDict:
			author = authorDict[authorname]
			csvDictWriter.writerow({
				'author': author.get('author', ''),
				'email': ';'.join(author.get('email', {})),
				'collabs': ';'.join(author.get('collabs', {})),
				'publications': ';'.join(author.get('publications', {})),
				'keywords': ';'.join(author.get('keywords', {})),
				'affiliation': ';'.join(author.get('affiliation', {})),
			})

def readAllData(authorDict):
	gexf = ET.Element('gexf')

	graph = ET.SubElement(gexf, 'graph', {
		'defaultedgetype':'undirected',
		'idtype':'string',
		'type':'static'
	})

	attrs = ET.SubElement(graph, 'attributes', {'class':'node', 'mode':'static'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'name',
		'title': 'Name',
		'type': 'string'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'email',
		'title': 'Email',
		'type': 'string'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'collabs',
		'title': 'Collabs',
		'type': 'string'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'publications',
		'title': 'Publications',
		'type': 'string'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'keywords',
		'title': 'Keywords',
		'type': 'string'})
	ET.SubElement(attrs, 'attribute', {
		'id': 'affiliation',
		'title': 'Affiliation',
		'type': 'string'})
	nodes = ET.SubElement(graph, 'nodes', {
		'count': str(len(authorDict))
	})

	idCount = 0
	for name in authorDict:
		author = authorDict[name]
		node = ET.SubElement(nodes, 'node', {
			'id': author.get('author', 'None'),
			'label':author.get('author', 'None')
		})
		attvalues = ET.SubElement(node, 'attvalues')
		ET.SubElement(attvalues, 'attvalue', {
			'for': 'name',
			'value': author.get('author', 'None')})
		ET.SubElement(attvalues, 'attvalue', {
			'for':'email',
			'value':';'.join(author.get('email'))})
		ET.SubElement(attvalues, 'attvalue', {
			'for':'collabs',
			'value':';'.join(author.get('collabs'))})
		ET.SubElement(attvalues, 'attvalue', {
			'for':'publications',
			'value':';'.join(author.get('publications'))})
		ET.SubElement(attvalues, 'attvalue', {
			'for':'keywords',
			'value':';'.join(author.get('keywords'))})
		ET.SubElement(attvalues, 'attvalue', {
			'for':'affiliation',
			'value': ';'.join(author.get('affiliation'))})
		idCount += 1
	print('Total %d nodes' % idCount)

	with open('edges.csv', 'rb') as edgeFile:
		fieldnames = ['author1','author2','commons']
		csvDictReader = csv.DictReader(edgeFile, fieldnames)
		csvDictReader.next()
		edges = ET.SubElement(graph, 'edges')
		idCount = 0
		for row in csvDictReader:
			ET.SubElement(edges, 'edge', {
				'id': str(idCount),
				'source': row['author1'],
				'target': row['author2'],
				'weight': str(len(row['commons'].split(';')))
			})
			idCount += 1
		print('Total %d edges' % idCount)

	tree = ET.ElementTree(gexf)
	tree.write('neural2.gexf', encoding='utf-8', xml_declaration=True)


def analyzeAllData(authorDict):
	checklist = ['email', 'collabs', 'keywords', 'publications',]

	edgeList = []

	pairs = itertools.combinations(authorDict, 2)
	for (name1, name2) in pairs:
		author1 = authorDict.get(name1)
		author2 = authorDict.get(name2)
		commons = []
		for key in checklist:
			valSet1 = set(author1[key])
			valSet2 = set(author2[key])
			intersection = valSet1 & valSet2
			if len(intersection) > 0:
				commons.extend(intersection)
		if len(commons) > 0:
			edge = {
				'author1': author1.get('author', ''),
				'author2': author2.get('author', ''),
				'commons': ';'.join(commons)
			}
			edgeList.append(edge)

	print('%d edges found, writing to file...' % len(edgeList))
	with open('edges.csv', 'wb') as csvFile:
		fieldnames = ['author1', 'author2', 'commons']
		csvDictWriter = csv.DictWriter(csvFile, fieldnames=fieldnames)
		csvDictWriter.writeheader()
		for edge in edgeList:
			csvDictWriter.writerow(edge)
	print('Done.')

def main():
	dir = 'raw'
	files = os.listdir(dir)
	print('./%s has %d files' % (dir, len(files)))

	authorDict = readRawFiles(files)
	print('%d data extracted' % len(authorDict))
	#allDataFileName = 'alldatax.csv'
	#writeAllData(allDataFileName, authorDict)
	analyzeAllData(authorDict)
	readAllData(authorDict)


if __name__ == '__main__':
	main()