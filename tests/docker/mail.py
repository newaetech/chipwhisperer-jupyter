#!/bin/python3

# Script used to send e-mails of test results

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sys import argv
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape


def send_mail(from_email, to_emails, subject, email_contents):
    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=email_contents)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY').strip())
        response = sg.send(message)
        logging.info('email with test results sent to: {}'.format(to_emails))
    except Exception as e:
        print(e)


def create_email_contents(context):
    """Renders email using jinja2 template.

    Args:
        context (dict): A dictionary containing the rendering context.
            title:
                A string that is the header of the email. Useful
                for overall tests passed/failed.
            commit:
                A string of the commit hash that was checked out
            summaries:
                A iterable of strings containing summaries of each part, something
                like: 'XMEGA: 10 failed, 100 run'
            tests:
                A dictionary with keys as strings that will show up on the clickable
                button to expand the value which will be treated as code block.
    Returns:
        (str): The fully rendered html.
    """
    env = Environment(
        loader=FileSystemLoader('./mail'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('mail.html')
    return template.render(context)


if __name__ == '__main__':
    from_email = os.environ.get('FROM_EMAIL')
    to_emails_env = os.environ.get('TO_EMAILS')


    # for creating a iterable from comma seperated list
    to_emails = [email.strip() for email in to_emails_env.strip().split(',') if email.strip()]

    script, subject, email_contents = argv
    send_mail(from_email, to_emails, subject, email_contents)

