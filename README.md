# trolley-tray-capture
OpenCV and Raspberry Pi prototype for ArUco-based tray pose detection and automatic image capture in an airline trolley setup

## Requirements

This project uses the following external Python libraries:

- `opencv-contrib-python` for OpenCV and ArUco marker detection
- `numpy` for array and image handling through OpenCV
- `picamera2` for Raspberry Pi camera access

Install them with:

```bash
pip install -r requirements.txt
```

## Usage

The capture scripts are located in `test_scripts/`.

### 1) Capture when one target marker is detected

```bash
python test_scripts/detect_one_aruco.py
```

Optional arguments:

- `--output-dir` Directory where images are saved (default: current directory)
- `--name` Base filename for captures (default: `single_marker_shot`)
- `--show-expected` If set, also generate and display the expected target ArUco marker (default: off)

Example:

```bash
python test_scripts/detect_one_aruco.py --output-dir captures --name tray_frame --show-expected
```

### 2) Capture when markers 0,1,2,3 are all visible

```bash
python test_scripts/detect_four_aruco.py
```

Optional arguments:

- `--output-dir` Directory where images are saved (default: current directory)
- `--name` Base filename for captures (default: `all_markers_shot`)

Example:

```bash
python test_scripts/detect_four_aruco.py --output-dir captures --name all_visible
```

## Output filenames

Captured images always include a timestamp and are written as:

`<name>_YYYYMMDD_HHMMSS.jpg`

If `--show-expected` is used in `detect_one_aruco.py`, the expected marker image is also saved with timestamp as:

`expected_target_aruco_YYYYMMDD_HHMMSS.png`

