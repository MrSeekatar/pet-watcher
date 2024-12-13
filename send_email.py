"""
Send an email with an image attachment
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
import configparser
import logging

logger = logging.getLogger("detector")


class MailOptions: # pylint: disable=R0902,R0903
    """ Class to hold email configuration options """
    def __init__(self, mail_config: dict):
        if mail_config is None:
            return
        # required fields
        self.username = mail_config['username']
        self.password = mail_config['password']
        self.to_email = mail_config['to']

        # optional fields
        self.from_email = mail_config.get('from', 'Cat Watcher')
        self.smtp_server = mail_config.get('smtp_server', 'smtp.gmail.com')
        self.smtp_port = mail_config.getint('smtp_port', 587)
        self.subject = mail_config.get('subject', 'Motion Detected')
        self.message = mail_config.get('message','Motion has been detected the Cat Detector Van. '
                                'Please see the attached image.')

def get_email_config() -> MailOptions | None:
    """
    Get the email configuration from the email.ini file

    Returns:
        MailOptions: Email configuration options if ok
        None: If there was an error in configuration
    """

    config = configparser.ConfigParser()
    config.read('email.ini')
    mail_config = config['email']
    if mail_config is None:
        logger.error('Email configuration not found in email.ini')
        return None

    ret = MailOptions(mail_config)
    logger.info('Email settings:')
    logger.info('  Username:   %s', ret.username)
    logger.info('  ApiKey:     %s...', ret.password[:3])
    logger.info('  To:         %s', ret.to_email)

    return ret

def send_email(mail_options : MailOptions, image_path : str) -> None:
    """
    Send an email with an image attachment

    Args:
        mail: MailOptions object with email configuration
        image_path: Path to the image to send

    """

    if image_path is None:
        logger.info('No image to send')
        return

    logger.info("Sending email with image: %s", image_path)

    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = mail_options.from_email
        msg['To'] = mail_options.to_email
        msg['Subject'] = mail_options.subject

        body = mail_options.message
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        with open(image_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(image_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(image_path)}"'
            msg.attach(part)

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(mail_options.smtp_server, mail_options.smtp_port)
        server.starttls()
        server.login(mail_options.username, mail_options.password)
        text = msg.as_string()
        server.sendmail(mail_options.from_email, mail_options.to_email.split(','), text)
        server.quit()

        logger.info("Email sent with image: %s", image_path)

    except Exception as e: # pylint: disable=C0103,W0718
        logger.exception("Error sending email: %s", e)

if __name__ == "__main__":
    mail = get_email_config()
    send_email(mail, "motion_images/motion_detected.jpg")
