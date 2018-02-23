# Standard imports
import csv
import itertools
import os
import re
# Special imports
from lxml import etree
from lxml import objectify as ET
import json
import random

# --------------------------------------------------
# Node object
# A node has a label, a dict of attributes
class Node:
	def __init__(self, label, attributes, confidence=0.0):
		self.label = label
		self.attributes = attributes
		self.confidence = confidence

	def __repr__(self):
		rep = ''
		for key in self.attributes.keys():
			rep += '%s: %s\n' % (key, self.attributes[key])
		return rep

	def updateAttrs(self, attributes):
		for key in attributes:
			if key in self.attributes:
				self.attributes[key] = self.attributes[key] | attributes[key]

	def toDict(self, color=None):
		for key in self.attributes.keys():
			self.attributes[key] = list(self.attributes[key])
		myDict = {
			'id': self.label,
			'label': self.label,
			'x': random.randint(0, 500),
			'y': random.randint(0, 500),
			'size': len(self.attributes['Pubs']),
			#'email': self.attributes['Email'],
			'affil': self.attributes['Affiliation'],
			'attrs': self.attributes['Keywords'] + self.attributes['Collabs'] + self.attributes['Pubs'],
			#'attributes': self.attributes,
			#'confidence': self.confidence,
		}
		return myDict
# --------------------------------------------------

# --------------------------------------------------
# Edge object
# An edge has a source and destination
# Common describes the weight's content
class Edge:
	def __init__(self, id, source, target, common):
		self.id = id
		self.source = source
		self.target = target
		self.common = common
		w = 0
		for interest in common:
			w += len(common[interest])
		self.weight = w

	def toDict(self):
		myDict = {
			'id': self.id,
			'source': self.source.label,
			'target': self.target.label,
			#'attributes': list(self.common['Keywords']),
			#'weight': self.weight,
		}
		return myDict
# --------------------------------------------------

# --------------------------------------------------
# Analyzer object
# Contains main methods for reading, processing, and writing data
class Analyzer:
	def __init__(self):
		self.nodeList = []
		self.edgeList = []
		self.affilTable = {
				'concordia': 'Corcordia',
				'douglasmcgill': 'McGill',
				'etsmtl': 'ETS',
				'mtsmt1': 'McGill',
				'hec': 'HEC',
				'inrs': 'INRS',
				'mc-gill': 'McGill',
				'mcgi1l': 'McGill',
				'mcgifl': 'McGill',
				'mcgill': 'McGill',
				'mcgitl': 'McGill',
				'megill': 'McGill',
				'plymtl': 'Polytechnique',
				'qc': 'QC',
				'umnontreal': 'UdeM',
				'umoncton': 'UdeM',
				'umontreal': 'UdeM',
				'uqam': 'UQAM',
				'uquebec': 'UQAM',
				#'usherbrook': 'USherbrook',
		}

	def extractSetFromRow(self, row, fieldname, delimiter=';'):
		infoList = []
		content = row.get(fieldname, '').lower().split(delimiter)
		for info in content:
			info = info.strip()
			if len(info) > 0:
				infoList.append(info)
		return set(infoList)

	def checkMatch(self, listA, listB):
		for item in listA:
			if item in listB:
				return item
		return None

	def word2vec(self, word):
		from collections import Counter
		from math import sqrt
		# count the characters in word
		cw = Counter(word)
		# precomputes a set of the different characters
		sw = set(cw)
		# precomputes the "length" of the word vector
		lw = sqrt(sum(c * c for c in cw.values()))
		# return a tuple
		return cw, sw, lw

	def calcMaxSimilarity(self, item0, listOfItems):
		maxSimilarity = 0.5
		maxItem = None
		for itemN in listOfItems:
			v1 = self.word2vec(item0)
			v2 = self.word2vec(itemN)
			common = v1[1].intersection(v2[1])
			similarity = sum(v1[0][ch] * v2[0][ch] for ch in common) / v1[2] / v2[2]
			v1 = set(item0)
			v2 = set(itemN)
			common = v1.intersection(v2)
			similarity *= len(common)*1.0/min(len(v1), len(v2))

			if similarity > maxSimilarity:
				maxSimilarity = similarity
				maxItem = itemN
		return (maxItem, maxSimilarity)

	def readRawFile(self, filename):
		authorCount = 0

		with open('raw/%s' % filename, 'rb') as rawFile:
			print('Processing file: %s.' % filename)

			reader = csv.reader(rawFile, dialect='excel-tab')
			fieldnames = reader.next()
			csvDictReader = csv.DictReader(rawFile, fieldnames, restval='', dialect='excel-tab')
			csvDictReader.next()  # To skip the first line (header)

			for row in csvDictReader:

				AF = self.extractSetFromRow(row, 'AF')
				EM = self.extractSetFromRow(row, 'EM')
				TI = self.extractSetFromRow(row, 'TI')
				DE = self.extractSetFromRow(row, 'DE')
				ID = self.extractSetFromRow(row, 'ID')
				KW = DE.union(ID)

				for email in EM:
					emailParts = re.split('[@\.]', email)
					domain = self.checkMatch(emailParts, self.affilTable.keys())
					if not domain:
						EM = EM - {email}

				for email in EM:
					emailParts = re.split('[@\.]', email)
					domain = self.checkMatch(emailParts, self.affilTable.keys())
					name, conf = self.calcMaxSimilarity(email.split('@')[0], AF)
					if name:
						affiliation = self.affilTable[domain]
						collabs = AF.copy() - {name}
						attrs = {
							'Name': {name},
							'Email': {email},
							'Pubs': TI,
							'Collabs': collabs,
							'Keywords': KW,
							'Affiliation': {affiliation}
						}

						newNode = Node(name, attrs, conf)
						for node in self.nodeList:
							# Duplicate name/email (i.e. same person), update node to include new attributes
							if name in node.attributes['Name'] or email in node.attributes['Email']:
								newNode.updateAttrs(node.attributes)
								self.nodeList.remove(node)
								authorCount -= 1

						self.nodeList.append(newNode)
						authorCount += 1

	def findCommon(self, author1, author2):
		interests = ['Name',
		             'Email',
		             'Pubs',
		             'Collabs',
		             'Keywords',
		             ]
		disinterest = {'brain','expression','neurons','activation','human brain',
		               'performance','age','task','sleep','pet','images','system',
		               'disease','networks',
		               }
		commons = {}
		for interest in interests:
			setVal1 = author1.attributes.get(interest, {})
			setVal2 = author2.attributes.get(interest, {})
			intersection = setVal1 & setVal2 - disinterest

			if len(intersection) > 0:
				if interest == 'Name' or interest == 'Email':
					return True
				else:
					commons.update({interest:intersection})
		if len(commons.keys()) > 0:
			if len(commons.get('Keywords', [])) > 3:
				link = Edge(len(self.edgeList), author1, author2, commons)
				self.edgeList.append(link)
		return False

	def buildEdges(self):
		self.edgeList = []
		pairs = itertools.combinations(self.nodeList, 2)
		for (node1, node2) in pairs:
			if node1 and node2:
				hasDuplicate = self.findCommon(node1, node2)
				if hasDuplicate:
					print('Duplicate nodes found, rebuilding edges...\nNode1: %s\nNode2: %s\n' % (node1, node2))
					node1.updateAttrs(node2.attributes)
					self.nodeList.remove(node2)
					self.buildEdges()

	def writeJSON(self, filename):
		newNodeList = []
		newEdgeList = []
		discardList = []

		for node in self.nodeList:
			if len(node.attributes['Pubs']) > 5:
				newNodeList.append(node.toDict())
			else:
				discardList.append(node.label)
		print('Nodes: %d' % (len(newNodeList),))

		for edge in self.edgeList:
			if edge.weight < 5:
				pass
			elif edge.source.label in discardList or edge.target.label in discardList:
				pass
			else:
				newEdgeList.append(edge.toDict())
				if len(newEdgeList) % 3000 == 2999:
					print('Edges: %d' % (len(newEdgeList)))
		print('Edges: %d' % (len(newEdgeList),))

		with open('%s.json' % (filename,), 'wb') as jsonFile:
			jsonStr = json.dumps({
				'nodes': newNodeList,
				'edges': newEdgeList,
			})
			jsonFile.write(jsonStr)

	def writeGEXF(self, filename):
		gexfE = ET.Element('gexf', {'version':'1.3'})
		graphE = ET.SubElement(gexfE, 'graph', {
			'defaultedgetype': 'undirected',
			'idtype': 'string',
			'type': 'static'
		})

		attrsE = ET.SubElement(graphE, 'attributes', {'class': 'node', 'mode': 'static'})
		for attr in self.nodeList[0].attributes:
			ET.SubElement(attrsE, 'attribute', {
				'id': attr,
				'title': attr,
				'type': 'string'
			})

		nodesE = ET.SubElement(graphE, 'nodes', {
			'count': str(len(self.nodeList))
		})

		idCount = 0
		for node in self.nodeList:
			nodeE = ET.SubElement(nodesE, 'node', {
				'id': node.label,
				'label': node.label,
			})
			attvalues = ET.SubElement(nodeE, 'attvalues')
			for attr in node.attributes:
				ET.SubElement(attvalues, 'attvalue', {
					'for': attr,
					'value': ';'.join(node.attributes[attr]),
				})
			idCount += 1
		print('Total %d nodes' % idCount)

		edges = ET.SubElement(graphE, 'edges', {
			'count': str(len(self.edgeList))
		})

		idCount = 0
		for link in self.edgeList:
			edgeE = ET.SubElement(edges, 'edge', {
				'id': str(idCount),
				'source': link.source,
				'target': link.target,
				'weight': str(link.weight),
			})
			attvaluesE = ET.SubElement(edgeE, 'attvalues')
			for attr in link.common:
				ET.SubElement(attvaluesE, 'attvalue', {
					'for': attr,
					'value': ';'.join(link.common[attr]),
				})
			idCount += 1
		print('Total %d edges' % idCount)

		tree = etree.ElementTree(gexfE)
		tree.write(filename+'.gexf', encoding='utf-8', xml_declaration=True)

	def analyzeNodesEdges(self):
		profile = {}
		for edge in self.edgeList:
			try:
				for key in edge.common['Keywords']:
					profile.update({
						key: profile.get(key, 0) + 1
					})
			except:
				pass
		print('Interest profile:')
		for key, value in sorted(profile.iteritems(), key=lambda (k, v): (v, k)):
			print "%s: %s" % (key, value)
# --------------------------------------------------

def main():

	dir = 'raw'
	filenameList = os.listdir(dir)
	print('./%s has %d files' % (dir, len(filenameList)))

	myAnalyzer = Analyzer()

	for filename in filenameList:
		myAnalyzer.readRawFile(filename)
	print('%d nodes built.' % len(myAnalyzer.nodeList))

	myAnalyzer.buildEdges()
	print('%d edges built.' % len(myAnalyzer.edgeList))

	#myAnalyzer.analyzeNodesEdges()
	#myAnalyzer.writeGEXF('neural7')
	myAnalyzer.writeJSON('neural')


if __name__ == '__main__':
	main()

