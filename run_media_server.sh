#!/bin/bash
# Run the media server in the background
nohup python serve_media.py > media_server.log 2>&1 &
echo "Media server started. Check media_server.log for output."
echo "PID: $!"