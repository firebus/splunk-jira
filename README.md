JIRA App for Splunk
===================

This is a JIRA App for Splunk.

It provides a 'jira' search command that will send a JQL search to a JIRA instance, and return results as a table.

See bin/jira.py for command documentation.

To deploy the app

1. Create a folder named local, copy default/jira.conf into local, and update with configuration specific to your instance.
2. Copy config.ini.sample to config.ini and update with your authentication credentials

Configure which keys to display in the table with the keys, time_keys, and custom_keys fields.

Please open an issue if you have any trouble with the app, and please feel free to fork and make pull requests if you find a bug
that you can fix or have an enhancement to add

Thanks!