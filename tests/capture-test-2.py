#! /usr/bin/env python3
import argparse
from picamera2 import Picamera2
import cv2
import numpy as np
import os


# 200 doesn't work
# 100 works, but slow motion is detected
# 50 works, pretty well
# 25 works
def detect_motion_ai_camera(threshold=25, min_area=500):
    """
    Detect motion using Raspberry Pi Camera Module and Picamera2.

    Args:
        threshold (int): The threshold for detecting changes between frames.
        min_area (int): Minimum contour area to qualify as motion.
    """
    # Initialize the camera
    picam2 = Picamera2()
    # config = picam2.create_preview_configuration(main={"size": (640, 480)})
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    canDisplay = os.environ.get("DISPLAY") is not None
    print("started.")
    print(f"  Can display: {canDisplay}")
    print(f"  Threshold:   {threshold}")
    print(f"  Min Area:    {min_area}")

    # Capture the first frame
    frame = picam2.capture_array()
    print("Captured array")
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    print("Motion detection started. Press 'q' to quit.")

    try:
        while True:
            # Capture the next frame
            # print("About to capture array")
            frame = picam2.capture_array()
            # print("Captured array")
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # print("about to do diff")
            # Calculate the difference between frames
            frame_delta = cv2.absdiff(prev_gray, gray_frame)

            # Display the frame_delta for debugging
            if canDisplay:
                cv2.imshow("Frame Delta", frame_delta)

            # print("about to do threashold")
            # Apply a binary threshold
            _, thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)

            # print("about to do dilate")
            # Dilate the threshold image to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)

            # print("about to do findCoutours")
            # Find contours
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            rectSet = False
            # Loop through contours and detect motion
            # print(f"Found {len(contours)} contours")
            for contour in contours:
                area = cv2.contourArea(contour)
                # print(f"Contour Area: {area} min_area is {min_area}")  # Debugging output
                if area < min_area:
                    continue

                # Get bounding box for the contour
                (x, y, w, h) = cv2.boundingRect(contour)
                # Draw rectangle around detected motion
                print(f"Motion detected at ({x}, {y}) with width {w} and height {h}")
                rectSet = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # if not rectSet:
                # print("No motion detected.")
                # continue

            # Display the frames
            if canDisplay:
                cv2.imshow("Camera Feed", frame)
                cv2.imshow("Threshold", thresh)

            # Prompt user to press a key before continuing
            # input("Press any key to continue...")

            # Update previous frame
            prev_gray = gray_frame.copy()

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Motion detection interrupted.")

    finally:
        print(">>>> in finally")
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motion detection with optional threshold and min_area.")
    parser.add_argument("--threshold", type=int, default=25, help="Threshold value for motion detection.")
    parser.add_argument("--min_area", type=int, default=500, help="Minimum area size for motion detection.")
    
    args = parser.parse_args()
    detect_motion_ai_camera(args.threshold, args.min_area)
