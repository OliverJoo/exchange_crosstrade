from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

# for attachments
from email.mime.base import MIMEBase
from email import encoders

# get file_name without directories
from os.path import basename
import datetime

# custom package
from oliver_util_package import io_utils
from oliver_util_package import log_utils

import logging

logger = log_utils.logging.getLogger()

def file_attach(file_path: str) -> MIMEBase:
    """
    Email file attachment

    param: file_path:str
    return: email_file:MIMEBase
    """
    logger.info(file_path)

    # email attachment
    email_file = MIMEBase('application', 'octet-stream')
    with open(file_path, 'rb') as f:
        file_data = f.read()

    email_file.set_payload(file_data)
    encoders.encode_base64(email_file)

    file_name = basename(file_path)
    email_file.add_header('Content-Disposition', 'attachment', filename=file_name)
    return email_file


def send_mail_html(receiver:str, subject:str, contents_html:str, file_path:str):
    """
    Sending email by html style

    :param receiver:str
    :param subject:str
    :param contents(html):str
    :param file_path:str
    :return: void
    """
    try:
        email_dict = io_utils.get_config_data("email")

        logger.info(receiver + ' : ' +  subject + ' : ' +  file_path)
        logger.debug(contents_html)

        # email info
        msg = MIMEMultipart()

        msg['FROM'] = email_dict['SMTP_USER']
        msg['TO'] = receiver
        msg['SUBJECT'] = subject

        start = """<html>
                        <body>
                            <center>"""

        end = """           </center>
                        </body>
                    </html>"""

        msg.attach(MIMEText(start + contents_html + end, "html"))

        if file_path != 'FILE':
            msg.attach(file_attach(file_path))

        smtp = smtplib.SMTP_SSL(email_dict['SMTP_SERVER'], email_dict['SMTP_PORT'])
        logger.debug('Serv connection Success!')
        smtp.login(email_dict['SMTP_USER'], email_dict['SMTP_PASSWORD'])
        logger.debug('Login Success!')
        smtp.sendmail(email_dict['SMTP_USER'], receiver, msg.as_string())
        logger.debug('Sending email Success!')
    except Exception as e:
        logger.warning(e)
        pass
    finally:
        smtp.close()
        logger.info('Sending Email Done!')

def send_mail(receiver:str, subject:str, contents:str, file_path:str):
    """
    Sending email with string text(only test purpose)

    :param receiver:str
    :param subject:str
    :param contents:str
    :param file_path:str
    :return: void
    """
    try:
        email_dict = io_utils.get_config_data("email")

        logger.info(receiver + ' : ' +  subject + ' : ' +   contents + ' : ' +  file_path)

        # email info
        msg = MIMEMultipart('alternative')

        msg['FROM'] = email_dict['SMTP_USER']
        msg['TO'] = receiver
        msg['SUBJECT'] = subject

        text = MIMEText(contents)
        msg.attach(text)

        if file_path != 'FILE':
            msg.attach(file_attach(file_path))

        smtp = smtplib.SMTP_SSL(email_dict['SMTP_SERVER'], email_dict['SMTP_PORT'])
        logger.debug('Serv connection Success!')
        smtp.login(email_dict['SMTP_USER'], email_dict['SMTP_PASSWORD'])
        logger.debug('Login Success!')
        smtp.sendmail(email_dict['SMTP_USER'], receiver, msg.as_string(contents))
        logger.debug('Sending email Success!')
    except Exception as e:
        logger.warning(e)
        pass
    finally:
        smtp.close()
        logger.info('Sending Email Done!')


# email sending test
"""
try:
    send_mail('lvsin@naver.com', '결제확인메일', 'ㅋㅋㅋㅋㅋ', 'FILE')
except Exception as e:
    print("Error : ", e)
    pass
"""