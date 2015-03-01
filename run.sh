#!/bin/bash

until python3 src/grasia.py; do
    echo "GrasiaABot crashed with exit code $?.  Respawning..." >&2
    sleep 1
done

