import config
from bs4 import BeautifulSoup
#parses the dump html file and stores the content in the mongo db

uriDump="alec-dump.htm"

def importfromDump(uriDump):	
	import pymongo
	client = pymongo.MongoClient(config.mongoURI)
	db=client.test
	content=db.content
	dumpFile=open(uriDump,"r")
	html_doc=dumpFile.read()
	soup = BeautifulSoup(html_doc, 'html.parser')
	i=0
	for element in soup.find_all("table")[0].tbody.contents:
		
		if element.name=="tr":
			#import pdb; pdb.set_trace()
			if element.contents[1].name=="th":
				continue
			try:	
			#extract the values
			#skip the russian content:)
				if element.contents[1].contents[0].find("eea.europa.eu/ru")!=-1:
					continue
				uri=element.contents[1].contents[0]
				print str(i) + " "+ uri+"\r\n"
				title=element.contents[3].contents[0]
				if len(element.contents[5].contents)>0:
					desc=element.contents[5].contents[0]
				else:
					desc=""
				text=repr(element.contents[7])
				keywords=element.contents[11].contents[0]
				themes=element.contents[13].contents[0]
				
				crtArticle=db.content.find_one({'uri':uri})
				if crtArticle==None:
					crtArticle={
					'uri':uri,'title':title, 'desc':desc, 'text':text, 'keywords':keywords, 'themes':themes 
					}
					try:
						db.content.insert_one(crtArticle)
						print str(i)+" success"
					except Exception as exmongo:
						print exmongo+" "+str(i)
				i=i+1		
			except Exception as e:
				print "Index error "+ str(i)+ " "+ uri
		else:
			#it is probably a \n
			continue

	client.close()
	dumpFile.close()

importfromDump(uriDump)
