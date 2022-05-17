.. _github_integration

******************
Github Integration
******************

To provide continuous integration (or at least something close) for the hardware, software,
and notebooks, the test server has been integrated with Github Actions. Due to limitations
with Github Actions, **direct access for the test server MUST NOT be given to any public repo**.
This is because Actions give Remote Code Execution to pull requests - someone can create
a new pull request with an Action that runs on pull requests, allowing it to run shell scripts on the server.

As such, our integration involves three repositories - the main ChipWhisperer repo, a private 
repo that has access to the test server, and a public repo that stores the test results. This
works as follows:

#. An on push Action for the ChipWhisperer repo uses workflow-dispatch to trigger the Private repo
#. The Private repo spins up a docker image, waits for that to finish, then pushes the results to the final repo using another action
#. An on push Action for the results repo checks the results

The original ChipWhisperer repo can then link to the results repo's badge, allowing users
to know if the tests passed.

