#!/usr/bin/python

# Standard lib imports
import logging
import os
import time
import re

# Third-party imports
import MySQLdb
from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine
import pandas as pd

# Constants
DATABASE_URL = os.environ.get('DATABASE_URL')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

class TweetHandler(object):
    """
    Update columns in , outputs it as a CSV, and copies our data
    to AWS S3
    """
    def __init__(self, url):
        logging.debug('Attempting to connect to MySQL database...')
