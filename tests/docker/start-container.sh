#!/bin/bash

echo "Container starting...Done"

su cwtests -c "cd /home/cwtests/ && /usr/bin/python3 -u /home/cwtests/testing_server.py /home/cwtests/chipwhisperer /home/cwtests/tests.yaml" 2>&1
