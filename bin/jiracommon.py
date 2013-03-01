import ConfigParser
import os
import splunk.bundle as sb
import splunk.Intersplunk as isp

def getSplunkConf():
   results, dummyresults, settings = isp.getOrganizedResults()
   namespace = settings.get("namespace", None)
   owner = settings.get("owner", None)
   sessionKey = settings.get("sessionKey", None)

   conf = sb.getConf('jira', namespace=namespace, owner=owner, sessionKey=sessionKey)
   stanza = conf.get('jira')

   return stanza

def getLocalConf():
   local_conf = ConfigParser.ConfigParser()
   location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
   local_conf.read(location + '/config.ini')

   return local_conf