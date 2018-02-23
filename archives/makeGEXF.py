import xml.etree.ElementTree as ET
import csv

def makeGEXF(authorList):
	gexf = ET.Element('gexf', {'defaultedgetype':'undirected', 'idtype':'string', 'type':'static'})
	attributes = ET.SubElement(gexf, 'attributes', {'class':'node', 'mode':'static'})
	ET.SubElement(attributes, 'attribute', {'id':'name', 'title':'Name', 'type':'string'})
	ET.SubElement(attributes, 'attribute', {'id':'email', 'title': 'Email', 'type': 'string'})
	ET.SubElement(attributes, 'attribute', {'id':'pubs', 'title': 'Publications', 'type': 'string'})

	nodes = ET.SubElement(gexf, 'nodes', {'count':len(authorList)})
	idCount = 0
	for author in authorList:
		node = ET.SubElement(nodes, 'node', {'id':idCount, 'label':author.get('name', 'None')})
		attvalues = ET.SubElement(node, 'attvalues')
		ET.SubElement(attvalues, 'attvalue', {'for':'name', 'value':author.get('name', 'None')})
		ET.SubElement(attvalues, 'attvalue', {'for':'email', 'value':author.get('email', 'None')})
		ET.SubElement(attvalues, 'attvalue', {'for':'pubs', 'value':author.get('title', 'None')})

	#ET.write('test.gexf')

def main():
	authorList = []
	with open('alldata.csv', 'rb') as readFile:
		rowReader = csv.reader(readFile)
		next(rowReader)
		for row in rowReader:
			author = {
				'name':row[0],
				'email':row[1],
				'title':row[2],
				'publication':row[3],
				'keywords':row[4],
				'keywords_plus':row[5],
				'funds':row[6]
			}
			authorList.append(author)

	makeGEXF(authorList)

if __name__ == '__main__':
	main()