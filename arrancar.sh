#!/bin/bash
cd "$(dirname "$0")"
source .venv/bin/activate
python video_loop.py &
VIDEO_PID=$!
trap "kill $VIDEO_PID 2>/dev/null" EXIT
python app.py
