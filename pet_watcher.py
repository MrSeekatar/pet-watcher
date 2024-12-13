#!/usr/bin/env python3
"""
This is the main script for the pet-watcher project.
"""
import logging
import logging.config

import detect_motion_3 as detect_motion

logger = logging.getLogger("detector")
logger.setLevel(logging.DEBUG)

# Create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)  # Set to DEBUG to capture all messages

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)

config = detect_motion.setup()

if config is None:
    logger.error('Missing config in motion.ini')
elif config.picam2 is None:
    logger.error('Camera not initialized')
else:
    detect_motion.detect_motion(config)
