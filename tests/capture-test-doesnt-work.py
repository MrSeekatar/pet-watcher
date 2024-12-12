import cv2
import numpy as np

def detect_motion_ai_camera(camera_index=0, threshold=25, min_area=500):
    """
    Couldn't get this to work on the Pi
    """
    # Initialize the video capture object
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return

    # Read the first frame and convert it to grayscale
    _, prev_frame = cap.read()
    prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_gray = cv2.GaussianBlur(prev_gray, (21, 21), 0)

    print("Motion detection started. Press 'q' to quit.")

    try:
        while True:
            # Capture the next frame
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Convert the frame to grayscale
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

            # Calculate the difference between current and previous frames
            frame_delta = cv2.absdiff(prev_gray, gray_frame)

            # Display the frame_delta for debugging
            cv2.imshow("Frame Delta", frame_delta)

            # Apply a binary threshold
            _, thresh = cv2.threshold(frame_delta, threshold, 255, cv2.THRESH_BINARY)

            # Dilate the threshold image to fill in holes
            thresh = cv2.dilate(thresh, None, iterations=2)

            # Display the threshold for debugging
            cv2.imshow("Threshold", thresh)

            # Find contours
            contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            print(f"Detected {len(contours)} contours")  # Debugging output

            # Loop through contours and detect motion
            for contour in contours:
                area = cv2.contourArea(contour)
                print(f"Contour Area: {area}")  # Debugging output
                if area < min_area:
                    continue

                # Get bounding box for the contour
                (x, y, w, h) = cv2.boundingRect(contour)
                # Draw rectangle around detected motion
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Display the frames
            cv2.imshow("Camera Feed", frame)

            # Update previous frame
            prev_gray = gray_frame.copy()

            # Break loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("Motion detection interrupted.")

    finally:
        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_motion_ai_camera()
