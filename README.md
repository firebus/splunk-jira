JIRA Add-on for Splunk
======================

This is a JIRA Add-on for Splunk.

* Download from http://www.gitub.com/firebus/splunk-jira
* Upgoat at http://apps.splunk.com/app/1438/

## Commands

### jira (SearchRequest XML)

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

jira is a 'generating' command that produces a results table. It does not create events. There is also a prototype retainsevents version called 'jiraevents' with the same syntax.
It creates real events instead of a table, but the events are empty so far...

### jirasoap (SOAP API)

#### Syntax

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

#### Arguments

* time
    * *Syntax:* now | updated | created | resolved
    * *Description:* By default, _time is set to the current timestamp (now), but if you'd like to have _time reflect one of the native timefields on the issue, you can choose from updated, created, or resolved (if this field is empty, _time will be set to the unix epoch - January 1, 1970 00:00:00 GMT)

#### Notes

jirasoap is a 'generating' command that produces a results table. It does not create events. There is also a prototype retainsevents version called 'jirasoapevents' with the same syntax.
It creates real events instead of a table, but the events are empty so far...

## Deployment

1. Place the app into $SPLUNK_HOME/etc/apps/jira
2. Create a folder named local, copy default/jira.conf into local, and update with configuration specific to your instance.
3. Copy config.ini.sample to config.ini and update with your authentication credentials

Configure which keys to display in the table with the keys, time_keys, and custom_keys fields.

* Note that the SOAP API command ignores the key configuration.

## Acknowledgements

* We're redistributing suds 4.0 https://fedorahosted.org/suds/
* Original jira commands written by Stephen Sorkin, Jeffrey Isenberg, and Fred de Boer
* MySQL app was used as a model, and lots of snippets here were stolen from its commands

## Support

Please open an issue on github if you have any trouble with the app. 
Please feel free to fork and make pull requests if you find a bug that you can fix or have an enhancement to add.