#! /usr/bin/env python3
"""
Motion detection using Raspberry Pi Camera Module and Picamera2.
"""
import configparser
import logging
import os
import sys
import time

import cv2
import picamera2

import send_email

# pylint: disable=I1101
# Module 'cv2' has no '...' member.
# Consider adding this module to extension-pkg-allow-list if you want
# to perform analysis based on run-time introspection of living objects.

logger = logging.getLogger("detector")

class MotionOptions:
    """
    This class is used to store the motion options


    """
    def __init__(self, motion_config: dict):
        if motion_config is None:
            return

        # optional fields
        self.threshold = motion_config.getint('threshold', 25)
        self.min_area = motion_config.getint('min_area',500)
        self.image_save_dir = motion_config.get('image_save_dir', 'motion_images')
        self.has_display = os.environ.get("DISPLAY") is not None
        self.image_delay_seconds = motion_config.getfloat('image_delay_seconds', 1.0)
        self.time_limit_minutes = motion_config.getint('time_limit_minutes', 2)

        self.picam2 : picamera2.picamera2 = None

    @staticmethod
    def get_motion_options():
        """
        Get the motion options from the configuration file

        """
        motion_config = configparser.ConfigParser()
        motion_config.read('motion.ini')
        motion = motion_config['motion']
        if motion is None:
            logger.error('Motion configuration not found in motion.ini')
            return None

        ret = MotionOptions(motion)
        logger.info('Motion settings:')
        logger.info('  Threshold:   %s', ret.threshold)
        logger.info('  Min Area:    %s', ret.min_area)
        logger.info('  Image Save Dir: %s', ret.image_save_dir)
        logger.info('  Can Display: %s', ret.has_display)

        return ret

def setup() -> MotionOptions | None:
    """
    Setup the motion detection
    """

    options = MotionOptions.get_motion_options()

    if options is None:
        return None

    # Create the directory to store images if it doesn't exist
    if not os.path.exists(options.image_save_dir):
        os.makedirs(options.image_save_dir)

    # Initialize the camera
    picam2 = picamera2.Picamera2()
    motion_config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(motion_config)
    picam2.start()
    options.picam2 = picam2

    return options

# Threshold 200 doesn't work
# 100 works, but slow motion is detected
# 50 works, pretty well
# 25 works
# min_area up to 15000 works since that's the change area
def detect_motion_ai_camera(options: MotionOptions) -> str | None:
    """
    Detect motion using Raspberry Pi Camera Module and Picamera2.

    Args:
        threshold (int): The threshold for detecting changes between frames.
        min_area (int): Minimum contour area to qualify as motion.
    """
    # Capture the first frame
    frame = options.picam2.capture_array()
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    logger.debug("In motion loop.")

    motion_detected = None
    logged = False

    try:
        while True:
            if ((motion_detected is not None) and
                (time.time() - motion_detected > options.image_delay_seconds)):
                # capture the current image and write it out
                logger.debug("Motion detected at %s, and > %.1f sec has passed" %
                      (motion_detected, options.image_delay_seconds))
                frame = cv2.cvtColor(options.picam2.capture_array(), cv2.COLOR_BGR2RGB)
                path = os.path.join(options.image_save_dir, "motion_detected.jpg")
                cv2.imwrite(path, frame)
                return path

            if motion_detected is not None:
                if not logged:
                    logger.debug(f"Motion detected at {motion_detected}, but not in the last 2 seconds.")
                    logged = True
                continue

            # Capture the next frame
            frame = options.picam2.capture_array()

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # Calculate the difference between frames
            frame_delta = cv2.absdiff(prev_gray, gray_frame)

            # Display the frame_delta for debugging
            if options.has_display:
                cv2.imshow("Frame Delta", frame_delta)

            # Apply a binary threshold
            _, thresh = cv2.threshold(frame_delta, options.threshold, 255, cv2.THRESH_BINARY)

            # Dilate the threshold image to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)

            contours, _ = cv2.findContours(thresh.copy(),
                                            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Loop through contours and detect motion
            # logger.debug("Found %d contours", len(contours)) # verrrry noisy
            for contour in contours:
                area = cv2.contourArea(contour)
                logger.debug("Contour Area: %s min_area is %s", area, options.min_area)  # Debugging output
                if area < options.min_area:
                    continue

                # Get bounding box for the contour
                (x, y, w, h) = cv2.boundingRect(contour) # pylint: disable=C0103
                # Draw rectangle around detected motion
                logger.debug(f"Motion detected at ({x}, {y}) with width {w} and height {h} area {area}")
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # write out the current cv2 image
                motion_detected = time.time()
                cv2.imwrite(os.path.join(options.image_save_dir, "motion_detected_cv2.jpg"),
                            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Display the frames
            if options.has_display:
                cv2.imshow("RGB Camera feed", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cv2.imshow("Threshold", thresh)

            # Update previous frame
            prev_gray = gray_frame.copy()

            # if don't have this the preview window will show correctly or refresh
            cv2.waitKey(1)

    except KeyboardInterrupt:
        logger.debug("Motion detection interrupted.")

    return None

def detect_motion(options: MotionOptions):
    """
    Detect motion using Raspberry Pi Camera Module and Picamera2.

    This runs detecting motion in a loop, sending an email with an image when
    there is motion. It never returns.

    Args:
        options: MotionOptions object with motion configuration
    """

    email_options = send_email.get_email_config()

    logger.info("Motion detection started.")
    logger.info("  Can display: %s", options.has_display)
    logger.info("  Threshold:   %d", options.threshold)
    logger.info("  Min Area:    %d", options.min_area)

    while True:
        image_path = detect_motion_ai_camera(options)

        send_email.send_email(email_options, image_path)

        # wait before sending another email
        logger.info(f"Sleeping for {options.time_limit_minutes} minutes since just sent an email")
        time.sleep(options.time_limit_minutes*60)

def stop():
    """
    Stop the camera, clean up
    """
    config.picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    config = setup()

    if config is None:
        logger.error('Missing config in motion.ini')
    elif config.picam2 is None:
        logger.error('Camera not initialized')
    else:
        detect_motion(config)

        config.picam2.stop()
