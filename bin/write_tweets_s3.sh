#!/bin/bash

source ~/.bashrc
source ~/.virtualenvs/superbowl/bin/activate
source ~/.virtualenvs/superbowl/bin/postactivate

~/.virtualenvs/superbowl/bin/python ~/Dev/superbowl_social/bin/sql_to_s3.py

