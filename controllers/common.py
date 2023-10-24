import os
import smtplib


from datetime import datetime
from mongodb import db

from utils import HTML_TEMPLATES_SOURCE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from utils import (
    FROM,
    PASSWORD,
    PORT
)


def parseDate(string, format="%d.%m.%Y"):
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


async def sendTemplateMail(data, multiple=False):
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

    for i, v in enumerate(replacers):
        print("Replace ", v, replacers[v])
        content = content.replace(v, replacers[v])

    msg.attach(MIMEText(content, "html"))

    try:
        server = smtplib.SMTP("smtp.office365.com", PORT)
        server.starttls()
        server.login(FROM, PASSWORD)
        server.sendmail(FROM, msg["To"], msg.as_string())
        server.quit()

    except Exception as e:
        print(f"{type(e)} - {e} - Email send error")
        raise