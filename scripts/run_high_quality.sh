#!/usr/bin/env sh
# Helper script to run a high-quality capture
RESOLUTION="3280x2464"
QUALITY="95"
OUTPUT="pasta-pesto"

python -m src.capture_aruco_configured --output-dir "$OUTPUT" --resolution "$RESOLUTION" --quality "$QUALITY"
