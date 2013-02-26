"""
External search command for querying a JIRA instance. 

Usage:
  | jira "JQL query" | ... <other splunk commands here> ...

http://jira.example.com/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=<JQL>&tempMax=count&page/start=offset

Author: Stephen Sorkin
Author: Russell Uman
"""

import base64
import datetime
import lxml.etree as et
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

keys = ['link', 'project', 'key', 'summary', 'type', 'priority', 'status', 'resolution', 'assignee', 'reporter', 'created', 'updated', 'resolved', 'fixVersion']
times = ['timeestimate', 'timeoriginalestimate', 'timespent']
offset = 0

try:
   conf_file = 'jira'
   namespace = 'jira'
   owner = settings.get("owner", None)
   sessionKey = settings.get("sessionKey", None)
   stanza_name = 'jira'

   conf = sb.getConf(conf_file, namespace=namespace, owner=owner, sessionKey=sessionKey)
   stanza = conf.get(stanza_name)

except Exception, e:
   logger.error(str(e))
   isp.addErrorMessage(messages, str(e))
   isp.outputResuts(results, messages)

custom_keys = ['Sprint', 'Scrum', 'Story Points', 'Epic/Theme']
hostname = stanza.get('hostname')
username = stanza.get('username')
password = stanza.get('password')
count = stanza.get('count')

if len(sys.argv) > 1:
   jql = sys.argv[1]
else:
   jql = "project=%s" % stanza.get('default_project')

try:
   while True:
      query = urllib.urlencode({'jqlQuery':jql, 'tempMax':count, 'pager/start':offset})
      request = urllib2.Request("https://%s/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?%s" % (hostname, query))

      request.add_header('Authorization', "Basic %s" % base64.b64encode("%s:%s" % (username, password)))
      result = urllib2.urlopen(request)

      root = et.parse(result)

      results = []
      added_count = 0
      for elem in root.iter('item'):
         added_count = added_count + 1
         row = dict(map((lambda k: (k, elem.findtext(k))), keys))

         for k in times:
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
