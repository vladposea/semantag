import httplib
import urllib
import test
import json
import urllib2
import pprint
import pymongo
import sys
sys.path.append('../')
from config import mongoURI

def getEntities(text):
	params=urllib.urlencode({ 'key': 'd26cca6be2130423e298841ccff27d42','lang':'en', 'txt': text, 'tt':'ec'})
	url = "http://api.meaningcloud.com/topics-2.0"
	req=urllib2.Request(url, params)
	response=urllib2.urlopen(req)
	data=response.read()
	data=json.loads(data)
	#pp=pprint.PrettyPrinter(indent=4)
	#pp.pprint(data)
	return data

#print getEntities(test.testString)
#getEntities(test.testString)

def detectTheme(theme_list, theme_name):
	for theme in theme_list:
		if theme_name in theme['type']:
			return theme['type']
	return None


def getTopEntities(data, percentage):
	i=0
	maxI=len(data['concept_list'])*percentage/100
	topEnt=[]
	for concept in data['concept_list']:
		i=i+1
		#print concept
		#print concept['sementity']['type']+ " "+ concept['form']+" "+concept['relevance']
		themes=[]
		
		if 'semtheme_list' in concept.keys():
			theme= detectTheme(concept['semtheme_list'], 'NaturalSciences')
			if theme is not None:
				themes.append(theme)
			else:
				i=i-1
				#a form of disambiguation - if i detect entities not related to naturalsciences it is most likely wrong
				continue #disregard the current concept identified

		
		if 'official_form' in concept.keys():
			form=concept['official_form']
		else:
			form=concept['form']
		
		lexicalizations=[]
		for term in concept['variant_list']:
			if term['form'] not in lexicalizations:
				lexicalizations.append(term['form'])

		
		if 'semld_list' in concept.keys():
			for possibleURI in concept['semld_list']:
				if possibleURI.find("en.wikipedia.org")!=-1 :
					themes.append(possibleURI.replace("http://en.wikipedia.org/wiki/", "http://dbpedia.org/resource/"))
					
				elif possibleURI.find("wikipedia.org")!=-1:
					continue
				else:
					themes.append(possibleURI) #we return the last uri in the semid_list
		
		uri=concept['sementity']['id']			

		topEnt.append(
			{
			'concept_name': form,
			'concept_uri':uri, 
			'relevance': concept['relevance'], 
			'count': len(concept['variant_list']), 
			'lexicalizations':lexicalizations, 
			'concept_types':themes,
			}
			)
		#a way to return the top percentage%
		if i==maxI:
			break
	return topEnt


#getTopEntities(test.result, 10)

def saveEntities(uriArticle, text):
	import pymongo
	client = pymongo.MongoClient(mongoURI)
	db=client.test
	articles=db.articles
	crtArticle=articles.find_one({'uri':uriArticle})
		
	try:
		result=getTopEntities(getEntities(text), 10)
		if crtArticle==None:
			#import pdb; pdb.set_trace()
			crtArticle={
			'uri':uriArticle,'meaningCloud':{ 'concepts':result, 'category':'todo'}

			}
			
			db.articles.insert_one(crtArticle)
		else:
			db.articles.update_one({'_id':crtArticle['_id']},{'$set':{'meaningCloud': { 'concepts':result, 'category':'todo'}}})
	except Exception as e:
		db.articles.update_one({'_id':crtArticle['_id']},{'$set':{'meaningCloud': { 'error': repr(e)}}})
	client.close()

#takes uri's from the mongodb and passes them to the saveentities function
def analyzeContent():
	client = pymongo.MongoClient(mongoURI)
	db=client.test
	contents=db.content
	for content in contents.find():
	
		saveEntities(content['uri'], content['text'])
	client.close

analyzeContent()