# Pet Watcher for the Raspberry Pi

This is a Raspberry Pi Python app that can be used to watch for movement and send an image of the movement. It was specifically designed for watching a pet while we're away, but can be adapted for other uses.

I poked around on the web for examples, and thought I'd let AI have a shot. I started by asking ChatGPT this

```text
Create an application for the raspberry pi that uses a camera and when it detects movement  sends an email to me, if one hasn't been sent within the last hour
```

It did _pretty_ well. The basics were there, but it used `picamera` instead of `picamera2`. After telling it to use that, it was pretty close, and only took an hour or so to get things working.

When running on a 3B with no UI, I found that running it in an SSH prompt would break the connection. (As when running in VSCode Remoting). I found it would work ok, if run in the background.

```bash
python3 pet-watcher.py &
```

I bought a 5B that came with the OS installed with the UI and it ran better. I bought a new AI camera, too, and didn't get the false movements I got so many times on the 3B with an older (1.3) camera. The next version will use the AI Camera to detect a cat.

## Configuration

`motion.ini` has settings to control the capture of motion from the camera and frequency of sending. It is included in the repo with default values. See that file for details about each setting.

`email.ini` has settings for sending emails and is not included in the repo since it includes secrets. Here's a sample file

```text
[email]
; credentials for SMTP server
username = ...
password = ...
; who to send it to. Comma separated list.
to = ...

; default values
;from_email = Cat Watcher
;smtp_server = smtp.gmail.com
;smtp_port = 587
;subject = Motion Detected
;message = Motion has been detected by the Raspberry Pi!
```

## Running

To run in the forground use this. If you are in a GUI, it will show the images on the screen when it is detecting motion.

```bash
python3 pet_watcher.py
```

To run on boot, one method is to add this to `/etc/rc.local`, adjusting folder as needed.

```bash
(cd /home/pi/pet-watcher && python3 pet_watcher.py > log.txt 2>&1) &
```
## Testing Motion Capture

The code in [tests/capture-test-2.py](tests/capture-test-2.py) in the similar code to the final version. You can run this in the UI and it will show three windows of the images used to detect motion, and green rectangles will be around the areas it detects.

## One-time Setup

These were run to use the camera on a fresh OS install

```bash
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt install -y python3-picamera2
```

## ChatGPT's Explanation of Motion Detection

This is how ChatGPT explains how the motion detection works

>The provided code detects motion when there is a significant change between two consecutive frames captured by the camera. Here's how motion detection works in the code:
>
>1. Frame Comparison:
>
>    - Each frame from the video feed is converted to grayscale and blurred to reduce noise.
>    - The current frame is compared to the previous frame using the cv2.absdiff() function, which calculates the absolute difference between the pixel values of the two frames. This highlights areas where there is a change in the scene (potential motion).
>1. Thresholding:
>
>    - A binary threshold is applied to the difference image (frame_delta) using cv2.threshold(). This step converts the difference image into a binary image, where pixel values above the threshold are set to 255 (white) and others are set to 0 (black). The threshold argument determines the sensitivity to motion.
>1. Dilating the Image:
>
>    - The thresholded image is dilated using cv2.dilate() to fill in small gaps and make the areas of detected motion more prominent.
>
>1. Contour Detection:
>
>    - The cv2.findContours() function is used to find the contours of white regions in the thresholded image. Each contour represents a distinct area where motion is detected.
>1. Motion Detection Criteria:
>
>    - The area of each contour is calculated using cv2.contourArea(). If the area is below the min_area threshold, the contour is ignored (to filter out small or insignificant movements, such as noise).
>    - If the contour's area is above min_area, it is considered as motion, and a bounding box is drawn around it on the frame using cv2.rectangle().
>
>1. Visualization:
>
>    - The live camera feed and the thresholded difference image are displayed in real-time. Detected motion is highlighted with bounding boxes in the live feed.
>
### Key Points of Motion Detection:

  - Motion is detected only if there is a significant pixel difference between two consecutive frames, and the detected change is larger than the specified min_area.
  - The parameters threshold and min_area can be tuned to control the sensitivity and avoid false positives (e.g., caused by small environmental changes like flickering lights).

For example:

  - A small moving object might not trigger motion detection if min_area is too high.
  - A very slight change in brightness might trigger motion detection if threshold is too low.

## Links

### Python

- [Logging](https://docs.python.org/3/library/logging.html)

### Camera

- [RPi Blog about release of 1.3 Camera](https://www.raspberrypi.com/news/camera-board-available-for-sale/)
- [PiCamera2 Manual (pdf)](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [Camera Documenation](https://www.raspberrypi.com/documentation/accessories/camera.html)
- [OpenCV 4.10 doc](https://docs.opencv.org/4.10.0/)
- [AI Camera Documentation](https://www.raspberrypi.com/documentation/accessories/ai-camera.html)
