import httplib
import urllib
import test
import json
import urllib2
import pprint
#data: json response from dandelion.eu
#extract entities with the highest score
#return dict with key wikipedia url, value = list with highest score and label
def analyzeResponse(data):
	result={}
	#import pdb; pdb.set_trace()
#convert the string to a json object
	data=json.loads(data)
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
	response=urllib2.urlopen(req)
	data=response.read()
	return analyzeResponse(data)

#todo: solve utf issues from the strings
#pp=pprint.PrettyPrinter(indent=4)
#pp.pprint(getEntities(test.testString))

#returns the dict containing the percentage% of the entities given by dandelion sorted by number of annotations and by confidence
def getTopEntities(entDict,percentage):
	keys=sorted(entDict, key=lambda x: (entDict[x]['count'], entDict[x]['confidence']), reverse=True)
	topEnt={}
	for i in range(len(keys)*percentage/100):
		topEnt[keys[i]]=entDict[keys[i]]
	return topEnt

pp=pprint.PrettyPrinter(indent=4)
pp.pprint(getTopEntities(getEntities(test.testString),10))
