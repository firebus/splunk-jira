"""
External search command for querying a JIRA instance. 

Usage:
  | jira "JQL query" | ... <other splunk commands here> ...

http://jira.example.com/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=<JQL>&tempMax=count&page/start=offset

Author: Stephen Sorkin
Author: Russell Uman
"""

import base64
import ConfigParser
import datetime
import lxml.etree as et
import os
import splunk.bundle as sb
import splunk.mining.dcutils as dcu
import splunk.Intersplunk as isp
import sys
import time
import urllib
import urllib2

results, dummyresults, settings = isp.getOrganizedResults()
messages = {}
logger = dcu.getLogger()

offset = 0
count = 100

try:
   namespace = settings.get("namespace", None)
   owner = settings.get("owner", None)
   sessionKey = settings.get("sessionKey", None)

   splunk_conf = sb.getConf('jira', namespace=namespace, owner=owner, sessionKey=sessionKey)
   stanza = splunk_conf.get('jira')

   keys = stanza.get('keys', '').split(',')
   time_keys = stanza.get('time_keys', '').split(',')
   custom_keys = stanza.get('custom_keys', '').split(',')

except Exception, e:
   logger.error(str(e))
   isp.addErrorMessage(messages, str(e))
   isp.outputResuts(results, messages)

try:
   local_conf = ConfigParser.ConfigParser()
   location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
   local_conf.read(location + '/config.ini')

   hostname = local_conf.get('jira', 'hostname')
   username = local_conf.get('jira', 'username')
   password = local_conf.get('jira', 'password')

except Exception, e:
   logger.error(str(e))
   isp.addErrorMessage(messages, str(e))
   isp.outputResuts(results, messages)

if len(sys.argv) > 1:
   jql = sys.argv[1]
else:
   jql = "project=%s" % stanza.get('default_project')

try:
   while True:
      query = urllib.urlencode({'jqlQuery':jql, 'tempMax':count, 'pager/start':offset})
      url = "https://%s/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?%s" % (hostname, query)
      request = urllib2.Request(url)
      logger.info(url)

      request.add_header('Authorization', "Basic %s" % base64.b64encode("%s:%s" % (username, password)))
      result = urllib2.urlopen(request)

      root = et.parse(result)

      results = []
      added_count = 0
      for elem in root.iter('item'):
         added_count = added_count + 1
         row = {}
         for k in keys:
            v = elem.xpath(k)
            if len(v) > 0:
               row[k] = ",".join([val.text for val in v])
         
         for k in time_keys:
            v = elem.xpath(k)
            if len(v) == 1:
               row[k] = v[0].get("seconds")

         for k in custom_keys:
            v = elem.xpath('customfields/customfield/customfieldvalues/customfieldvalue[../../customfieldname/text() = "%s"]' % k)
            if len(v) > 0:
               row[k] = ",".join([val.text for val in v])

            v = elem.xpath('customfields/customfield/customfieldvalues/label[../../customfieldname/text() = "%s"]' % k)
            if len(v) > 0:
               row[k] = ",".join([val.text for val in v])
         results.append(row)
         #print row

      if added_count > 0:
         isp.outputResults(results)
         offset = offset + added_count

      if added_count < count:
         break
except Exception, e:
   logger.error(str(e))
   isp.addErrorMessage(messages, str(e))
   isp.outputResuts(results, messages)