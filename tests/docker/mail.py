#!/bin/python3

# Script used to send e-mails of test results

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sys import argv


def send_mail(from_email, to_emails, subject, email_contents, api_key):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=email_contents)
    print(message)
    try:
        sg = SendGridAPIClient(api_key)
        print(api_key)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


if __name__ == '__main__':
    from_email = os.environ.get('FROM_EMAIL')
    to_emails_env = os.environ.get('TO_EMAILS')
    api_key = os.environ.get('SENDGRID_API_KEY')


    # for creating a iterable from comma seperated list
    to_emails = [email.strip() for email in to_emails_env.strip().split(',') if email.strip()]

    script, subject, email_contents = argv
    send_mail(from_email, to_emails, subject, email_contents, api_key)
    
