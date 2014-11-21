Tests
=====

This is a manual test script (which is not the best, but it's significantly better than nothing)

Please test each of these queries, substituting variables for ones that make sense for your JIRA installation, before each
release or pull request. | table helps verify.

## jirarest

| jirarest filters
* Should return a list of filters favorited by the jira user.

| jirarest issues FILTER_ID
* Should return a list of issues. Use an id from the filters mode.

| jirarest jqlsearch JQL_QUERY
* Should return a list of issues for some reasonable query.

| jirarest jqlsearch JQL_QUERY comments
* Should return a list of comments on the issues returned by the query.

| jirarest jqlsearch JQL_QUERY changefield
* Should return a list of issues with internal field names instead of pretty field names.

| jirarest jqlsearch JQL_QUERY changetime updated
* Should return a list of issues with _time set to updated instead of created.

| jirarest jqlsearch JQL_QUERY comments changefield changetime updated
* All together now.

| jirarest jqlsearch JQL_QUERY fields "status,duedate"
* Should return a list of issues with just key, created, status, and duedate fields.

| jirarest changelog JQL_QUERY
* Should return a list of changes (history) for the issues returned by the query.

| jirarest rapidboards list
* Should return a list of all rapidboards.

| jirarest rapidboards all
* Should return a list of all sprints in all rapidboards.

| jirarest rapidboards RAPIDBOARD_ID
* Should return a list of all issues in a specific rapidboard. Use an id from the list option.

| jirarest rapidboards RAPIDBOARD_ID detail sprints
* Should return a list of all sprints in a specific rapidboard. Use an id from the list option.

| jirarest rapidboards RAPIDBOARD_ID detail issues
* Should return a list of all active issues in a specific rapidboard, including column and swimlane information.
  Use an id from the list option.

... | jirarest batch JQL_QUERY $foo$
* I don't really know how to test this I should get an example from Fred.

## jirasoap

## jiraxml