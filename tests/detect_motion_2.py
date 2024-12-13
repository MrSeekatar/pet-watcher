import cv2
import os
from datetime import datetime

from send_email import send_email
def setup_camera():
    pass

def detect_motion(last_email_time, CONTOUR_THRESHOLD, IMAGE_SAVE_DIR, CHECK_INTERVAL, TIME_LIMIT):
    os.environ["GST_DEBUG"] = "3"
    pipeline = "v4l2src device=/dev/video0 ! videoconvert ! appsink"
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)
    # cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    first_frame = None

    print("Starting detecting")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Breaking since cap.read() returned False")
            break

        print("converting")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        print("diffing")
        # Compute difference and threshold
        frame_diff = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        print("finding contours")
        # Find contours
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < CONTOUR_THRESHOLD:  # Ignore small movements, larger less sensitive
                continue

            # Save the frame as an image
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            image_path = os.path.join(IMAGE_SAVE_DIR, f"motion_{timestamp}.jpg")
            cv2.imwrite(image_path, frame)
            print(f"Motion detected. Image saved to {image_path}")

            # Send email with the image
            # Check if enough time has passed since the last email
            if last_email_time is None or datetime.now() - last_email_time > TIME_LIMIT:
                print(f"Sending email since {datetime.now()} - {last_email_time} > {TIME_LIMIT}")
                send_email(image_path)
                last_email_time = datetime.now()
            else:
                print(f"Not sending email since {datetime.now()} - {last_email_time} <= {TIME_LIMIT}")

            # Update first frame to avoid repeated detection
            first_frame = None
            break

        # Show the frame
        # cv2.imshow('Motion Detection', frame)

        # key = cv2.waitKey(1)
        # if key == 27:  # ESC key to exit
        #     break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_motion()
