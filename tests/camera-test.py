# example from the PiCamera pdf, to take a photo
import os
from picamera2 import Picamera2, Preview

picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
picam2.configure(camera_config)
if (os.environ.get("DISPLAY") is not None):
    picam2.start_preview(Preview.DRM)
picam2.start()
picam2.capture_file("test.jpg")
print("Image written to test.jpg")