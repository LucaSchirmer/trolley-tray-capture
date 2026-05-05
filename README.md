# trolley-tray-capture
OpenCV and Raspberry Pi prototype for ArUco-based tray pose detection and automatic image capture in an airline trolley setup.

## Requirements

This project uses the following external Python libraries:

- `opencv-contrib-python` for OpenCV and ArUco marker detection
- `numpy` for array and image handling through OpenCV
- `picamera2` for Raspberry Pi camera access

Install them with:

```bash
pip install -r requirements.txt
```

## Project structure

- `test_scripts/` contains prototype and quick test scripts.
- `src/` is a Python package containing final scripts and reusable modules.
- `configs/` contains JSON configuration files used by scripts in `src/`.

## Usage

### Final configurable capture script

Use the configurable script in `src/` and select marker IDs in a JSON file:

```bash
python -m src.capture_aruco_configured --config configs/aruco_detection_config.json
```

Optional arguments:

- `--config` Path to the JSON config file
- `--output-dir` Directory where images are saved (default: current directory)
- `--name` Optional filename base override

Edit `configs/aruco_detection_config.json` to choose:

- `aruco_dictionary` (for example `DICT_6X6_250`)
- `required_ids` (the marker IDs that must all be visible)
- output naming and camera/window settings

### Continuous camera preview

Use this when you want a live, endless Pi camera preview on a connected screen:

```bash
python test_scripts/continuous_camera_preview.py
```

Press `q` in the preview window or use `Ctrl+C` to stop it.

### Test scripts

The test capture scripts remain in `test_scripts/`.

### Continuous camera preview

Use this when you want an endless camera view on a connected screen:

```bash
python test_scripts/continuous_camera_preview.py
```

Press `q` in the preview window or use `Ctrl+C` to stop it.

#### 1) Capture when one target marker is detected

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

#### 2) Capture when markers 0,1,2,3 are all visible

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

#### 3) Print every detected ArUco ID

Use this when you want a simple debug view that prints the marker IDs visible in each frame:

```bash
python test_scripts/detect_aruco_ids.py
```

Optional arguments:

- `--config` Path to the JSON config file (default: `configs/aruco_detection_config.json`)

This script uses the configured dictionary from the JSON file, draws detected markers in the preview window, and prints lines like `Detected IDs: [0, 3]` or `No marker detected`.

## Output filenames

Captured images always include a timestamp and are written as:

`<name>_YYYYMMDD_HHMMSS.jpg`

If `--show-expected` is used in `detect_one_aruco.py`, the expected marker image is also saved with timestamp as:

`expected_target_aruco_YYYYMMDD_HHMMSS.png`

## Notes

- The final script reads marker configuration from `configs/aruco_detection_config.json`.
- Run the package entry point with `python -m src.capture_aruco_configured` so imports resolve cleanly.

