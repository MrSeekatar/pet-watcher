#! /usr/bin/env python3
import configparser
import logging
import os
import sys
import time

import cv2
import picamera2

import send_email

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

class MotionOptions:
    """
    This class is used to store the motion options


    """
    def __init__(self, config: dict):
        if config is None:
            return

        # optional fields
        self.threshold = config.getint('threshold', 25)
        self.min_area = config.getint('min_area',500)
        self.image_save_dir = config.get('image_save_dir', 'motion_images')
        self.can_display = os.environ.get("DISPLAY") is not None
        self.image_delay_seconds = config.getfloat('image_delay_seconds', 1.0)
        self.time_limit_minutes = config.getint('time_limit_minutes', 2)

        self.picam2 : picamera2.PiCamera2 = None

    @staticmethod
    def get_motion_options():
        """
        Get the motion options from the configuration file

        """
        config = configparser.ConfigParser()
        config.read('motion.ini')
        motion = config['motion']
        if motion is None:
            logger.error('Motion configuration not found in motion.ini')
            return None
        else:
            ret = MotionOptions(motion)
            logger.info('Motion settings:')
            logger.info('  Threshold:   %s', ret.threshold)
            logger.info('  Min Area:    %s', ret.min_area)
            logger.info('  Image Save Dir: %s', ret.image_save_dir)
            logger.info('  Can Display: %s', ret.can_display)

        return ret

def setup():

    options = MotionOptions.get_motion_options()

    if options is None:
        return None

    # Initialize the camera
    picam2 = picamera2.Picamera2()
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    options.picam2 = picam2

    return options

# Threshold 200 doesn't work
# 100 works, but slow motion is detected
# 50 works, pretty well
# 25 works
# min_area up to 15000 works since that's the change area
def detect_motion_ai_camera(options: MotionOptions):
    """
    Detect motion using Raspberry Pi Camera Module and Picamera2.

    Args:
        threshold (int): The threshold for detecting changes between frames.
        min_area (int): Minimum contour area to qualify as motion.
    """
    canDisplay = os.environ.get("DISPLAY") is not None
    print("started.")
    print(f"  Can display: {options.can_display}")
    print(f"  Threshold:   {options.threshold}")
    print(f"  Min Area:    {options.min_area}")

    # Capture the first frame
    frame = options.picam2.capture_array()
    print("Captured array")
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    print("Motion detection started.")

    motionDetected = None
    logged = False

    try:
        while True:
            if ((motionDetected is not None) and
                (time.time() - motionDetected > options.image_delay_seconds)):
                # capture the current image and write it out
                print("Motion detected at %s, and > %.1f sec has passed" %
                      (motionDetected, options.image_delay_seconds))
                frame = cv2.cvtColor(options.picam2.capture_array(), cv2.COLOR_BGR2RGB)
                path = os.path.join(options.image_save_dir, "motion_detected.jpg")
                cv2.imwrite(path, frame)
                return path
            elif motionDetected is not None:
                if not logged:
                    print(f"Motion detected at {motionDetected}, but not in the last 2 seconds.")
                    logged = True
                continue

            # Capture the next frame
            frame = options.picam2.capture_array()

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # Calculate the difference between frames
            frame_delta = cv2.absdiff(prev_gray, gray_frame)

            # Display the frame_delta for debugging
            if canDisplay:
                cv2.imshow("Frame Delta", frame_delta)

            # Apply a binary threshold
            _, thresh = cv2.threshold(frame_delta, options.threshold, 255, cv2.THRESH_BINARY)

            # Dilate the threshold image to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(thresh.copy(),
                                            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            rectSet = False
            # Loop through contours and detect motion
            # print(f"Found {len(contours)} contours")
            for contour in contours:
                area = cv2.contourArea(contour)
                # print(f"Contour Area: {area} min_area is {min_area}")  # Debugging output
                if area < options.min_area:
                    continue

                # Get bounding box for the contour
                (x, y, w, h) = cv2.boundingRect(contour)
                # Draw rectangle around detected motion
                print(f"Motion detected at ({x}, {y}) with width {w} and height {h} area {area}")
                rectSet = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # write out the current cv2 image
                motionDetected = time.time()
                cv2.imwrite(os.path.join(options.image_save_dir, "motion_detected_cv2.jpg"), cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Display the frames
            if canDisplay:
                cv2.imshow("RGB Camera feed", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cv2.imshow("Threshold", thresh)

            # Update previous frame
            prev_gray = gray_frame.copy()

    except KeyboardInterrupt:
        print("Motion detection interrupted.")

    # finally:
    #     print(">>>> in finally to stop camera")
    #     picam2.stop()
    #     cv2.destroyAllWindows()

    # print("Motion detection stopped.")
    # picam2.stop()

def detect_motion(options: MotionOptions):

    email_options = send_email.get_email_config()

    while True:
        image_path = detect_motion_ai_camera(options)

        send_email.send_email(email_options, image_path)

        # wait before sending another email
        print(f"Sleeping for {options.time_limit_minutes} minutes")
        time.sleep(options.time_limit_minutes*60)


if __name__ == "__main__":
    config = setup()

    if config is None:
        logger.error('Missing config in motion.ini')
    elif config.picam2 is None:
        logger.error('Camera not initialized')
    else:
        detect_motion(config)

        config.picam2.stop()
