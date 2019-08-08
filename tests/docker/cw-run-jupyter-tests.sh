#!/bin/bash

# access variables defined by docker created by
# startup script

CURRENTDATEPRETTY=$(date +"%A, %b %d, %Y %H:%M:%S %Z")
CURRENTDATELOG=$(date +"%Z_%m_%d_%Y__%H_%M")
LOGFILE="/tmp/$CURRENTDATELOG-cw-tests.log"

# clear logs and add date
echo "$CURRENTDATEPRETTY" > "$LOGFILE"

# update the chipwhisperer repo
cd /home/$USER/chipwhisperer && git pull --rebase && git submodule update --init jupyter >> "$LOGFILE"

# record what hash you have checked out
echo "Checked out hash:" >> "$LOGFILE"
cd /home/$USER/chipwhisperer && git rev-parse $(git branch | grep \* | cut -d ' ' -f2) >> "$LOGFILE"

# run the tests
cd /home/$USER/chipwhisperer/jupyter/tests && python3 tutorials.py $1 >> "$LOGFILE"

# send the results via mail
# place in log after sending to get the output of the mail
# operation for when looking at log files in the container
# this also loads docker set env variables for use by python
. /tmp/env.sh && /usr/bin/python3 /usr/local/bin/send-mail.py "ChipWhisperer Test Results $CURRENTDATEPRETTY" "$LOGFILE" >> "$LOGFILE"


