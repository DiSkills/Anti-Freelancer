import os
import smtplib
from email.mime.text import MIMEText

from celery import Celery
from jinja2 import Template

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(__name__)
celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND

sender = os.environ.get('EMAIL')
sender_password = os.environ.get('PASSWORD_EMAIL')


@celery.task(name='send_email')
def send_email(recipient: str, subject: str, template: str, **data) -> None:
    """
        Send email
        :param recipient: Recipient
        :type recipient: str
        :param subject: Subject
        :type subject: str
        :param template: Template
        :type template: str
        :param data: Jinja data
        :return: None
    """

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    with open(template) as file:
        html = file.read()

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
