#!/bin/bash

# start the mail server
service postfix start

# create file for emails that cron can read
# this is to get around the fact the env variables
# are not accessible in cron
TMP_FILE=/tmp/emails.txt
echo "" > $TMP_FILE

for email in $(echo $EMAILS | sed "s/,/ /g")
do
    echo $email >> $TMP_FILE
done

# start crontab in the foreground
cron -l 2 -f
