from tasks import send_email as emails
from config import TEST


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

    if not int(TEST):
        emails.delay(recipient, subject, template, **data)
