import os
import smtplib
from email.mime.text import MIMEText

from jinja2 import Template

sender = os.environ.get('EMAIL')
sender_password = os.environ.get('PASSWORD_EMAIL')


def send_email(recipient: str, subject: str, template: str, **data):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        with open(template) as file:
            html = file.read()
    except IOError:
        return 'The template file not found'

    t = Template(html)
    message = t.render(**data)

    try:
        server.login(sender, sender_password)
        msg = MIMEText(message, 'html')
        msg['From'] = sender
        msg['To'] = recipient
        msg['Subject'] = subject
        server.sendmail(sender, recipient, msg.as_string())
    except Exception as _ex:
        print(_ex)
