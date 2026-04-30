"""Config loader utilities for ArUco capture scripts."""

import json
import os
import cv2


def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)

    required_fields = [
        "aruco_dictionary",
        "required_ids",
        "default_output_basename",
        "camera_warmup_seconds",
        "window_name",
    ]

    missing = [field for field in required_fields if field not in config]
    if missing:
        raise ValueError(f"Missing config fields: {', '.join(missing)}")

    if not isinstance(config["required_ids"], list) or not config["required_ids"]:
        raise ValueError("required_ids must be a non-empty list of integers")

    return config


def resolve_dictionary(dictionary_name: str):
    if not hasattr(cv2.aruco, dictionary_name):
        raise ValueError(
            f"Unknown ArUco dictionary '{dictionary_name}'. Use a valid cv2.aruco.DICT_* name."
        )
    return getattr(cv2.aruco, dictionary_name)
