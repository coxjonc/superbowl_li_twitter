#!/bin/bash

source ~/.virtualenvs/superbowl/bin/activate

until python ~/Dev/superbowl_social/bin/stream_to_sql.py; do
    sleep 1
done
