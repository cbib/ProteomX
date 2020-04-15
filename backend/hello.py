#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan
import sys
import uuid

from loguru import logger

config = {
    "handlers": [
        {"sink": sys.stdout, "serialize": True},
        {"sink": "file.log", "serialize": True},
    ],
    "extra": {"job_uuid": uuid.uuid4()}
}
logger.configure(**config)
if __name__ == '__main__':
    logger.info("Hello world")
    logger.info("This is another message")
    logger.error("This is an error!")
    logger.bind(result={"status": "all right"}).info("This is a message with extra data")
