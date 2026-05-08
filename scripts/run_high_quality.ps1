# Helper script to run a high-quality capture on Windows PowerShell
# Adjust resolution and quality variables below if desired.
$resolution = "3280x2464"
$quality = 95
$output = "pasta-pesto"

python -m src.capture_aruco_configured --output-dir $output --resolution $resolution --quality $quality
