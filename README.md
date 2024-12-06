# Pet Watcher for the Raspberry Pi

This is a Python app that can be used to watch for movement and send an image of the movement. It was specifically designed for watching a pet while we're away, but can be adapted for other uses.

I poked around on the we at examples, and thought I'd let AI have a shot. I started by asking ChatGPT this

```text
Create an application for the raspberry pi that uses a camera and when it detects movement  sends an email to me, if one hasn't been sent within the last hour
```

It did _pretty_ well. The basics were there, but it used `picamera` instead of `picamera2`. After telling it to use that, it was pretty close, and only took an hour or so to get things working. One issue I found that running it in an SSH prompt would break the connection. (As when running in VSCode Remoting). I found it would work ok, if run in the background.

```bash
python3 pet-watcher.py &
```

## Running

This sends email via SMTP to Gmail for now. These environment variables must be set to be able to send emails.

```bash
export mail_appKey=...
export mail_username=...
export mail_to=...
```

## One-time Setup

```bash
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt install -y python3-picamera2 --no-install-recommends # no GUI dependencies
```

## Links

- [PiCamera2 Manual (pdf)](https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf)
- [OpenCV 4.10 doc](https://docs.opencv.org/4.10.0/)