JIRA App for Splunk
===================

This is a JIRA App for Splunk.

It provides a jira search command that will send a JQL search to a JIRA instance, and return results in a splunk-friendly format

You can pipe the results generated into an index, or do whatever. See bin/jira.py for command documentation.

To deploy the app, create a folder named local, copy default/jira.conf into local, and update with configuration specific to your
instance.

The custom_keys config variable takes a comma-separated list of custom fields you've defined in JIRA so that we can output them
correctly as events.

This works for me, and I've tried to make it as generic as possible, but it might not work for you! Please open an issue if you 
have any trouble with the app, and please feel free to fork and make pull requests if you find a bug that you can fix.

Thanks!