import time
import cv2
from picamera2 import Picamera2
from datetime import datetime, timedelta
from detect_motion_1 import setup_camera, detect_motion
import os
import sys

# Configuration
CONTOUR_THRESHOLD = 1000 # 500 was original value and pretty sensitive
SENDER_USERNAME = os.getenv("mail_username")
SENDER_PASSWORD = os.getenv("mail_appKey")
RECEIVER_EMAIL = os.getenv("mail_to")
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

setup_camera()

# Run the motion detection
detect_motion(last_email_time, CONTOUR_THRESHOLD, IMAGE_SAVE_DIR, CHECK_INTERVAL, TIME_LIMIT)
