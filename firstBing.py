import urllib2
import base64

bingUrl = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%27gates%27&$top=10&$format=Atom'
#Provide your account key here
accountKey = 'JsV9AIVwzY0l654YiaIXAppMcpvpm7lvkcYdmzJrNcs'

accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
headers = {'Authorization': 'Basic ' + accountKeyEnc}
req = urllib2.Request(bingUrl, headers = headers)
response = urllib2.urlopen(req)
content = response.read()
#content contains the xml/json response from Bing. 
print content
