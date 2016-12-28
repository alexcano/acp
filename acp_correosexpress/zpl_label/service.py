import urllib
import urllib2

class ZPLlabel(object):
    
    def __init__(self):    
        self.url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
            
    def connect(self, data):
                
        url = self.url
        
        headers = { 'Accept' : 'application/pdf' }
        
        req = urllib2.Request(url, data ,headers)
        print req
        response = urllib2.urlopen(req)
        label = response.read()        
        return label                        
        
 
                    

