"""
External search command for querying the JIRA SOAP API 

Usage:
  | jirasoap search "text search" | ... <other splunk commands here> ... # text search
  | jirasoap jqlsearch "JQL query" | ... <other splunk commands here> ... # JQL search*
  | jirasoap issues <filter_id> | ... <other splunk commands here> ... # filter search
  | jirasoap filters | ... <other splunk commands here> ... # list all filters (to get ids for issues command)

* The jqlsearch doesn't handle '=' very well - splunk parses these as options.
Instead of saying "project = foo AND status = Open" say "project in (foo) AND status in (Open)".
Or use the SearchRequest XML command instead

Author: Fred de Boer
Author: Jeffrey Isenberg
Author: Russell Uman
"""

import splunk.Intersplunk as isp
import splunk.mining.dcutils as dcu

import jiracommon
import logging
import sys
import time

from suds.client import Client

try:
   messages = {}
   logging.getLogger('suds').setLevel(logging.INFO)

   logger = dcu.getLogger()

   # Get configuration values from config.ini
   local_conf = jiracommon.getLocalConf()

   hostname = local_conf.get('jira', 'hostname')
   username = local_conf.get('jira', 'username')
   password = local_conf.get('jira', 'password')
   protocol = local_conf.get('jira', 'soap_protocol');
   port = local_conf.get('jira', 'soap_port');

   url = "%s://%s:%s/rpc/soap/jirasoapservice-v2?wsdl" % (protocol, hostname, port)
   logger.info(url)
   client = Client(url)
   auth = client.service.login(username, password)

   keywords, argvals = isp.getKeywordsAndOptions()

   time_option = argvals.get('time', "now")

   logger.info('argv: ' + str(sys.argv))

   if sys.argv[1] == 'filters':
      filters =  client.service.getFavouriteFilters(auth)

      keys = (('author', None), ('id', None), ('name', None))

      results = []
      for filter in filters:
         row = jiracommon.flatten(filter, keys)
         logger.info(time.time())
         row['host'] = hostname
         row['source'] = "jira_soap"
         row['sourcetype'] = "jira_filters"
         row['_time'] = int(time.time())
         results.append(row)
      isp.outputResults(results)
      sys.exit(0)

   elif sys.argv[1] == 'issues':
      filter_id = sys.argv[-1]
      issues = client.service.getIssuesFromFilter(auth, filter_id)
   # TODO this 1000 issue max isn't working as expected - if there are more than 1000 results, no results are returned
   elif sys.argv[1] == 'search':
      search = sys.argv[-1]
      issues = (client.service.getIssuesFromTextSearch(auth, search, 1000) )
   elif sys.argv[1] == 'jqlsearch':
      jql = sys.argv[-1]
      issues = (client.service.getIssuesFromJqlSearch(auth, jql, 1000) )
   else:
      logger.fatal('invalid command')
      sys.exit(1)

   statuses = jiracommon.api_to_dict(client.service.getStatuses(auth))
   resolutions = jiracommon.api_to_dict(client.service.getResolutions(auth))
   priorities = jiracommon.api_to_dict(client.service.getPriorities(auth))

   resolutions[None] = 'UNRESOLVED'

   results = []

   keys = (('assignee', None),
          ('description', None),
          ('key', None),
          ('summary', None),
          ('reporter', None),
          ('status', statuses),
          ('resolution', resolutions),
          ('priority', priorities),
          ('project', None),
          ('type', None),
          ('created', None),
          ('updated', None))
   for issue in issues:
      row = jiracommon.flatten(issue, keys)

      # Special handling for multi-value fields
      affectedVersions = []
      for f in issue['affectsVersions']:
        affectedVersions.append(f['name'])
      row['affectedVersions'] = affectedVersions

      fixVersions = []
      for f in issue['fixVersions']:
         fixVersions.append(f['name'])
      row['fixVersions'] = fixVersions

      # Custom fields
      for f in issue['customFieldValues']:
         if f['customfieldId'] == "customfield_10020":
            row['SFDCcase'] = f['values']
         if f['customfieldId'] == "customfield_10091":
            row['TargetRelease'] = f['values']

      row['host'] = hostname
      row['source'] = 'jira_soap'
      row['sourcetype'] = "jira_issues"

      # override _time if time argument is set
      if time_option == "now":
         row['_time'] = int(time.time())
      else:
         row['_time'] = int(time.mktime(time.strptime(row[time_option], '%Y-%m-%d %H:%M:%S')))

      results.append(row)

   isp.outputResults(results)

except Exception, e:
   logger.exception(str(e))
   isp.generateErrorResults(str(e)) 