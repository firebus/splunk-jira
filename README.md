Add-on for JIRA
======================

This is an Add-on for JIRA.

* Download from https://www.github.com/firebus/splunk-jira
* Upgoat at http://apps.splunk.com/app/1438/

## Commands

### jirarest (REST API)

#### Syntax

```
| jirarest MODE OPTIONS
```

#### Modes

* List favorite filters of the configured user

  ```
  | jirarest filters
  ```

* Run a specific filter and return Issues

  ```
  | jirarest issues FILTER_ID
  ```

* Run a JQL search and return Issues.

  ```
  | jirarest jqlsearch JQL_QUERY
  ```

* Run a JQL search and return the all Changes for all matching Issues.
  
  ```
  | jirarest changelog JQL_QUERY
  ```

* List rapidboards or sprints (Greenhopper REST API)

  ```
  | jirarest rapidboards list|all|(RAPIDBOARD_ID [detail sprints|issues])
  ```

  * list will list all scrum boards. This is the default behavior.
  * all will list all sprints in all scrum boards.
  * RAPIDBOARD_ID will list all sprints in one specific scrum board.
    * "detail sprints" gives details on the active sprints in the rapidboard.
    * "detail issues" gives details on the active issues in the board including swimlanes and groupings.
    * Hint: to get issues in a sprint use jqlquery "sprint=sprint_id" after you have found the desired sprint id here with rapidboards.

* Pipe search results into a jqlsearch

  ```
  | search ... | eval foo="WTF-1,WTF-2,WTF-3" | makemv delim=, foo | map search="|jirarest batch JQL_QUERY $foo$"
  ```

  * The JQL_QUERY in the batch command is a partial query that ends with the IN keyword, e.g. "key in"
  * Results piped in from the preceding search will populate the IN clause.
  * Results piped in can be comma- or space- separated
  * This is a little ungainly, but quite powerful if you want to pull a list of JIRA keys from an external source and then get all the Issues from JIRA

#### Options

* comments 
  * Shows comments for all Issues returned by main option.
  * Compatible with issues, jqlquery, and batch commands.

* changefield
  * By default, pretty names for fields are show. Changefield outputs internal field names instead.
  * Compatible with issues, jqlquery and batch commands.

* changetime TIME_FIELD
   * Sets _time to the chosen field. If field does not contain a valid, returns 0 Epoch time
   * _time defaults to created if changetime is not set
   * Compatible with issues, jqlquery, and batch commands.

* fields "[INTERNAL_FIELD_NAME,...]"
   * Limits the set of fields returned
   * Takes a comma-separated list of internal field names. No extra spaces, we're too lazy to trim
   * If you want multiple fields, please enclose the field list in double-quotes
   * key and created are always returned

#### Notes

* The rest command can also be called with | jira. 

### jirasoap (SOAP API - deprecated)

#### Syntax

```
| jirasoap MODE OPTIONS
```

#### MODES

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

* App maintained by Russell Uman
* jirarest command written by Fred de Boer
* jirasoap command written by Fred de Boer
* jiraxml command written by Stephen Sorkin and Jeffrey Isenberg
* The Splunk MySQL app was used as a model, and lots of snippets here were stolen from its commands
* To support the jirasoap command, this App redistributes suds 4.0 https://fedorahosted.org/suds/

## Support

Please open an issue on github if you have any trouble with the app, or contact the maintainer through github.
Please feel free to fork and make pull requests if you find a bug that you can fix or have an enhancement to add.