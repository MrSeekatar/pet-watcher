# Pet Watcher for the Raspberry Pi

This is a Python app that can be used to watch for movement and send an image of the movement. It was specifically designed for watching a pet while we're away, but can be adapted for other uses.

I poked around on the we at examples, and thought I'd let AI have a shot. I started by asking ChatGPT this

```text
Create an application for the raspberry pi that uses a camera and when it detects movement  sends an email to me, if one hasn't been sent within the last hour
```

It did _pretty_ well. The basics were there, but it used `picamera` instead of `picamera2`. After telling it to use that, it was pretty close, and only took an hour or so to get things working.

When running on a 3B with no UI, I found that running it in an SSH prompt would break the connection. (As when running in VSCode Remoting). I found it would work ok, if run in the background.

```bash
python3 pet-watcher.py &
```

I bought a 5B that came with the OS installed with the UI and it ran better. I bought a new AI camera, too, and didn't get the false movements I got so many times on the 3B with an older camera.

## Configuration

`motion.ini` has settings to control the capture of motion from the camera and frequency of sending. It is included in the repo with default values.

`email.ini` has settings for sending emails and is not included in the repo since it includes secrets. Here's a sample file

```text
[email]
username = ...
password = ...
to = ...

; default values
;from_email = Cat Watcher
;smtp_server = smtp.gmail.com
;smtp_port = 587
;subject = Motion Detected
;message = Motion has been detected by the Cat Detector Van.
```

## Running



## One-time Setup

```bash
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt install -y python3-picamera2 --no-install-recommends # no GUI dependencies
```

## Links

- [PiCamera2 Manual (pdf)](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [OpenCV 4.10 doc](https://docs.opencv.org/4.10.0/)
