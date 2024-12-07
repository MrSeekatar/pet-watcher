import time
import cv2
from picamera2 import Picamera2
from datetime import datetime, timedelta
import os
import sys

from send_email import send_email

picam2 = None

def setup_camera():
    global picam2

    # Setup the camera using Picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(main={"size":(640,480)}))
    # picam2.set_controls({"Resolution": (640, 480)})
    picam2.start()


# Motion detection setup
# Initialize the motion detection
def detect_motion(last_email_time, CONTOUR_THRESHOLD, IMAGE_SAVE_DIR, CHECK_INTERVAL, TIME_LIMIT):

    global picam2

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

