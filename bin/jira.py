import urllib
import urllib2
import base64
import lxml.etree as et
import time
import datetime
import splunk.Intersplunk as isp
import sys

# http://jira.example.com/sr/jira.issueviews:searchrequest-xml/16483/SearchRequest-16483.xml?tempMax=1000
# http://jira.example.com/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?jqlQuery=project%3DExample&tempMax=1000

if len(sys.argv)>1:
    jql = sys.argv[1]
else:
    jql = 'project=Example'

keys = ['link', 'project', 'key', 'summary', 'type', 'priority', 'status', 'resolution', 'assignee', 'reporter', 'created', 
    'updated', 'resolved', 'fixVersion']
custom_keys = ['Sprint', 'Scrum', 'Story Points','Epic/Theme']
times = ['timeestimate', 'timeoriginalestimate', 'timespent']

# TODO: Get this from config
hostname = 'jira.example.com'
username = 'admin'
password = 'changeme'
count = 100
offset = 0

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
        #print results
        offset = offset + added_count

    if added_count < count:
        break