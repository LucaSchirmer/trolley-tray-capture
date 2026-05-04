#!/usr/bin/env python3
"""
Arrange existing ArUco PNG marker images onto 2 printable A4 pages.

The script scans a folder for files like:
  aruco_DICT_4X4_50_id000_531px.png
and places them on exactly two A4 pages, centered and evenly spaced.

Best for your workflow when the individual marker PNGs already exist.
"""

import argparse
import math
import re
from pathlib import Path

import cv2
import numpy as np

MM_PER_INCH = 25.4
A4_MM = (210.0, 297.0)

FILENAME_RE = re.compile(r'^aruco_(DICT_[A-Z0-9_]+)_id(\d+)_(\d+)px\.png$', re.IGNORECASE)


def mm_to_px(mm: float, dpi: int) -> int:
    return max(1, round(mm / MM_PER_INCH * dpi))


def make_a4_canvas(dpi: int):
    w_px = mm_to_px(A4_MM[0], dpi)
    h_px = mm_to_px(A4_MM[1], dpi)
    return np.full((h_px, w_px), 255, dtype=np.uint8), w_px, h_px


def parse_marker_file(path: Path):
    m = FILENAME_RE.match(path.name)
    if not m:
        return None
    dict_name, marker_id, px = m.group(1), int(m.group(2)), int(m.group(3))
    return {
        'path': path,
        'dict': dict_name,
        'id': marker_id,
        'px': px,
    }


def load_marker_files(folder: Path):
    files = []
    for p in sorted(folder.glob('*.png')):
        meta = parse_marker_file(p)
        if meta is not None:
            files.append(meta)
    return files


def split_two_pages(items):
    mid = math.ceil(len(items) / 2)
    return items[:mid], items[mid:]


def choose_grid(n):
    if n <= 1:
        return 1, 1
    if n == 2:
        return 1, 2
    if n <= 4:
        return 2, 2
    if n <= 6:
        return 2, 3
    if n <= 9:
        return 3, 3
    if n <= 12:
        return 3, 4
    return 4, math.ceil(n / 4)


def render_page(page_items, page_no, outdir: Path, dpi: int, margin_mm: float, gap_mm: float, label_mm: float, title: str):
    canvas, page_w, page_h = make_a4_canvas(dpi)
    margin = mm_to_px(margin_mm, dpi)
    gap = mm_to_px(gap_mm, dpi)
    label_h = mm_to_px(label_mm, dpi)
    cols, rows = choose_grid(len(page_items))

    usable_w = page_w - 2 * margin - gap * (cols - 1)
    usable_h = page_h - 2 * margin - gap * (rows - 1) - label_h * rows - mm_to_px(10, dpi)
    cell_w = usable_w // cols
    cell_h = usable_h // rows
    marker_side = min(cell_w, cell_h)

    x_total = cols * marker_side + (cols - 1) * gap
    y_total = rows * (marker_side + label_h) + (rows - 1) * gap
    x0 = (page_w - x_total) // 2
    y0 = (page_h - y_total) // 2 + mm_to_px(5, dpi)

    font = cv2.FONT_HERSHEY_SIMPLEX
    header = f'{title} | Page {page_no} | {len(page_items)} markers | A4 {dpi} dpi'
    cv2.putText(canvas, header, (margin, max(30, margin)), font, 0.6, 0, 2, cv2.LINE_AA)

    for idx, item in enumerate(page_items):
        r = idx // cols
        c = idx % cols
        x = x0 + c * (marker_side + gap)
        y = y0 + r * (marker_side + label_h + gap)

        img = cv2.imread(str(item['path']), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        resized = cv2.resize(img, (marker_side, marker_side), interpolation=cv2.INTER_NEAREST)
        canvas[y:y + marker_side, x:x + marker_side] = resized

        label = f"{item['dict']} | id={item['id']}"
        cv2.putText(canvas, label, (x, y + marker_side + max(18, label_h - 8)), font, 0.5, 0, 1, cv2.LINE_AA)

    out_path = outdir / f'aruco_existing_sheet_p{page_no:02d}_{dpi}dpi.png'
    cv2.imwrite(str(out_path), canvas)
    return out_path


def main():
    parser = argparse.ArgumentParser(description='Ordnet bestehende ArUco-PNGs auf genau 2 A4-Druckseiten an')
    parser.add_argument('--input-dir', default='ArUco-images', help='Ordner mit vorhandenen Einzelmarker-PNGs')
    parser.add_argument('--output-dir', default='ArUco-images', help='Zielordner fuer die erzeugten Seiten')
    parser.add_argument('--dpi', type=int, default=300, help='DPI der A4-Ausgabe')
    parser.add_argument('--margin-mm', type=float, default=12.0, help='Seitenrand')
    parser.add_argument('--gap-mm', type=float, default=10.0, help='Abstand zwischen Markern')
    parser.add_argument('--label-mm', type=float, default=8.0, help='Beschriftungsbereich unter jedem Marker')
    parser.add_argument('--dict-filter', default=None, help='Optional, z. B. DICT_4X4_50')
    parser.add_argument('--show', action='store_true', help='Zeigt beide Seiten nacheinander an')
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    items = load_marker_files(input_dir)
    if args.dict_filter:
        items = [x for x in items if x['dict'] == args.dict_filter]

    items = sorted(items, key=lambda x: (x['dict'], x['id'], x['px']))

    if not items:
        raise SystemExit('Keine passenden Einzelmarker gefunden. Erwartet werden Dateien wie aruco_DICT_4X4_50_id000_531px.png')

    page1, page2 = split_two_pages(items)
    title = args.dict_filter if args.dict_filter else 'Existing ArUco markers'

    out1 = render_page(page1, 1, output_dir, args.dpi, args.margin_mm, args.gap_mm, args.label_mm, title)
    print(f'Gespeichert: {out1}')

    if page2:
        out2 = render_page(page2, 2, output_dir, args.dpi, args.margin_mm, args.gap_mm, args.label_mm, title)
        print(f'Gespeichert: {out2}')
    else:
        out2 = None

    if args.show:
        for page_path in [out1, out2]:
            if page_path is None:
                continue
            img = cv2.imread(str(page_path), cv2.IMREAD_GRAYSCALE)
            preview = img.copy()
            max_w = 1200
            if preview.shape[1] > max_w:
                scale = max_w / preview.shape[1]
                preview = cv2.resize(preview, (int(preview.shape[1] * scale), int(preview.shape[0] * scale)))
            cv2.imshow(page_path.name, preview)
            key = cv2.waitKey(0)
            cv2.destroyWindow(page_path.name)
            if key in (27, ord('q')):
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
