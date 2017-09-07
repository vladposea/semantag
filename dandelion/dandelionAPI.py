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
import time

#data: json response from dandelion.eu
#extract entities with the highest score
#return dict with key wikipedia url, value = list with highest score and label
def analyzeResponse(data):
	result={}
	#import pdb; pdb.set_trace()
#convert the string to a json object
	data=json.loads(data)
	if 'message' in data.keys():
		print data['message']
	for annotation in data['annotations']:
		uri=annotation['uri'].replace("http://en.wikipedia.org/wiki/", "http://dbpedia.org/resource/")
		spot=annotation['spot'].lower()
		if uri in result.keys():
			if annotation['confidence']>result[uri]['confidence']:
				result[uri]['confidence']=annotation['confidence']
			result[uri]['count']=result[uri]['count']+1
			if  spot not in result[uri]['spots']:
				result[uri]['spots'].append(spot)
		else:
			#import pdb; pdb.set_trace()
			result[uri]={}
			result[uri]['confidence']=annotation['confidence']
			result[uri]['label']=annotation['label']
			result[uri]['count']=1
			result[uri]['spots']=[spot]
	return result		


#makes request to dandelion with a given text, converts the result to a dictionary with the following structure:
# dbpediaURI:
#	confidence = maxconfidence from dandelion
#	spots = list of keywords to which the concept was annotated
# 	count = (deprecated) - number of spots
#	label = the label of the concept from dbpedia
def getEntities(text):
	params=urllib.urlencode({ 'token': '11d55d73877e4332be43deb194d05b80','lang':'en', 'text': text})
	url="https://api.dandelion.eu/datatxt/nex/v1"
	req=urllib2.Request(url, params)
	time.sleep(5)
	try:
		response=urllib2.urlopen(req)
	except Exception as e:
		print ("timeout")
		raise Exception()

	data=response.read()
	return analyzeResponse(data)


#returns a list containing the first percentage% of the concepts given by dandelion sorted by number of annotations and by confidence
#the resulted dict contains the following pairs key value
# concept_types: [list of types of the given concept]
#concept_name: name
#concept_uri: uri
#lexicalisations: [list of alternative terms for the given concept]
#relevance: number 
def getTopEntities(entDict,percentage):
	keys=sorted(entDict, key=lambda x: (entDict[x]['count'], entDict[x]['confidence']), reverse=True)
	topEnt=[]
	for i in range(len(keys)*percentage/100):
		#topEnt[keys[i]]=entDict[keys[i]]
		topEnt.append(
			{
			'concept_name': entDict[keys[i]]['label'],
			'concept_uri':keys[i], 
			'relevance': entDict[keys[i]]['confidence'], 
			'count': entDict[keys[i]]['count'], 
			'lexicalizations':entDict[keys[i]]['spots'], 
			'concept_types':[]
			}
			)
	return topEnt



#takes an article, sends it to dandelion, extracts the top 10% most relevant entities and stores the results in mongo
def saveEntities(uriArticle, text):
	client = pymongo.MongoClient(mongoURI)
	db=client.test
	
	articles=db.articles
	crtArticle=articles.find_one({'uri':uriArticle})
	
	if crtArticle==None:
		print uriArticle
		try:
			result=getTopEntities(getEntities(text), 10)
			crtArticle={
			'uri':uriArticle,
			'dandelion':{ 'concepts':result, 'category':'todo'}
		      }
		except Exception as e:
			crtArticle={'uri':uriArticle,'dandelion': {'error': repr(e)}}
         
		db.articles.insert_one(crtArticle)
	
	client.close()


#takes uri's from the mongodb and passes them to the saveentities function
def analyzeContent():
	client = pymongo.MongoClient(mongoURI)
	db=client.test
	contents=db.content
	for content in contents.find():
		if content['uri']=="https://www.eea.europa.eu/soer-2015/synthesis/report/4-resourceefficiency":
			continue #skip this one for now

		saveEntities(content['uri'], content['text'])
	client.close

analyzeContent()