import time
import cv2
import smtplib
from picamera2 import Picamera2
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime, timedelta
import os
import sys

# Configuration
CONTOUR_THRESHOLD = 1000 # 500 was original value and pretty sensitive
SENDER_EMAIL = "Cat Watcher"
SENDER_USERNAME = os.getenv("mail_username")
SENDER_PASSWORD = os.getenv("mail_appKey")
RECEIVER_EMAIL = os.getenv("mail_to")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
CHECK_INTERVAL = 5 # Interval between motion checks (in seconds)
TIME_LIMIT = timedelta(hours=1)  # Limit time between emails

if (not SENDER_USERNAME or not RECEIVER_EMAIL or not SENDER_PASSWORD):
    print("Must set env vars. See doc")
    exit(9)

print("Email settings:")
print(f"  Username:   {SENDER_USERNAME}")
print(f"  ApiKey:     {SENDER_PASSWORD[:3]}...")
print(f"  To:         {RECEIVER_EMAIL}")
print(f"  Time limit: {TIME_LIMIT}")

# File to store the time of the last email
LAST_EMAIL_FILE = "last_email_time.txt"
IMAGE_SAVE_DIR = "motion_images"  # Directory where images will be saved

# Create the directory to store images if it doesn't exist
if not os.path.exists(IMAGE_SAVE_DIR):
    os.makedirs(IMAGE_SAVE_DIR)

# Initialize variables
last_email_time = None

# # Read the last email sent time from file
# if os.path.exists(LAST_EMAIL_FILE):
#     with open(LAST_EMAIL_FILE, "r") as file:
#         last_email_time = datetime.fromisoformat(file.read().strip())
last_email_time = datetime.fromisoformat('2020-01-01')

# print(f"  Last email time {last_email_time}")

# Setup the camera using Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size":(640,480)}))
# picam2.set_controls({"Resolution": (640, 480)})
picam2.start()

# Motion detection setup
def send_email(image_path):
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

# Initialize the motion detection
def detect_motion():
    global last_email_time

    # Start the camera stream
    # print("Starting motion detection...")
    time.sleep(2)  # Let the camera warm up

    # Initialize the background subtractor for motion detection
    fgbg = cv2.createBackgroundSubtractorMOG2()

    firstPass = True
    while True:
        # print("capturing array...")
        # Capture an image
        frame = picam2.capture_array()

        # Convert the image to grayscale for motion detection
        # print("converting...")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fgmask = fgbg.apply(gray)

        # Find contours (moving objects)
        # print("finding contours...")
        contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False

        for contour in contours:
            if cv2.contourArea(contour) > CONTOUR_THRESHOLD:  # Area threshold to avoid tiny movements
                motion_detected = True
                break

        if motion_detected and not firstPass:
            # Save the image to a file with a timestamp
            image_path = os.path.join(IMAGE_SAVE_DIR, f"motion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
            cv2.imwrite(image_path, frame)
            print("Motion detected! Image written to ", image_path)

            # Check if enough time has passed since the last email
            if last_email_time is None or datetime.now() - last_email_time > TIME_LIMIT:
                print(f"Sending email since {datetime.now()} - {last_email_time} > {TIME_LIMIT}")
                send_email(image_path)
                last_email_time = datetime.now()
            else:
                print(f"Not sending email since {datetime.now()} - {last_email_time} <= {TIME_LIMIT}")
        else:
            print(f"No motion detected. First pass is {firstPass}")

        firstPass = False

        # Wait for the specified check interval
        # print(f"Sleeping for {CHECK_INTERVAL}s")
        sys.stdout.flush()
        time.sleep(CHECK_INTERVAL)

# Run the motion detection
detect_motion()
