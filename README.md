JIRA Add-on for Splunk
======================

This is a JIRA Add-on for Splunk.

* Download from http://www.gitub.com/firebus/splunk-jira
* Upgoat at http://apps.splunk.com/app/1438/

## Commands

### jirarest (REST API)

#### Syntax

```
| jirarest command options
```

#### Commands

* List all filters available to the logged-in user.
```
| jirarest filters
```

* Run a filter.
```
| jirarest issues FILTER_ID
```

* Run a JQL search and return Issues.
```
| jirarest jqlquery JQL_QUERY
```

* Run a JQL search and return the change history for all matching Issues.
```
| jirarest changelog JQL_QUERY
```

* List rapidboards (Greenhopper)
```
| jirarest rapidboards [list|all|RAPIDBOARD_ID]
```
  * list will list rapidboards.
  * all will list all sprints in all rapidboards.
  * RAPIDBOARD_ID will list all sprints in that rapidboard.
    * Hint: to get issues in a sprint use jqlquery "sprint=sprint_id" after you have found the desired sprint id here with rapidboards.

* Pipe search results into a jqlquery
```
| search ... | jirarest batch JQL_QUERY
```
  * The JQL_QUERY in the batch command is a partial query that ends with the IN keyword.
  * Results piped in from the preceding search will populate the IN clause.
  * Results piped in can be comma- or space- separated

#### Options

* comments 
  * Shows comments for all Issues returned by main option.
  * Compatible with issues,jqlquery, and batch commands.

* changefield
  * By default, pretty names for fields are show. Changefield outputs internal field names instead.
  * Compatible with issues, jqlquery and batch commands.

* changetime TIME_FIELD
   * Sets _time to the chosen field. If field does not contain a valid, returns 0 Epoch time
   * Compatible with issues, jqlquery, and batch commands.

#### Notes

* The rest command can also be called with | jira. 

### jirasoap (SOAP API - deprecated)

#### Syntax

```
| jirasoap command options

#### Commands

* List all filters available to the logged-in user
```
| jirasoap filters
```

* Run a filter
```
| jirasoap issues [time=TIME_OPTION] FILTER_ID
```

* Run a text search
```
| jirasoap search [time=TIME_OPTION] "foo bar bas"
```

* Run a JQL search
```
| jirasoap jqlsearch [time=TIME_OPTION] JQL_QUERY
```

#### Options

* time
    * *Syntax:* now | updated | created | resolved
    * *Description:* By default, _time is set to the current timestamp (now), but if you'd like to have _time reflect one of the native timefields on the issue, you can choose from updated, created, or resolved (if this field is empty, _time will be set to the unix epoch - January 1, 1970 00:00:00 GMT)

#### Notes

jirasoap is a 'generating' command that produces a results table. It does not create events. There is also a prototype retainsevents version called 'jirasoapevents' with the same syntax.
It creates real events instead of a table, but the events are empty so far...

### jiraxml (SearchRequest XML - deprecated)

#### Synopsis

Send a JQL query, return a table with one row for each result

#### Syntax

```
| jira [time=TIME_OPTION] [JQL_QUERY]
```

#### Arguments

* time
    * *Syntax:* now | updated | created | resolved
    * *Description:* By default, _time is set to the current timestamp (now), but if you'd like to have _time reflect one of the native timefields on the issue, you can choose from updated, created, or resolved (if this field is empty, _time will be set to the unix epoch - January 1, 1970 00:00:00 GMT)
* JQL_QUERY
    * If omitted, search for all Issues in the default project

#### Notes

jiraxml is a 'generating' command that produces a results table. It does not create events. There is also a prototype retainsevents version called 'jiraxmlevents' with the same syntax.
It creates real events instead of a table, but the events are empty so far...

## Deployment

1. Place the app into $SPLUNK_HOME/etc/apps/jira
2. Create a folder named local, copy default/jira.conf into local, and update with configuration specific to your instance.
3. Copy config.ini.sample to config.ini and update with your authentication credentials

Configure which keys to display in the table with the keys, time_keys, and custom_keys fields.

* Note that the SOAP API command ignores the key configuration.

## Acknowledgements

* We're redistributing suds 4.0 https://fedorahosted.org/suds/
* jiraxml command written by Stephen Sorkin and Jeffrey Isenberg
* jirasoap command written by Fred de Boer
* The Splunk MySQL app was used as a model, and lots of snippets here were stolen from its commands

## Support

Please open an issue on github if you have any trouble with the app, or contact the maintainer on apps.splunk.com 
Please feel free to fork and make pull requests if you find a bug that you can fix or have an enhancement to add.