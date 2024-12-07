import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(image_path):
    SENDER_USERNAME = os.getenv("mail_username")
    SENDER_PASSWORD = os.getenv("mail_appKey")
    RECEIVER_EMAIL = os.getenv("mail_to")
    SENDER_EMAIL = "Cat Watcher"

    try:
        # Prepare the email
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        msg['Subject'] = 'Motion Detected!'

        body = "Motion has been detected by your Raspberry Pi camera. Please find the attached image."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the image
        with open(image_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(image_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(image_path)}"'
            msg.attach(part)

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_USERNAME, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, text)
        server.quit()

        print(f"Email sent with image: {image_path}")

        # Update the last email time
        # with open(LAST_EMAIL_FILE, "w") as file:
        #     file.write(datetime.now().isoformat())

    except Exception as e:
        print(f"Error sending email: {e}")

