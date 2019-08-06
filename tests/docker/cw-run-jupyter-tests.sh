#!/bin/bash

echo starting tests

# update the chipwhisperer repo
cd /home/$USER/chipwhisperer && git pull --rebase && git submodule update --init jupyter

# run the tests
cd /home/$USER/chipwhisperer/jupyter/tests && python3 tutorials.py $1


