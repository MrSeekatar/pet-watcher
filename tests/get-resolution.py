from picamera2 import Picamera2

# Initialize the Picamera2 object
picam2 = Picamera2()

# List all available modes
camera_modes = picam2.sensor_modes
print("Supported resolutions:")
for mode in camera_modes:
    resolution = mode["size"]
    print(f"{resolution[0]}x{resolution[1]}")