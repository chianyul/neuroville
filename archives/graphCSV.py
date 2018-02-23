import csv
import itertools
import networkx
import matplotlib.pyplot as plt

def main():
	authorList = []
	with open('alldata.csv', 'rb') as readFile:
		rowReader = csv.reader(readFile)

		count = 0
		for row in rowReader:
			count = count + 1
			if count == 1:
				continue

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

			if count > 10:
				break

	myGraph = networkx.Graph()
	for author in authorList:
		myGraph.add_node(author['name'])

	#networkx.draw_circular(myGraph)
	fig1 = plt.figure()

	plt.show()


if __name__ == '__main__':
	main()

