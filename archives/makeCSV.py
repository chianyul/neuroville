'''
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/10501-11000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/11001-11500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/11501-12000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/12001-12500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/12501-13000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/13001-13500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/13501-14000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/14001-14500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/14501-15000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/15001-15500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/15501-16000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/16001-16500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/16501-17000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/17001-17500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/17501-18000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/18001-18500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/18501-19000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/19001-19500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/19501-20000.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/20001-20500.txt" --headerline
mongoimport.exe -d neurobrainmtl -c alldata --type tsv --file "C:/Users/Farivar Lab/Documents/Chianyu/neurobrainmtl/20501-20890.txt" --headerline
'''
import pymongo
import re
import csv
import itertools

def similar(a, b):
	awords = a.split(' ')
	awordset = set(awords)
	bwords = b.split(' ')
	bwordset = set(bwords)
	overlap = awordset.intersection(bwordset)
	
	ratio = (len(overlap)*2.0) / (len(awordset)+len(bwordset))

	return ratio

def main():
	client = pymongo.MongoClient()
	db = client.neurobrainmtl

	cursor = db.alldata.find({}, {'AF':1, 'EM':1, 'TI':1, 'SO':1, 'DE':1, 'ID':1, 'FU':1, '_id':0})

	file = open('alldata.csv', 'wb')
	csvwriter = csv.writer(file)
	csvwriter.writerow(['Author','Email', 'Title', 'Publication', 'Keywords', 'Keywords Plus', 'Funds'])

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

	authors = []
	emails = []
	funds = []
	count = 0
	for doc in cursor:
		af = doc['AF'].split('; ')
		em = doc['EM'].split('; ')
		ti = doc['TI']
		so = doc['SO']
		de = doc['DE'].split('; ')
		id = doc['ID'].split('; ')
		fu = doc['FU'].split('; ')

		if len(af) > 0:
			if len(af) == len(em):
				for a, e in zip(af, em):
					emailList = re.split('[@\.]', e)
					if any(map(lambda domain: domain in domainList, emailList)):
						csvwriter.writerow([a, e, ti, so, ';'.join(de), ';'.join(id), ';'.join(fu)])		
						authors.append(a)
						emails.append(e)
						count += 1
			else:
				for name in af:
					nameList = name.lower().split(', ')
					for email in em:
						emailList = re.split('[@\.]', email.lower())
						if any(map(lambda domain: domain in domainList, emailList)):
							if any(map(lambda prefix: prefix in nameList, emailList)):
								csvwriter.writerow([name, email, ti, so, ';'.join(de), ';'.join(id), ';'.join(fu)])		
								authors.append(name)
								emails.append(email)
								count += 1


	print('Total records: %d\n' % count)

if __name__ == '__main__':
	main()
'''
count = 0
funds = funds.sort()
funds = set(funds)
existing = []
import itertools
for a, b in itertools.combinations(funds, 2):
	if a not in existing:
		similarity = similar(a, b)
		if similarity > 0.50:
			existing.append(a)
			existing.append(b)
		else:
			existing.append(a)
		print(a)
		count += 1

print('Total records: %d\n' % count)

print('\nSchools:')
domains = []
for email in emails:
	e = re.split('@|\.', email)
	index = len(e)

	domain = (e[index-2]+'.'+e[index-1]).lower()
	domains.append(domain)

domainset = set(domains)
domainlist = list(domainset)
domainlist.sort()

print('\n'.join(domainlist))
'''
