import base64
import collections
import json
import re
import splunk.clilib.cli_common as spcli
import splunk.Intersplunk
import sys
import time
import urllib2
import urllib

import jiracommon

row={}
results=[]
keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

# Get configuration values from config.ini
local_conf = jiracommon.getLocalConf()

# Set up authentication variables
username = local_conf.get('jira', 'username')
password = local_conf.get('jira', 'password')
maxresults = local_conf.get('jira', 'maxresults')
maxresults = int(maxresults) if maxresults else 1000
auth = username + ':' + password
authencode = base64.b64encode(auth)

# Set up URL prefix
hostname = local_conf.get('jira', 'hostname')
protocol = local_conf.get('jira', 'jira_protocol')
port = local_conf.get('jira', 'jira_port')
jiraserver = protocol + '://' + hostname + ':' + port

pattern = '%Y-%m-%dT%H:%M:%S'
datepattern = "(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})"
datevalues = re.compile(datepattern)
option = sys.argv[1]

# filters
if option == 'filters':
   target = jiraserver + "/rest/api/2/filter/favourite?expand"
   reqf = urllib2.Request(target)
   reqf.add_header('Content-Type', 'application/json; charset=utf-8')
   reqf.add_header('Authorization', 'Basic '+authencode )
   filters = urllib2.urlopen(reqf)
   for filter in json.load(filters):
      row['name'] = filter['name']
      row['id'] = filter['id']
      row['owner'] = filter['owner']['name']
      row['owner_name'] = filter['owner']['displayName']
      row['search'] = filter['jql']
      row['url'] = filter['viewUrl']
      row['host'] = hostname
      row['source'] = "jira_rest"
      row['sourcetype'] = "jira_filters"
      row['_time'] = int(time.time())
      row['_raw'] = row
      results.append(row)
      row = {}
   splunk.Intersplunk.outputStreamResults(results)
   results = []
   exit()

# rapidboards
if option == 'rapidboards':
   args = sys.argv[2]
   if args == "all":
     target = jiraserver + "/rest/greenhopper/1.0/rapidviews/list"
   elif args == "list":
     target = jiraserver + "/rest/greenhopper/1.0/rapidview"
   elif "detail" in sys.argv:
     target = jiraserver + "/rest/greenhopper/1.0/xboard/work/allData/?rapidViewId=" + args
   else:
     target = jiraserver + "/rest/greenhopper/1.0/rapidview/" + args
   reqrb = urllib2.Request(target)
   reqrb.add_header('Content-Type', 'application/json; charset=utf-8')
   reqrb.add_header('Authorization', 'Basic '+authencode )
   rbopen = urllib2.urlopen(reqrb)
   rapidboards = json.load(rbopen)
   rbamv = []
   if args != "all":
     if args == "list":
       for view in rapidboards['views']:
        row['name'] = view['name']
        row['id'] = view['id']
        row['host'] = hostname
        row['source'] = "jira_rest"
        row['sourcetype'] = "jira_rapidboards"
        row['_time'] = int(time.time())
        row['_raw'] = row
        results.append(row)
        row = {}
       splunk.Intersplunk.outputStreamResults(results)
       results = []
       exit()
     if "detail" in sys.argv:
          columns = {}
          swimlanes = {}
          detailidx = sys.argv.index("detail")
          detailarg = sys.argv[detailidx+1]
          if detailarg == "issues":
            for sw in rapidboards['columnsData']['columns']:
               for j in sw['statusIds']:
                  columns[j]=sw['name']
            if "customSwimlanesData" in rapidboards['swimlanesData']:
               csw = True
               for wja in rapidboards['swimlanesData']['customSwimlanesData']['swimlanes']:
                 for i in wja['issueIds']:
                   swimlanes[i] = {"name":wja['name'], "query":wja['query']}
            else:
               csw = False
            for i in rapidboards['issuesData']['issues']:
                for j in i:
                  if "Statistic" in j:
                    field = i[j]['statFieldId']
                    if 'value' in i[j]['statFieldValue'].keys():
                      row[field] = str(i[j]['statFieldValue']['value'])
                    else:
                      row[field] = ''
                  else:
                    if "status" in j:
                       if j == "statusName":
                         row['status'] = i[j]
                       if j == "statusId":
                          try:
                            row['column'].append(columns[i[j]])
                          except:
                            row['column']=[]
                            row['column'].append(columns[i[j]])
                    elif "type" in j:
                       if j == "typeName":
                          row['type'] = i[j]
                    elif "priority" in j:
                       if j == "priorityName":
                          row['priority']=i[j]
                    elif j == "fixVersions":
                         for fv in i[j]:
                           try:
                              row['fixVersions'].append(str(fv))
                           except:
                               row['fixVersions'] = []
                               row['fixVersions'].append(str(fv))
                    elif j == "id":
                       if csw == True:
                         row['swimlane'] = swimlanes[i[j]]['name']
                         row['swimlane_query'] = swimlanes[i[j]]['query']
                       row['id'] = i[j]
                    else:
                      row[j] = str(i[j])
                row['rapidboard'] = rapidboards["rapidViewId"]
                row['source'] = option
                row['host'] = "JIRA"
                row['sourcetype'] = "jira_rapidboards"
                row['_time'] = int(time.time())
                row['_raw'] = row
                results.append(row)
                row = {}
            splunk.Intersplunk.outputStreamResults(results)
            results = []
            exit()
          elif detailarg == "sprints":
           for i in rapidboards["sprintsData"]["sprints"]:
                 for k in i:
                     if k == "remoteLinks":
                       for rl in i[k]:
                           if "url" in rl:
                            try:
                              row['remoteLinks'].append(str(rl['url']))
                            except:
                              row['remoteLinks']=[]
                              row['remoteLinks'].append(str(rl['url']))
                     else:
                        row[k] = i[k]
                 row['rapidboard'] = rapidboards["rapidViewId"]
                 row['host'] = hostname
                 row['source'] = "jira_rest"
                 row['sourcetype'] = "jira_rapidboads"
                 row['_time'] = int(time.time())
                 row['_raw'] = row

                 results.append(row)
                 row = {}
                 splunk.Intersplunk.outputStreamResults(results)
                 results = []
          exit()
     # rapidboard ID (no detail requested)
     target2 = jiraserver + "/rest/greenhopper/1.0/sprintquery/" + str(rapidboards['id']) + "?includeHistoricSprints=true&includeFutureSprints=true"
     reqsp = urllib2.Request(target2)
     reqsp.add_header('Content-Type', 'application/json; charset=utf-8')
     reqsp.add_header('Authorization', 'Basic ' + authencode )
     sprintopen = urllib2.urlopen(reqsp)
     sprints = json.load(sprintopen)
     for sprint in sprints['sprints']:
        row['name'] = rapidboards['name']
        row['id'] = rapidboards['id']
        row['sprint_id'] = sprint['id']
        row['sprint_name'] = sprint['name']
        row['sprint_state'] = sprint['state']
        row['host'] = hostname
        row['source'] = "jira_rest"
        row['sourcetype'] = "jira_sprints"
        row['_time'] = int(time.time())
        row['_raw'] = row
        results.append(row)
        row = {}
        splunk.Intersplunk.outputStreamResults(results)
        results = []
   # rapidboards all
   else:
     for view in rapidboards['views']:
      target2 = jiraserver + "/rest/greenhopper/1.0/sprintquery/" + str(view['id']) + "?includeHistoricSprints = true&includeFutureSprints=true"
      reqsp = urllib2.Request(target2)
      reqsp.add_header('Content-Type', 'application/json; charset=utf-8')
      reqsp.add_header('Authorization', 'Basic '+authencode )
      sprintopen = urllib2.urlopen(reqsp)
      sprints = json.load(sprintopen)
      for sprint in sprints['sprints']:
        row['sprint_id'] = sprint['id']
        row['sprint_name'] = sprint['name']
        row['sprint_state'] = sprint['state']
        row['_time'] = int(time.time())
        row['host'] = hostname
        row['source'] = "jira_rest"
        row['sourcetype'] = "jira_sprints"
        row['_time'] = int(time.time())
        row['_raw'] = row
        row['name'] = view['name']
        row['id'] = view['id']
        row['owner'] = view['filter']['owner']['userName']
        row['owner_name'] = view['filter']['owner']['displayName']
        row['filter_query'] = view['filter']['query']
        row['filter_name'] = view['filter']['name']
        row['filter_id'] = view['filter']['id']
        for admin in view['boardAdmins']['userKeys']:
           rbamv.append(admin['key'])
        row['boardAdmins'] = rbamv
        row['_time'] = int(time.time())
        row['_raw'] = row
        results.append(row)
        row = {}
        rbamv = []
      splunk.Intersplunk.outputStreamResults(results)
      results = []
   exit()

# changelog
if option == 'changelog':
   target = jiraserver + "/rest/api/2/search?jql="
   args=urllib.quote_plus(sys.argv[2]).split()
   querystring = '+'.join(args)
   clfieldmv = []
   clfrommv = []
   cltomv = []
   reqcl = urllib2.Request(target+querystring+"&fields=key,id,reporter,assignee,summary&maxResults=" + str(maxresults) + "&expand=changelog&validateQuery=false")
   reqcl.add_header('Content-Type', 'application/json; charset=utf-8')
   reqcl.add_header('Authorization', 'Basic '+authencode )
   clopen = urllib2.urlopen(reqcl)
   changelog = json.load(clopen)
   for issue in changelog['issues']:
      for field in issue['changelog']['histories']:
         for item in field['items']:
            row['created'] = field['created']
            row['user'] = field['author']['name']
            row['user_name'] = field['author']['displayName']
            row['field'] = item['field']
            row['from'] = item['fromString']
            row['to'] = item['toString']
            if datevalues.match(row['created']):
               jdate = datevalues.match(row['created']).group(1)
            epoch = int(time.mktime(time.strptime(jdate, pattern)))
            row['_time'] = epoch
            row['_raw'] = row
            row['host'] = hostname
            row['source'] = "jira_rest"
            row['sourcetype'] = "jira_changelog"
            row['key']=issue['key']
            if issue['fields']['reporter'] == None:
               row['reporter'] = None
               row['reporter_name'] = None
            else:
               row['reporter'] = issue['fields']['reporter']['name']
               row['reporter_name'] = issue['fields']['reporter']['displayName']
            if issue['fields']['assignee'] == None:
               row['assignee'] = None
               row['assignee_name'] = None
            else:
               row['assignee'] = issue['fields']['assignee']['name']
               row['assignee_name'] = issue['fields']['assignee']['displayName']
            row['summary'] = issue['fields']['summary']
            results.append(row)
            row = {}
         splunk.Intersplunk.outputStreamResults(results)
         results=[]
   exit()

# Since it wasn't filters, rapidboards, or changelog, it's either issues, jqlquery, or batch which share some options
if "changefield" in sys.argv[3:]:
   changefield = True
else:
   changefield = False

if "comments" in sys.argv[3:]:
   comments=True
else:
   comments=False

if "changetime" in sys.argv[3:]:
   timestamp=sys.argv[sys.argv.index("changetime")+1]
else:
   timestamp="created"

# TODO: Refactor 'fields' up here

def main(changefield,comments,timestamp):
   global issuecount
   try: 
      row = {}
      results = []
      fieldlist = {}
      flist = []
      fields = ""
      try: issuecount
      except: issuecount = 0  
      if issuecount >= maxresults:
         offset = "&startAt=" + str(issuecount)
      else:
         offset = ""

      # jqlsearch
      if option == 'jqlsearch':
         args=urllib.quote_plus(sys.argv[2]).split()
         if len(sys.argv) > 3 and "fields" in sys.argv[3:]:
            fields="&fields=key,id,created," + sys.argv[sys.argv.index('fields') + 1]
         target = jiraserver + "/rest/api/2/search?jql="
         querystring = '+'.join(args)
         if comments == True:
            req = urllib2.Request(target+querystring+"&maxResults=" + str(maxresults)  + "&fields=key"+offset+"&validateQuery=false")
         else:
            req = urllib2.Request(target+querystring+"&maxResults="+ str(maxresults) +fields+offset+"&validateQuery=false")

      # batch
      if option == 'batch':
         args = urllib.quote_plus(sys.argv[2]).split()
         batchargs = sys.argv[3]
         if len(sys.argv) > 4 and "fields" in sys.argv[4:]:
            fields = "&fields=key,id,created," + sys.argv[sys.argv.index('fields') + 1]
         batchargs = re.sub(',',' ',batchargs)
         batchargs = batchargs.split()
         batchargs = ','.join(batchargs)
         target = jiraserver + "/rest/api/2/search?jql="
         querystring = '+'.join(args) + "("+batchargs+")"
         if comments == True:
            req = urllib2.Request(target + querystring + "&maxResults=" + str(maxresults)  + "&fields=key" + offset + "&validateQuery=false")
         else:
            req = urllib2.Request(target + querystring + "&maxResults=" + str(maxresults)  + fields + offset + "&validateQuery=false")

      # issues
      if option == 'issues':
         args=sys.argv[2]
         if len(sys.argv) > 3 and "fields" in sys.argv[3:]:
            fields = "&fields=key,id,created," + sys.argv[sys.argv.index('fields') + 1]
         target = jiraserver + "/rest/api/2/search?jql=filter=" + args
         if comments == True:
            req = urllib2.Request(target + "&maxResults=" + str(maxresults) +"&fields=key" + offset + "&validateQuery=false")
         else:
            req = urllib2.Request(target + "&maxResults=" + str(maxresults) + fields + offset + "&validateQuery=false")

      fieldtarget = jiraserver + "/rest/api/2/field"
      fieldreq = urllib2.Request(fieldtarget)
      req.add_header('Content-Type', 'application/json; charset=utf-8')
      fieldreq.add_header('Content-Type', 'application/json; charset=utf-8')
      req.add_header('Authorization', 'Basic ' + authencode )
      fieldreq.add_header('Authorization', 'Basic ' + authencode )
      fields = urllib2.urlopen(fieldreq)
      handle = urllib2.urlopen(req)
      fullfields = json.load(fields)
      full2 = json.load(handle)

      # comments
      if comments == True:
         for issue in full2['issues']:
            commenttarget = jiraserver + "/rest/api/2/issue/" + issue['key'] + "/comment"
            reqc = urllib2.Request(commenttarget)
            reqc.add_header('Content-Type', 'application/json; charset=utf-8')
            reqc.add_header('Authorization', 'Basic '+authencode )
            commentf = urllib2.urlopen(reqc)
            commentfull = json.load(commentf)['comments']
            for comment in commentfull:
               for author in comment:
                  if author == "author" or author == "updateAuthor":
                     row[author] = comment[author]['name']
                     row[author + "_name"] = comment[author]['displayName']
               row['created'] = comment['created']
               row['updated'] = comment['updated']
               row['comment'] = comment['body']
               if changefield == True:
                  row['key'] = issue['key']
               else:
                  row['Key'] = issue['key']
               if row[timestamp] != None:
                  if datevalues.match(row[timestamp]):
                     jdate = datevalues.match(row[timestamp]).group(1)
                     epoch = int(time.mktime(time.strptime(jdate, pattern)))
               else:
                  epoch = 0
               row['_time'] = epoch
               row['_raw'] = row
               row['host'] = hostname
               row['source'] = "jira_rest"
               row['sourcetype'] = "jira_comments"
               results.append(row)
               row={}
            splunk.Intersplunk.outputStreamResults(results)
            results=[]
         exit() 
      for fielditem in fullfields:
         fieldlist[fielditem['id']] = fielditem['name']
         flist.append(fieldlist)
      for issue in full2['issues']:
         for jirafield in issue['fields']:
            if changefield == True:
               field = jirafield
            else:
               if jirafield in fieldlist:
                  field = fieldlist[jirafield]
               else:
                  field = jirafield
            if issue['fields'][jirafield] == None:
               row[field] = None
            elif (isinstance(issue['fields'][jirafield], basestring) == True):
               row[field] = issue['fields'][jirafield]
            elif (isinstance(issue['fields'][jirafield], collections.Iterable) == True):
               if jirafield=='labels':
                  row[field]=issue['fields'][jirafield]
               for mvfield1 in issue['fields'][jirafield]:
                  if (isinstance(mvfield1, basestring) == True) and jirafield != 'labels':
                     if mvfield1 == 'name' or mvfield1 == 'value' or mvfield1 == 'displayName':
                        if mvfield1 == 'displayName':
                           row[field + "_" + "Name"] = issue['fields'][jirafield][mvfield1]
                        else:
                           row[field] = issue['fields'][jirafield][mvfield1]
                     elif mvfield1=='total' :
                        row[field+"_total"]=issue['fields'][jirafield][mvfield1]
                     elif mvfield1=='progress' :
                        row[field+"_progress"]=issue['fields'][jirafield][mvfield1]
                  elif (isinstance(mvfield1, collections.Iterable) == True and jirafield != 'labels'):
                     for mvfield2 in mvfield1: 
                        if mvfield2=='key':
                           try:
                              row[field].append(mvfield1[mvfield2])
                           except:
                              row[field]=[]
                              row[field].append(mvfield1[mvfield2])
                        if (isinstance(mvfield1[mvfield2], basestring)==True):
                           if mvfield2=='name' or mvfield2=='value' or mvfield2=='displayName':
                              try:
                                 row[field].append(mvfield1[mvfield2])
                              except:
                                 row[field]=[]
                                 row[field].append(mvfield1[mvfield2])
                        else:
                           if (isinstance(mvfield1[mvfield2], collections.Iterable)==True):
                              for mvfield3 in mvfield1[mvfield2]:
                                 if jirafield=="issuelinks":
                                    if mvfield3=='key':
                                       try:
                                          row[field].append(mvfield1[mvfield2][mvfield3])
                                       except:
                                          row[field]=[]
                                          row[field].append(mvfield1[mvfield2][mvfield3])
                                       if mvfield2=="inwardIssue":
                                          try:
                                             row[field+'_type'].append(mvfield1['type']['inward']+"-"+mvfield1[mvfield2][mvfield3])
                                          except:
                                             row[field+'_type']=[]
                                             row[field+'_type'].append(mvfield1['type']['inward']+"-"+mvfield1[mvfield2][mvfield3])
                                       if mvfield2=="outwardIssue":
                                          try:
                                             row[field+'_type'].append(mvfield1['type']['outward']+"-"+mvfield1[mvfield2][mvfield3])
                                          except:
                                             row[field+'_type']=[]
                                             row[field+'_type'].append(mvfield1['type']['outward']+"-"+mvfield1[mvfield2][mvfield3])
                                       if 'summary' in mvfield1[mvfield2]['fields']:
                                          try:
                                             row[field+'_summary'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['summary'])
                                          except:
                                             row[field+'_summary']=[]
                                             row[field+'_summary'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['summary'])
                                       if 'status' in mvfield1[mvfield2]['fields']:
                                          try:
                                             row[field+'_status'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['status']['name'])
                                          except:
                                             row[field+'_status']=[]
                                             row[field+'_status'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['status']['name'])
                                       if 'priority' in mvfield1[mvfield2]['fields']:
                                          try:
                                             row[field+'_priority'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['priority']['name'])
                                          except:
                                             row[field+'_priority']=[]
                                             row[field+'_priority'].append(mvfield1[mvfield2][mvfield3]+"-"+mvfield1[mvfield2]['fields']['priority']['name'])
                              if 'summary' in mvfield1[mvfield2]:
                                 try:
                                    row[field+'_summary'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['summary'])
                                 except:
                                    row[field+'_summary']=[]
                                    row[field+'_summary'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['summary'])
                              if 'status' in mvfield1[mvfield2]:
                                 try:
                                    row[field+'_status'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['status']['name'])
                                 except:
                                    row[field+'_status']=[]
                                    row[field+'_status'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['status']['name'])
                              if 'priority' in mvfield1[mvfield2]:
                                 try:
                                    row[field+'_priority'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['priority']['name'])
                                 except:
                                    row[field+'_priority']=[]
                                    row[field+'_priority'].append(mvfield1['key']+"-"+mvfield1[mvfield2]['priority']['name'])
                  else:
                    if jirafield != 'labels':
                       row[field] = issue['fields'][jirafield][mvfield1]
            else:
               if jirafield != 'labels':
                  row[field] = str(issue['fields'][jirafield])

         if changefield != True:
            if row[fieldlist[timestamp]] != None:
               if datevalues.match(row[fieldlist[timestamp]]):
                  jdate = datevalues.match(row[fieldlist[timestamp]]).group(1)
                  epoch = int(time.mktime(time.strptime(jdate, pattern)))
            else:
               epoch = 0
         else:
            if row[timestamp] != None:
               if datevalues.match(row[timestamp]):
                  jdate = datevalues.match(row[timestamp]).group(1)
                  epoch = int(time.mktime(time.strptime(jdate, pattern)))
            else:
               epoch = 0

         if changefield == True: 
            row['key'] = issue['key']
         else:
            row['Key'] = issue['key']
         row['_time'] = epoch
         row['_raw'] = row
         row['host'] = hostname
         row['source'] = "jira_rest"
         row['sourcetype'] = "jira_issues"
         results.append(row)     
         row = {}
      splunk.Intersplunk.outputStreamResults(results)
      results = []
      issuecount = issuecount + len(full2['issues'])
      if int(len(full2['issues'])) >= maxresults:
         main(changefield, comments, timestamp)       
      else:
         exit()

   except Exception, e:
      import traceback
      results = []
      row = {}
      stack =  traceback.format_exc()
      row['_time'] = int(time.time())
      row['error'] = str(str(e))
      row['host'] = hostname
      row['search'] = " " . join(args)
      row['source'] = "jira_rest"
      row['sourcetype'] = 'jira_exception'
      results.append(row)
      splunk.Intersplunk.outputStreamResults(results)

main(changefield, comments, timestamp)