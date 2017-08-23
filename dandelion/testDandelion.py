import httplib
import urllib
import test
import socket
socket.ssl


conn=httplib.HTTPSConnection("api.dandelion.eu")
params=urllib.urlencode({ 'token': '11d55d73877e4332be43deb194d05b80','lang':'en', 'text': test.testString})
conn.request("GET","/datatxt/nex/v1?"+params)
#import pdb; pdb.set_trace()
response=conn.getresponse()
data=response.read()
print data
