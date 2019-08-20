.. _hardware_and_tutorial_testing_server:

************************************
Hardware and Tutorial Testing Server
************************************

The hardware and tutorial testing server aims to provide testing functionality for the Jupyter Notebook
tutorials on various hardware. The current tested hardware and notebooks can be found in the *tests
.yaml* file. The syntax for that file is explained in the file and hardware configurations can be added
as needed.

It is important to understand what parts of the testing server are pulled from the repository and which
need to be updated by rebuilding the docker image. Any change to any file in the *docker* folder
requires and image rebuild. This was done to allow changing files that are specifically written for the
server without have to keep pushing commits to the repository to test them. Therefore, the configuration
file can quickly be changed and the image rebuilt to try out changes. One useful one is to remove all
but one test so that you can tests changes to the email procedure or other step that occur at the end of
the build process.

This directory contains all you need for setting up the testing server for ChipWhisperer. Here is a list
of features of the hardware and tutorial testing server.

  * Checks periodically for updates to the **chipwhisperer** repository on the develop branch.
  * Tests install process for **chipwhisperer**, and **jupyter** submodule in virtual environment.
  * Clears the virtual environment between test runs.
  * Runs through all tutorials based on the configuration in the *tests.yaml* file.
  * Exports HTML and ReST results of tutorials to the **tutorials** submodule inside the docker container.
  * Uses a HTML template to create a e-mail with summary of tests results and output.
  * Sends this e-mail using Sendgrid to email addresses given at docker container start up.

.. note:: All following commands include relative paths from the *chipwhisperer/jupyter/tests/docker*
    directory. If the command contains a path, it should be run from there.

What the testing server is not is a replacement for unit testing and other testing done before committing
changes. However, it gets us closer to a more stable and reliable ChipWhisperer.
Building
========

.. code::

    docker build . -t cw-testing-server


Configuring
===========

First make sure the udevadm rules are changed on the host. Just follow the ChipWhisperer installation
where the *plugdev* group is created.


Running
=======

First create an api key on *newae* SendGrid account and give it *only* send mail permissions. **Delete
the old key**. Use the new key when starting the container. Before starting the container create a
folder to share with the container for the tutorial output.

.. code::

    mkdir $HOME/tutorials && chmod 777 $HOME/tutorials

Then start the container:

.. code::

    docker run -it --privileged
        -v /dev:/dev \
        -v $HOME/tutorials/:/home/cwtests/chipwhisperer/tutorials \
        -e TO_EMAILS="email@example.com, another@email.com" \
        -e FROM_EMAIL="from@email.com" \
        -e SENDGRID_API_KEY="the sendgrid api key" \
        cw-testing-server

The tutorials will be written in both html and ReST to the *$HOME/tutorials* directory. The is useful for checking specifics of why tests failed.

.. warning:: do not commit the docker container after it has been started, or somehow add the key to the
    VCS. If this happens (it should not), delete the key right away and recreate a new API key

The running container will log to console. On startup it will log the server time. After if the current
hour is in the *HOURS* env variable given it will check if there are any changes to the repository. If
there are it will test them. If not it will just continue checking.


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

Then play detective. If you are okay with restarting the container and testing this way you can restart
with *DEBUG* set to anything that evaluates to True in python.

.. code::

    docker run ...
        -e DEBUG=True \
        ...
        ...


If you want to overwrite the starting command and just run the container interactively:

.. code::

    docker run -it cw-testing-server:latest /bin/bash

Docker
======

To clean up docker containers, and dangling images use:

.. code::

    docker system prune
