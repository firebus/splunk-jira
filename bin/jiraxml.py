"""
External search command for querying the JIRA SearchRequest XML endpoint

Usage:
  | jira [time=TIME_OPTION JQL_QUERY | ... <other splunk commands here> ...

Author: Stephen Sorkin
Author: Russell Uman
"""

import base64
import datetime
import lxml.etree as et
import re
import sys
import time
import urllib
import urllib2

import jiracommon

import splunk.mining.dcutils as dcu
import splunk.Intersplunk as isp

try:
   messages = {}
   logger = dcu.getLogger()

   # Get configuration values from jira.conf
   splunk_conf = jiracommon.getSplunkConf()

   keys = splunk_conf.get('keys', '').split(',')
   time_keys = splunk_conf.get('time_keys', '').split(',')
   custom_keys = splunk_conf.get('custom_keys', '').split(',')

   offset = 0
   count = int(splunk_conf.get('tempMax', 1000))

   # Get configuration values from config.ini
   local_conf = jiracommon.getLocalConf()

   hostname = local_conf.get('jira', 'hostname')
   username = local_conf.get('jira', 'username')
   password = local_conf.get('jira', 'password')
   protocol = local_conf.get('jira', 'jira_protocol');
   port = local_conf.get('jira', 'jira_port');

   keywords, argvals = isp.getKeywordsAndOptions()
   logger.info('keywords: %s' % keywords)
   logger.info('argvals: %s' % argvals)
   logger.info('argv: %s' % sys.argv)

   # jql must be the last argument (but it's optional)
   if len(sys.argv) > 1:
      jql = sys.argv[-1]
   # default is to search for all issues in the default project
   else:
      jql = "project=%s" % splunk_conf.get('default_project')
   logger.info('jql: %s' % jql)

   time_option = argvals.get('time', "now")
   logger.info('time: %s' % time)

   results = []

   header = ['_time']
   for k in keys:
      header.append(k)
   for k in time_keys:
      header.append(k)
   for k in custom_keys:
      header.append(k)
   header.extend(['host', 'index', 'source', 'sourcetype', '_raw'])

   while True:
      query = urllib.urlencode({'jqlQuery':jql, 'tempMax':count, 'pager/start':offset})

      url = "%s://%s:%s/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml?%s" % (protocol, hostname, port, query)
      request = urllib2.Request(url)
      logger.info(url)

      request.add_header('Authorization', "Basic %s" % base64.b64encode("%s:%s" % (username, password)))
      result = urllib2.urlopen(request)

      root = et.parse(result)

      added_count = 0
      for elem in root.iter('item'):
         added_count = added_count + 1
         row = {}

         for k in keys:
            v = elem.xpath(k)
            if len(v) > 1:
               row[k] = [val.text for val in v]
               if '__mv_' + k not in header:
                  header.append('__mv_' + k)
            elif len(v) == 1:
               row[k] = v[0].text
         
         for k in time_keys:
            # If time_keys is empty, then the split above results in ['']
            if k:
               v = elem.xpath(k)
               if len(v) == 1:
                  row[k] = v[0].get("seconds")

         for k in custom_keys:
            # If custom_keys is empty, then the split above results in ['']
            if k:
               v = elem.xpath('customfields/customfield/customfieldvalues/customfieldvalue[../../customfieldname/text() = "%s"]' % k)
               if len(v) > 1:
                  row[k] = [val.text for val in v]
                  if '__mv_' + k not in header:
                     header.append('__mv_' + k)
               elif len(v) == 1:
                  row[k] = v[0].text

               v = elem.xpath('customfields/customfield/customfieldvalues/label[../../customfieldname/text() = "%s"]' % k)
               if len(v) > 1:
                  row[k] = [val.text for val in v]
                  if '__mv_' + k not in header:
                     header.append('__mv_' + k)
               elif len(v) == 1:
                  row[k] = v[0].text

         # override _time if time argument is set
         if time_option == "now":
            row['_time'] = int(time.time())
         elif time_option in keys:
            time_text = elem.findtext(time_option)
            if time_text != None:
               logger.info("time text: %s" % time_text)
               time_value = re.sub(r' (\+|-)\d+$', '', elem.findtext(time_option)) 
               timestamp = time.mktime(datetime.datetime.strptime(time_value, "%a, %d %b %Y %H:%M:%S").timetuple())
               row['_time'] = timestamp
            else: 
               row['_time'] = 0
         else: 
            row['_time'] = 0

         row['host'] = hostname
         row['index'] = 'jira'
         row['source'] = 'jql'
         row['sourcetype'] = 'jira_xml'
         #row['_raw'] = ', '.join("%s=%r" % (key,val) for (key,val) in row.iteritems())

         results.append(row)

      if added_count > 0:
         offset = offset + added_count

      if added_count < count:
         break

   isp.outputResults(results, None, header)
 
except Exception, e:
   logger.exception(str(e))
   isp.generateErrorResults(str(e))