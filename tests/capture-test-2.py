#! /usr/bin/env python3
import argparse
import time
from picamera2 import Picamera2
import cv2
import os

def initCamera():
    # Initialize the camera
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    return picam2

# Threshold 200 doesn't work
# 100 works, but slow motion is detected
# 50 works, pretty well
# 25 works
def detect_motion_ai_camera(picam2, threshold=25, min_area=500):
    """
    Detect motion using Raspberry Pi Camera Module and Picamera2.

    Args:
        threshold (int): The threshold for detecting changes between frames.
        min_area (int): Minimum contour area to qualify as motion.
    """
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

    print("Motion detection started.")

    motionDetected = None
    logged = False

    try:
        while True:
            # if (motionDetected is not None) and (time.time() - motionDetected > 2):
            #     # capture the current image and write it out
            #     print(f"Motion detected at {motionDetected}, and > 2 sec has passed")
            #     frame = picam2.capture_array()
            #     cv2.imwrite("motion_images/motion_detected.jpg", frame)
            #     motionDetected = None
            #     logged = False
            #     break
            # elif motionDetected is not None:
            #     if (not logged):
            #         print(f"Motion detected at {motionDetected}, but not in the last 2 seconds.")
            #         logged = True
            #     continue

            # Capture the next frame
            frame = picam2.capture_array()

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # Calculate the difference between frames
            frame_delta = cv2.absdiff(prev_gray, gray_frame)

            # Display the frame_delta for debugging
            if canDisplay:
                cv2.imshow("Frame Delta", frame_delta)

            # Apply a binary threshold
            _, thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)

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
                if area < min_area:
                    continue

                # Get bounding box for the contour
                (x, y, w, h) = cv2.boundingRect(contour)
                # Draw rectangle around detected motion
                print(f"Motion detected at ({x}, {y}) with width {w} and height {h} area {area}")
                rectSet = True
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # write out the current cv2 image
                motionDetected = time.time()
                cv2.imwrite("motion_images/motion_detected_cv2.jpg", frame)

            # Display the frames
            if canDisplay:
                cv2.imshow("RGB Camera feed", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cv2.imshow("Threshold", thresh)

            # Update previous frame
            prev_gray = gray_frame.copy()

            # Break loop on 'q' key press
            # if don't have this the preview window will show correctly or refresh
            cv2.waitKey(1)

    except KeyboardInterrupt:
        print("Motion detection interrupted.")

    # finally:
    #     print(">>>> in finally to stop camera")
    #     picam2.stop()
    #     cv2.destroyAllWindows()

    # print("Motion detection stopped.")
    # picam2.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Motion detection with optional threshold and min_area.")
    parser.add_argument("--threshold", type=int, default=25, help="Threshold value for motion detection.")
    parser.add_argument("--min_area", type=int, default=500, help="Minimum area size for motion detection.")

    args = parser.parse_args()

    picam2 = initCamera()
    for i in range(10):
        print(f"Starting motion detection with threshold: {args.threshold} and min_area: {args.min_area}")
        detect_motion_ai_camera(picam2, args.threshold, args.min_area)
        print("Sleeping for 10 seconds.")
        time.sleep(10)

    picam2.stop()
