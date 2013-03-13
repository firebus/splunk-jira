JIRA Add-on for Splunk
======================

This is a JIRA Add-on for Splunk.

## Commands

### jira (SearchRequest XML)

* Send a JQL query, return a table with one row for each result
	* | jira "JQL query"

* jira is a 'generating' command. There is also a prototype 'streaming' command available called 'jiraevents'. It creates real 
  events instead of a table, but does not preserve anything streamed into it yet.

### jirasoap (SOAP API)

* List all filters available to the logged-in user
	* | jirasoap filters
* Run a filters
	* | jirasoap issues <filter_id>
* Run a text search
	* | jirasoap search "foo bar bas"
* Run a JQL search
	* | jirasoap jqlsearch "project in (foo) AND status in (bar)
	* jqlsearch does not parse JQL containing '=' very well, so please use 'in' instead, or use the 'jira' command instead.

* jirasoap is a 'generating' command. There is also a prototype 'streaming' command available called 'jirasoapevents'. It creates
  real events instead of a table, but does not preserve anything streamed into it yet.

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

Please open an issue if you have any trouble with the app, and please feel free to fork and make pull requests if you find a bug
that you can fix or have an enhancement to add