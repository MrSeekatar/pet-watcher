import smtplib
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import sys
import configparser
import logging
logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class MailOptions:
    def __init__(self, mail):
        if mail is None:
            return
        # required fields
        self.username = mail['username']
        self.password = mail['password']
        self.to_email = mail['to']

        # optional fields
        self.from_email = mail.get('from', 'Cat Watcher')
        self.smtp_server = mail.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = mail.getint('smtp_port', 587)
        self.subject = mail.get('subject', 'Motion Detected')
        self.message = mail.get('message','Motion has been detected by your Raspberry Pi camera. Please find the attached image.')

def get_email_config() -> Optional[MailOptions]:
    config = configparser.ConfigParser()
    config.read('email.ini')
    mail = config['email']
    if mail is None:
        logger.error('Email configuration not found in email.ini')
        return None
    else:
        ret = MailOptions(mail)
        logger.info('Email settings:')
        logger.info(f'  Username:   {ret.username}')
        logger.info(f'  ApiKey:     {ret.password[:3]}...')
        logger.info(f'  To:         {ret.to_email}')

    return ret

def send_email(mail : MailOptions, image_path : str) -> None:

    if image_path is None:
        logger.info('No image to send')
        return
    
    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = mail.from_email
        msg['To'] = mail.to_email
        msg['Subject'] = mail.subject

        body = mail.message
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        with open(image_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(image_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(image_path)}"'
            msg.attach(part)

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(mail.smtp_server, mail.smtp_port)
        server.starttls()
        server.login(mail.username, mail.password)
        text = msg.as_string()
        server.sendmail(mail.from_email, mail.to_email, text)
        server.quit()

        logger.info(f"Email sent with image: {image_path}")

    except Exception as e:
        logger.exception(f"Error sending email: {e}")

if __name__ == "__main__":
    mail = get_email_config()
    send_email(mail, "motion_images/motion_detected.jpg")