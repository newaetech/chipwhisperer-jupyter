## Building

```docker build . -t cw-testing-server```

## Configuring

First make sure the udevadm rules are changed on the host. Just follow the ChipWhisperer installation where the *plugdev* group is created.

## Running
First create an api key on *newae* SendGrid account and give it *only* send mail permissions. **Delete the old key**. Use the new key when starting the container. Before starting the container create a folder to share with the container for the tutorial output.

```mkdir $HOME/tutorials && chmod 777 $HOME/tutorials```

Then start the container:

```
docker run -it --privileged
    -v /dev:/dev \
    -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
    -e TO_EMAILS="email@example.com, another@email.com" \
    -e FROM_EMAIL="from@email.com" \
    -e SENDGRID_API_KEY="the sendgrid api key" \
    cw-testing-server
```

**Warning: do not commit the docker container after it has been started, or somehow add the key to the VCS. If this happens (it should not), delete the key right away and recreate a new API key**

The running container will log to console. On startup it will log the server time. After if the current hour is in the *HOURS* env variable given it will check if there are any changes to the repository. If there are it will test them. If not it will just continue checking.

## Future Enhancements

Allow the debug varaible to 

## Troubleshooting

Find the container currently running:

```docker ps```

Attach to the container using:

```docker exec -it <container id> /bin/bash```

Then play detective. If you are okay with restarting the container and testing this way you can restart with *DEBUG* set to anything that evaluates to True in python.

```docker run ...
    -e DEBUG=True \
    ...
    ...
```

## Docker

To clean up docker containers, and dangling images use:

```docker system prune```
