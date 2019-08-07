#!/bin/bash

# export environment for cron job
# whitelist the environmental variables that carry over
# and add double quotes for all key value pairs to avoid
# spaces in value causing problem
env | grep 'SENDGRID_API_KEY\|FROM_EMAIL\|TO_EMAILS' | sed 's/\(^.*\)=\(.*\)/export \1="\2"/' > /tmp/env.sh

echo "Starting cron in the foreground...done"
# start crontab in the foreground
cron -l 2 -f
