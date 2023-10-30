import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils import (
    HTML_TEMPLATES_SOURCE,
    EMAIL_HOST,
    EMAIL_FROM,
    EMAIL_PASSWORD,
    EMAIL_PORT,
)


def parse_date(string, format="%d.%m.%Y"):
    return datetime.strptime(string, format)


def extract_name_from_email(email):
    email_parts = email.split("@")
    email_username = email_parts[0]

    name_parts = email_username.split(".")
    first_name = name_parts[0].capitalize()
    try:
        last_name = name_parts[1].capitalize()
    except IndexError:
        last_name = ""

    return first_name, last_name


async def send_template_mail(data, multiple=False):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = data["title"]

    receiver = data["receiver"]
    replacers = data["replacers"]

    template_path = os.path.join(HTML_TEMPLATES_SOURCE, data["template"])
    content = open(template_path, "r+").read()

    if multiple:
        msg["To"] = ", ".join(receiver)
    else:
        msg["To"] = receiver

    for _, value in enumerate(replacers):
        content = content.replace(value, replacers[value])

    msg.attach(MIMEText(content, "html"))

    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, receiver, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"{type(e)} - {e} - Email send error")
        raise


def get_full_name_opt(email, users):
    user = list(filter(lambda x: x.get("email") == email, users))[0]
    firstname, lastname = user.get("firstname"), user.get("lastname")
    return f"{firstname} {lastname}"
