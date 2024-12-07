import cv2

print(cv2.getBuildInformation())

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open video capture")
else:
    print("Camera opened successfully")

cap.release()