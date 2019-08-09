## Building

```docker build . -t cw-testing-server```

## Configuring

First make sure the udevadm rules are changed on the host. Just follow the ChipWhisperer installation where the *plugdev* group is created.

## Running
First create an api key on *newae* SendGrid account and give it *only* send mail permissions. **Delete the old key**. Use the new key when starting the container.

```
docker run --privileged
    -v /dev:/dev \
    -e TO_EMAILS="email@example.com, another@email.com" \
    -e FROM_EMAIL="from@email.com" \
    -e SENDGRID_API_KEY="the sendgrid api key" \
    cw-testing-server
```

**Warning: do not commit the docker container after it has been started, or somehow add the key to the VCS. If this happens (it should not), delete the key right away and recreate a new API key**

The tests should be run as a cronjob every 4 hours starting at 6:00 until 18:00 (server time), and e-mail will be sent to all the emails specified after the tests are complete. Check your spam!
Note that the running container will not print anything to terminal other that when it starts cron in the foreground. That is expected behaviour as everything is logged instead.

## Troubleshooting

Find the container currently running:

```docker ps```

Attach to the container using:

```docker exec -it <container id> /bin/bash```

Check the log files that are used:

  * */var/log/cw-cron.log* This log file contains the stdout and stderr of the cron job
  * */tmp/<date time>_cw-test.log* Multiple files containing the output of the cw-run-jupyter-tests.sh file for each time the cronjob is executed.
  * */tmp/env.sh* contains the environment variables passed to the cw-run-jupyter-tests.sh script by the start-container.sh script at container startup.
