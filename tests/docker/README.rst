.. _hardware_and_tutorial_testing_server:

************************************
Hardware and Tutorial Testing Server
************************************

The hardware and tutorial testing server aims to provide testing functionality
for the Jupyter Notebooktutorials on various hardware. The current tested
hardware and notebooks can be found in the *tests.yaml* file. The syntax for
that file is explained in the file and hardware configurations can be added
as needed.

It is important to understand what parts of the testing server are pulled from
the repository and whichneed to be updated by rebuilding the docker image. Any
change to any file in the *docker* folderrequires and image rebuild. This was
done to allow changing files that are specifically written for theserver without
have to keep pushing commits to the repository to test them. Therefore, the
configuration file can quickly be changed and the image rebuilt to try out
changes. One useful one is to remove all but one test so that you can tests
changes to the email procedure or other step that occur at the end of
the build process.

This directory contains all you need for setting up the testing server for
ChipWhisperer. Here is a list of features of the hardware and tutorial testing
server.

  * Checks periodically for updates to the **chipwhisperer** repository on the
    develop branch.
  * Tests install process for **chipwhisperer**, and **jupyter** submodule in
    virtual environment.
  * Clears the virtual environment between test runs.
  * Runs through all tutorials based on the configuration in the *tests.yaml*
    file.
  * Exports HTML and ReST results of tutorials to the **tutorials** submodule
    inside the docker container.
  * Uses a HTML template to create a e-mail with summary of tests results and
    output.
  * Sends this e-mail using Sendgrid to email addresses given at docker
    container start up.

.. note:: All following commands include relative paths from the
    *chipwhisperer/jupyter/tests/docker* directory. If the command contains a
    path, it should be run from there.

What the testing server is not is a replacement for unit testing and other
testing done before committing changes. However, it gets us closer to a more
stable and reliable ChipWhisperer.

Configuring and Building
========================

You will need a few packages installed:

  * udev
  * libusb-dev

.. warning:: Do not install the docker package through apt. You need to install
    the Docker-CE using the `instructions`_ on the docker website.

.. _instructions: https://docs.docker.com/install/linux/docker-ce/ubuntu/

You also need to clone the chipwhisperer repository and pull the jupyter
submodule:

.. code::

    git clone https://github.com/newaetech/chipwhisperer.git

    cd chipwhisperer
    git submodule update --init jupyter

    cd jupyter
    git checkout master

You will need to copy the *50-newae.rules* files into */etc/udev/rules.d*
and apply the changes:

.. code::

    sudo cp chipwhisperer/hardware/50-newae.rules /etc/udev/rules.d/

    sudo udevadm control --reload-rules

Then log in and out again. This will give the host access to the ChipWhisperer
devices when they are plugged in, as long as they are passed through if you are
using a VM based server.

You also need to have access to running docker without sudo. You can do this by
adding yourself to the **docker** group.

.. code::

    groupadd docker

    usermod -a -G docker <you username>

You will need to log out and in again. Finally you can build the image using
the docker cli.

.. code::

    cd chipwhisperer/jupyter/tests/docker
    docker build . -t cw-testing-server


Running
=======

First create an api key on *newae* SendGrid account and give it *only* send mail
permissions. **Delete the old key**. Use the new key when starting the
container. Before starting the container create a folder to share with the
container for the tutorial output.

.. code::

    mkdir $HOME/tutorials && chmod 777 $HOME/tutorials
53373100383248323030323034333038
Then start the container:

.. code::

    docker run -d --privileged \
        -v /dev:/dev \
        -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
        -e TO_EMAILS="email@example.com, another@email.com" \
        -e FROM_EMAIL="testing-server@chipwhisperer.com" \
        -e SENDGRID_API_KEY="the sendgrid api key" \
        -e HOURS="6, 10, 14, 18" \
        cw-testing-server

The -d runs the container in the background, so you can sign out of your session
without the container stopping. If you want to see what the container prints
to the screen and want to test if it starts properly run it with *-it* instead
of *-d*. This will run it in the foreground with STDIN open and a pseudo tty
connection. If it runs using this method you can then press *Ctrl+C* to stop it
and restart it in detached mode.

The *--privileged* starts the docker container with all system privileges. Since
this is a testing server for private use this is fine. We are using the docker
cotnainer not for isolation but envrionment reproducibility. The *-v* option
allows mounting of the host files system to the docker container. The whole
*/dev* directory is mounted because the container needs access to the host
hardware. The tutorials directory is mounted to allow looking at the tutorials
output by the testing server during its testing sessions. It is for ease of
accessing those files mostly.

The *-e* option allows setting of environment variables inside the docker
container. The *TO_EMAILS* is a comma seperated string of emails to send the
test output to. The *FROM_EMAIL* is the email that will appear as the sender
when you look at the sent e-mail. This can be anything but I have chosen
*testing-server@chipwhisperer.com*. The *SENDGRID_API_KEY* is the api key you
created on the *newae* sendgrid account. The *HOURS* are the hours during which
the testing server checks for changes to the repository. This should be enough
to get the container running.

The tutorials will be written in both html and ReST to the *$HOME/tutorials*
directory. The is useful for checking specifics of why tests failed.

.. warning:: do not commit the docker container after it has been started, or
    somehow add the key to the VCS. If this happens (it should not), delete the
    key right away and recreate a new API key

The running container will log to console, unless started in detached mode. If
started in detached mode you can see the output by using:

.. code::

    docker ps

This will show the running containers an allow you to find out the docker id.
You can then run:

.. code::

    docker logs <container id>

You usually only have to type as much of the id as is necessary to make it
not match more than one container. So the first two characters are usually
enough.

The test server will continue checking for changes to the repository every 100
seconds by doing a pull and submodule update from the chipwhisperer repository
during the *HOURS* given. If there are changes it will run all the tests in the
*tests.yaml* files using the configuration specified.


Future Enhancements
===================

  * See if we can get a build badge based on the results.

Troubleshooting
===============

Find the container currently running:

.. code::

    docker ps

Attach to the container using:

.. code::

    docker exec -it <container id> /bin/bash

Then play detective. If you are okay with restarting the container and testing
this way you can restart with *DEBUG* set to anything that evaluates to True in
python.

.. code::

    docker run ...
        -e DEBUG="True" \
        ...
        ...


If you want to overwrite the starting command and just run the container
interactively:

.. code::

    docker run -it cw-testing-server:latest /bin/bash

Docker
======

To clean up docker containers, and dangling images use:

.. code::

    docker system prune


Running Jupyter Notebook Interactively
======================================

Sometimes what you need is to use the jupyter notebook instance inside the
container interactively. This can be done by using the **run_interactively.sh**
script:

.. code:: bash

    cd chipwhisperer/jupyter/tests/docker
    chmod +x run_interactively.sh
    ./run_interactively.sh

Then navigate to *localhost:8888* in your browser.

If the server is on your local network instead of on the same computer you can
use the same script in you ssh session. This will start the jupyter notebook and
print the token to you terminal screen. Then navigate to the servers IP address
and port 8888 in your browser. You should then be asked for your token/password.
Copy the token from your ssh session into your browser and use it to sign on.
Ctrl+C in your ssh session will terminate the notebook server.

Bash Helper Functions
=====================

A few bash helper functions are provided in :code:`helper_func.sh`, including
:code:`run_test` (use :code:`run_test -h` to see args) to run the test image, :code:`build_test`
to build the test image, and :code:`attach_test image_id` to attach to the test image.

The following functions are available:

.. code:: bash
    build_test # navigate to ~/chipwhisperer/jupyter/tests/docker and build docker image

.. code:: bash
	# Usage: run_test [-h|--help] [-H|--hours hours] 
    #                 [--emails sendgrid_api_key from_email to_emails] 
    #                 [--no-check-git] [--no-clear]
    run_test # start docker test image

.. code:: bash
    kill_test # kill docker test image image

.. code:: bash
    attach_test # attach to docker test image

.. code:: bash
    log_test # display log for docker test image

.. code:: bash
    list_chipwhisperers # list newae devices/serial numbers from lsusb

.. code:: bash
    monitor_log file # repeatedly clear screen and print file

.. code:: bash
    monitor_summary # monitor_log ./sum_test.log

.. code:: bash
    monitor_summary # monitor_summary, but only with the "Finished all tests" line