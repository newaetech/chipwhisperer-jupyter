#!/bin/python3

# Script used to send e-mails of test results

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sys import argv

from_email = os.environ.get('FROM_EMAIL')
to_emails = os.environ.get('TO_EMAILS')

script, subject, email_contents_file = argv

with open(email_contents_file, 'r') as f:
    email_contents = f.read()

message = Mail(
    from_email=from_email,
    to_emails=to_emails,
    subject=subject,
    plain_text_content=email_contents)
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
