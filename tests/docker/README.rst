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
    the Docker-CE using the instructions on the docker website.

You also need to clone the chipwhisperer repository and pull the jupyter
submodule:

.. code::

    git clone https://github.com/newaetech/chipwhisperer.git

    cd chipwhisperer
    git submodule update --init jupyter

    cd jupyter
    git checkout master

You will need to copy the *99-newae.rules* files into */etc/udev/rules.d*
and apply the changes:

.. code::

    sudo cp chipwhisperer/hardware/99-newae.rules /etc/udev/rules.d/

    sudo usermod -a -G plugdev YOUR-USERNAME

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

    docker build . -t cw-testing-server


Running
=======

First create an api key on *newae* SendGrid account and give it *only* send mail
permissions. **Delete the old key**. Use the new key when starting the
container. Before starting the container create a folder to share with the
container for the tutorial output.

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

The tutorials will be written in both html and ReST to the *$HOME/tutorials*
directory. The is useful for checking specifics of why tests failed.

.. warning:: do not commit the docker container after it has been started, or
    somehow add the key to the VCS. If this happens (it should not), delete the
    key right away and recreate a new API key

The running container will log to console. On startup it will log the server
time. After if the current hour is in the *HOURS* env variable given it will
check if there are any changes to the repository. If there are it will test
them. If not it will just continue checking.


Future Enhancements
===================

  * See if we can get a build badge based on the results.
  * Add ability to run tests on different hardware in parrallel.

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
        -e DEBUG=True \
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

    chmod +x run_interactively.sh
    ./run_interactively.sh

Then navigate to *localhost:8888* in your browser.
