#! python3
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sender and receiver details
sender_email = os.getenv("mail_username")
receiver_email = os.getenv("mail_to")
app_password = os.getenv("mail_appKey")

if (not sender_email or not receiver_email or not app_password):
    print("Must set env vars. See doc")
    exit(9)

# Email content
subject = "Test Email from Python"
body = "This is a test email sent from Python using an app-specific password."

# Create the email
message = MIMEMultipart()
message["From"] = "Cat Watcher"
message["To"] = receiver_email
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# Send the email
try:
    # Connect to Gmail's SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Secure the connection
        server.login(sender_email, app_password)  # Log in with the app password
        server.sendmail(sender_email, receiver_email, message.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")
