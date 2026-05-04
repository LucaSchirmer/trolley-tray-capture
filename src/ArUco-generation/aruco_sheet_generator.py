#!/usr/bin/env python3
"""
Aruco marker sheet generator for printing and later detection.

Features:
- Generates one or more classic OpenCV ArUco markers
- Packs as many markers as possible onto A4 pages
- Optional preview of pages one after another
- Saves PNG pages and individual marker PNGs with clear filenames
- Prints a detection reference table (dictionary + id + physical size)

Example:
python aruco_sheet_generator.py --dict DICT_4X4_50 --ids 0-11 --marker-mm 45 --show
"""

import argparse
import math
import os
from pathlib import Path

import cv2
import numpy as np

MM_PER_INCH = 25.4
A4_MM = (210.0, 297.0)
DEFAULT_DPI = 300

ARUCO_DICTS = {
    name: getattr(cv2.aruco, name)
    for name in dir(cv2.aruco)
    if name.startswith('DICT_')
}


def parse_ids(spec: str):
    ids = []
    for chunk in spec.split(','):
        chunk = chunk.strip()
        if not chunk:
            continue
        if '-' in chunk:
            a, b = chunk.split('-', 1)
            start, end = int(a), int(b)
            if end < start:
                raise ValueError(f'Ungueltiger ID-Bereich: {chunk}')
            ids.extend(range(start, end + 1))
        else:
            ids.append(int(chunk))
    result = []
    seen = set()
    for i in ids:
        if i not in seen:
            result.append(i)
            seen.add(i)
    return result


def mm_to_px(mm: float, dpi: int) -> int:
    return max(1, round(mm / MM_PER_INCH * dpi))


def px_to_mm(px: int, dpi: int) -> float:
    return px * MM_PER_INCH / dpi


def get_dictionary(dict_name: str):
    if dict_name not in ARUCO_DICTS:
        raise ValueError(f'Unbekanntes Dictionary: {dict_name}')
    return cv2.aruco.getPredefinedDictionary(ARUCO_DICTS[dict_name])


def generate_marker(dict_name: str, marker_id: int, side_px: int, border_bits: int):
    dictionary = get_dictionary(dict_name)
    marker = np.zeros((side_px, side_px), dtype=np.uint8)
    cv2.aruco.generateImageMarker(dictionary, marker_id, side_px, marker, border_bits)
    return marker


def make_a4_canvas(dpi: int):
    w_px = mm_to_px(A4_MM[0], dpi)
    h_px = mm_to_px(A4_MM[1], dpi)
    canvas = np.full((h_px, w_px), 255, dtype=np.uint8)
    return canvas, w_px, h_px


def render_page(marker_images, ids, dict_name, marker_mm, dpi, margin_mm, gap_mm, label_height_mm, page_idx):
    canvas, page_w_px, page_h_px = make_a4_canvas(dpi)
    margin_px = mm_to_px(margin_mm, dpi)
    gap_px = mm_to_px(gap_mm, dpi)
    label_h_px = mm_to_px(label_height_mm, dpi)
    cell_marker_px = marker_images[0].shape[0]
    cell_w = cell_marker_px
    cell_h = cell_marker_px + label_h_px

    cols = max(1, (page_w_px - 2 * margin_px + gap_px) // (cell_w + gap_px))
    rows = max(1, (page_h_px - 2 * margin_px + gap_px) // (cell_h + gap_px))
    capacity = cols * rows

    font = cv2.FONT_HERSHEY_SIMPLEX

    for idx, (marker_img, marker_id) in enumerate(zip(marker_images, ids)):
        row = idx // cols
        col = idx % cols
        x = margin_px + col * (cell_w + gap_px)
        y = margin_px + row * (cell_h + gap_px)
        canvas[y:y + cell_marker_px, x:x + cell_marker_px] = marker_img

        label = f'{dict_name} | id={marker_id} | {marker_mm:.0f}mm'
        label_y = y + cell_marker_px + max(18, label_h_px - 10)
        cv2.putText(canvas, label, (x, label_y), font, 0.45, 0, 1, cv2.LINE_AA)

    header = f'Aruco page {page_idx} | {dict_name} | marker={marker_mm:.0f}mm | dpi={dpi}'
    cv2.putText(canvas, header, (margin_px, max(24, margin_px // 2 + 12)), font, 0.6, 0, 2, cv2.LINE_AA)

    return canvas, capacity, cols, rows


def plan_capacity(dpi: int, marker_mm: float, margin_mm: float, gap_mm: float, label_height_mm: float):
    canvas, page_w_px, page_h_px = make_a4_canvas(dpi)
    marker_px = mm_to_px(marker_mm, dpi)
    margin_px = mm_to_px(margin_mm, dpi)
    gap_px = mm_to_px(gap_mm, dpi)
    label_h_px = mm_to_px(label_height_mm, dpi)
    cell_w = marker_px
    cell_h = marker_px + label_h_px
    cols = max(1, (page_w_px - 2 * margin_px + gap_px) // (cell_w + gap_px))
    rows = max(1, (page_h_px - 2 * margin_px + gap_px) // (cell_h + gap_px))
    return cols * rows, cols, rows, marker_px


def recommend_marker_mm(distance_cm: float):
    if distance_cm <= 60:
        return 35.0
    if distance_cm <= 90:
        return 45.0
    if distance_cm <= 120:
        return 60.0
    return 80.0


def save_marker_png(outdir: Path, dict_name: str, marker_id: int, side_px: int, marker_img):
    path = outdir / f'aruco_{dict_name}_id{marker_id:03d}_{side_px}px.png'
    cv2.imwrite(str(path), marker_img)
    return path


def save_page_png(outdir: Path, dict_name: str, page_idx: int, dpi: int, marker_mm: float, page_img):
    path = outdir / f'aruco_sheet_{dict_name}_p{page_idx:02d}_{marker_mm:.0f}mm_{dpi}dpi.png'
    cv2.imwrite(str(path), page_img)
    return path


def build_parser():
    parser = argparse.ArgumentParser(description='A4-ArUco-Generator fuer Druck und spaetere Detection')
    parser.add_argument('--dict', default='DICT_4X4_50', choices=sorted(ARUCO_DICTS.keys()), help='OpenCV ArUco Dictionary')
    parser.add_argument('--ids', default='0-11', help='IDs, z. B. 0-3 oder 0,1,2,7')
    parser.add_argument('--marker-mm', type=float, default=None, help='Physische Marker-Kantenlaenge in mm')
    parser.add_argument('--distance-cm', type=float, default=90.0, help='Typische Kameraentfernung in cm fuer Empfehlung')
    parser.add_argument('--dpi', type=int, default=DEFAULT_DPI, help='Druckaufloesung')
    parser.add_argument('--border-bits', type=int, default=1, help='ArUco borderBits')
    parser.add_argument('--margin-mm', type=float, default=10.0, help='Seitenrand auf A4')
    parser.add_argument('--gap-mm', type=float, default=8.0, help='Abstand zwischen Markern')
    parser.add_argument('--label-height-mm', type=float, default=8.0, help='Hoehe fuer Textlabel unter jedem Marker')
    parser.add_argument('--outdir', default='ArUco-images', help='Zielordner')
    parser.add_argument('--show', action='store_true', help='Zeigt Seiten nacheinander an')
    parser.add_argument('--save-individual', action='store_true', help='Speichert Einzelmarker-PNGs zusaetzlich')
    parser.add_argument('--start-small', action='store_true', help='Erzeugt zusaetzlich einen kleinen Testlauf mit 4X4_50, 35mm, falls du experimentieren willst')
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    ids = parse_ids(args.ids)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    marker_mm = args.marker_mm if args.marker_mm is not None else recommend_marker_mm(args.distance_cm)
    capacity, cols, rows, marker_px = plan_capacity(args.dpi, marker_mm, args.margin_mm, args.gap_mm, args.label_height_mm)

    print('=== ArUco Druck-Plan ===')
    print(f'Dictionary        : {args.dict}')
    print(f'IDs               : {ids}')
    print(f'Marker size       : {marker_mm:.1f} mm')
    print(f'Empf. Distanz     : {args.distance_cm:.1f} cm')
    print(f'DPI               : {args.dpi}')
    print(f'Marker pixel      : {marker_px}px')
    print(f'A4 capacity/page  : {capacity} Marker ({cols} Spalten x {rows} Reihen)')
    print(f'Output folder     : {outdir.resolve()}')
    print('')
    print('Detection-Referenz:')
    for marker_id in ids:
        print(f'  - dict={args.dict}, id={marker_id}, marker_length_mm={marker_mm:.1f}')

    all_page_paths = []
    for start in range(0, len(ids), capacity):
        subset = ids[start:start + capacity]
        marker_images = [generate_marker(args.dict, marker_id, marker_px, args.border_bits) for marker_id in subset]

        if args.save_individual:
            for marker_id, marker_img in zip(subset, marker_images):
                save_marker_png(outdir, args.dict, marker_id, marker_px, marker_img)

        page_idx = start // capacity + 1
        page_img, _, _, _ = render_page(marker_images, subset, args.dict, marker_mm, args.dpi, args.margin_mm, args.gap_mm, args.label_height_mm, page_idx)
        page_path = save_page_png(outdir, args.dict, page_idx, args.dpi, marker_mm, page_img)
        all_page_paths.append(page_path)

        if args.show:
            preview = page_img.copy()
            max_w = 1200
            if preview.shape[1] > max_w:
                scale = max_w / preview.shape[1]
                preview = cv2.resize(preview, (int(preview.shape[1] * scale), int(preview.shape[0] * scale)))
            cv2.imshow(f'Aruco Sheet {page_idx}', preview)
            key = cv2.waitKey(0)
            cv2.destroyWindow(f'Aruco Sheet {page_idx}')
            if key in (27, ord('q')):
                break

    if args.start_small:
        test_mm = 35.0
        test_dict = 'DICT_4X4_50'
        test_ids = [0, 1, 2, 3]
        _, _, _, test_px = plan_capacity(args.dpi, test_mm, args.margin_mm, args.gap_mm, args.label_height_mm)
        test_imgs = [generate_marker(test_dict, marker_id, test_px, args.border_bits) for marker_id in test_ids]
        page_img, _, _, _ = render_page(test_imgs, test_ids, test_dict, test_mm, args.dpi, args.margin_mm, args.gap_mm, args.label_height_mm, 1)
        save_page_png(outdir, test_dict, 1, args.dpi, test_mm, page_img)

    if args.show:
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
