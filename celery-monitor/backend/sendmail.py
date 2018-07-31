#date:2018/7/27
import smtplib  # 加载电邮模块smtplib

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from conf import settings
def email(message):
    msg = MIMEText(message, 'plain', 'utf-8')
    msg['From'] = settings.sendmailuser
    msg['To'] = ','.join(settings.acceptmailuser)
    msg['Subject'] = settings.mailSubject

    server = smtplib.SMTP(settings.smtpmail, 25)
    server.login(settings.sendmailuser, settings.sendmailpasswd)
    server.sendmail(settings.sendmailuser, settings.acceptmailuser, msg.as_string())
    server.quit()