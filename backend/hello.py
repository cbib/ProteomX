#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Credits: Claire Lescoat, Macha Nikolski, Benjamin Dartigues, Cedric Usureau, Aurélien Barré, Hayssam Soueidan
import argparse
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


def get_args():
    example_text = "Usage example: " \
                   "hello.py --name Claire Macha Ben Cedric Aurélien Hayssam"
    parser = argparse.ArgumentParser(epilog=example_text)
    parser.add_argument('--name', nargs='+', required=False, help='A list of names to greet', default=["world"])
    args = parser.parse_args()
    return args


def say_hello(name):
    logger.bind(result={"status": "all right", "target": name, "result": f"hello {name}"}).info(f"This is a message for {name} with extra data")


if __name__ == '__main__':
    args = get_args()
    for n in args.name:
        say_hello(n)
