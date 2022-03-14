#!/bin/bash

echo "Container starting...Done"
usermod -a -G plugdev cwtests
chown -R cwtests results
chmod -R +x results
rm -rf results/*

su cwtests -c "cd /home/cwtests/ && python -u /home/cwtests/testing_server.py /home/cwtests/chipwhisperer /home/cwtests/tests.yaml" 2>&1
