Change Log
==========

## 2.0.1

* Add urlencode.quote_plus to arguments so that we don't barf on special characters

## 2.0

* Add jirarest command and documentation
* Rename jira and jiraevents commands to jiraxml and jiraxmlevents respectively - "| jira" is now an alias of jirarest
* jiraxml and jirasoap commands are now deprecated, and will not be developed further (but pull requests are still accepted if there's something you need to have fixed!)
* source is standardized as the command being run: jira_rest, jira_xml, jira_soap
* sourcetype is standardized as the kind of results being returned: jira_issues, jira_filters, jira_sprints, etc.
* index is no longer set in returned events

## 1.11

* Remove _raw field as it was misformatted, and made it impossible to collect results in a summary index

## 1.10

* Add time option to SearchXML and SOAP commands, allows setting _time field to now(), updated, resolved, or created

## 1.9

* Make time_keys and custom_keys configuration parameters optional for the SearchXML command

## 1.8

* Make Protocol and Port configurable
* gitignore .pyc files

## 1.7

* Set _time to now()
* Fix a bug that breaks the main while loop when tempMax is undefined

## 1.6

* Make output of fixVersions prettier in the SOAP command
* Switch from keywords to sys.argv to parse command line and options
* Fix bug in default query

## 1.5

* Make tempMax configurable in SearchXML command
* Make mv fields actually mv in SearchXML command
* Manually construct header in SearchXML command to preserve ordering

## 1.4

* Fix bug with outputResults()
* Move hostname configuration to config.ini

## 1.3 

* Add alternate streaming versions of both commands

## 1.2 

* Add SOAP command

## 1.1

* Add _time field

## 1.0

* Initial commit of SearchXML command