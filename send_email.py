"""
Send an email with an image attachment
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
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

def send_email(mail_options : MailOptions,
                image_path : str,
                trigger_image_path : str,
                seconds: int) -> None:
    """
    Send an email with an image attachment

    Args:
        mail: MailOptions object with email configuration
        image_path: Path to the image to send
        trigger_image_path: Path to the second image to send
        seconds: The number of seconds after the trigger

    """

    if image_path is None:
        logger.info('No image to send')
        return

    logger.info("Sending email with image: %s", image_path)

    try:
        # Prepare the email
        msg = MIMEMultipart('related')
        msg['From'] = mail_options.from_email
        msg['To'] = mail_options.to_email
        msg['Subject'] = mail_options.subject

        msg_alternative = MIMEMultipart('alternative')
        msg.attach(msg_alternative)

        body = mail_options.message
        msg_text = (f'<html><body>{body}<br><br>{seconds} second{"" if seconds == 1 else "s"}'
                    ' after trigger<img src="cid:image1"><br>')

        # Attach the first image inline
        with open(image_path, "rb") as attachment:
            img = MIMEImage(attachment.read())
            img.add_header('Content-ID', '<image1>')
            msg.attach(img)

        if trigger_image_path is not None:
            msg_text += 'Trigger image<img src="cid:image2"><br>'
            with open(trigger_image_path, "rb") as attachment:
                img = MIMEImage(attachment.read())
                img.add_header('Content-ID', '<image2>')
                msg.attach(img)

        msg_text += '</body></html>'
        msg_alternative.attach(MIMEText(msg_text, 'html'))

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
    logger = logging.getLogger("detector")
    logger.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages

    # Create formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    mail = get_email_config()
    send_email(mail,
               "motion_images/motion_detected.jpg",
               "motion_images/motion_detected_cv2.jpg",
               1)
