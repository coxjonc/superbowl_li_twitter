#!/bin/bash

source ~/.virtualenvs/superbowl/bin/activate

until python ~/Dev/superbowl_social/bin/stream_to_sql.py; do
    echo "Stream parser crashed with exit code $?. Respawning..." >&2
    sleep 1
done

