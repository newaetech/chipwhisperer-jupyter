#!/bin/bash

CURRENTDATEPRETTY=$(date +"%A, %b %d, %Y %H:%M:%S")
CURRENTDATELOG=$(date +"%m_%d_%Y__%H_%M")
LOGFILE="/tmp/$CURRENTDATELOG-cw-tests.log"

# clear logs
echo "$CURRENTDATEPRETTY" > "$LOGFILE"

# update the chipwhisperer repo
cd /home/$USER/chipwhisperer && git pull --rebase && git submodule update --init jupyter >> "$LOGFILE"

# run the tests
cd /home/$USER/chipwhisperer/jupyter/tests && python3 tutorials.py $1 >> "$LOGFILE"

# send the results via mail
# /tmp/emails.txt is set by start-container.sh
cat "$LOGFILE" | mail -s "ChipWhisperer Test Results $CURRENTDATEPRETTY" $(< /tmp/emails.txt)


