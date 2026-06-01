from pathlib import Path
import argparse

import cv2
import numpy as np


# ============================================================
# BEGINNER SETTINGS
# ============================================================
# If you only want to run the sample image, do not change anything.
# Just run: py main.py
#
# If you want to try another image later, change IMAGE_PATH.
# If the result is bad, the first thing to change is MANUAL_CROP.
# ============================================================

IMAGE_PATH = Path("sample_inputs/physical_front_view_1.jpeg")
OUTPUT_DIR = Path("results")

# Use this if the script is looking at too much empty paper.
# Format: (x1, y1, x2, y2)
# This default crop is chosen for the bundled sample image.
# If you change to a new image later, you may need to change this too.
MANUAL_CROP = (0, 1780, 2698, 2320)

# If MANUAL_CROP is None, the script keeps only the lower part of the image.
BOTTOM_START_RATIO = 0.55


# 6-dot Braille order:
# 1 4
# 2 5
# 3 6
PATTERN_TO_CHAR = {
    (1, 0, 0, 0, 0, 0): "a",
    (1, 1, 0, 0, 0, 0): "b",
    (1, 0, 0, 1, 0, 0): "c",
    (1, 0, 0, 1, 1, 0): "d",
    (1, 0, 0, 0, 1, 0): "e",
    (1, 1, 0, 1, 0, 0): "f",
    (1, 1, 0, 1, 1, 0): "g",
    (1, 1, 0, 0, 1, 0): "h",
    (0, 1, 0, 1, 0, 0): "i",
    (0, 1, 0, 1, 1, 0): "j",
    (1, 0, 1, 0, 0, 0): "k",
    (1, 1, 1, 0, 0, 0): "l",
    (1, 0, 1, 1, 0, 0): "m",
    (1, 0, 1, 1, 1, 0): "n",
    (1, 0, 1, 0, 1, 0): "o",
    (1, 1, 1, 1, 0, 0): "p",
    (1, 1, 1, 1, 1, 0): "q",
    (1, 1, 1, 0, 1, 0): "r",
    (0, 1, 1, 1, 0, 0): "s",
    (0, 1, 1, 1, 1, 0): "t",
    (1, 0, 1, 0, 0, 1): "u",
    (1, 1, 1, 0, 0, 1): "v",
    (0, 1, 0, 1, 1, 1): "w",
    (1, 0, 1, 1, 0, 1): "x",
    (1, 0, 1, 1, 1, 1): "y",
    (1, 0, 1, 0, 1, 1): "z",
}


def save_image(path: Path, image: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), image)


def load_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Could not open image: {path}")
    return image


def crop_image(image: np.ndarray, manual_crop: tuple[int, int, int, int] | None) -> tuple[np.ndarray, int, int]:
    height, width = image.shape[:2]

    if manual_crop is not None:
        x1, y1, x2, y2 = manual_crop
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(width, x2)
        y2 = min(height, y2)

        # If this crop does not fit the current image, just use the whole image.
        if x2 <= x1 or y2 <= y1:
            return image.copy(), 0, 0

        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            return image.copy(), 0, 0

        return crop, x1, y1

    y1 = int(height * BOTTOM_START_RATIO)
    return image[y1:height, 0:width], 0, y1


def make_mask(crop: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    # 1. Turn the crop into grayscale.
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # 2. Increase local contrast so raised dots stand out more.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    contrast = clahe.apply(gray)

    # 3. Estimate the page background and subtract it.
    background = cv2.GaussianBlur(contrast, (0, 0), sigmaX=15, sigmaY=15)
    enhanced = cv2.subtract(contrast, background)
    enhanced = cv2.normalize(enhanced, None, 0, 255, cv2.NORM_MINMAX)

    # 4. Make a black-and-white mask.
    _, mask = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 5. Clean tiny noise and connect broken pieces a little.
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
    )
    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
    )

    return gray, contrast, mask


def find_dot_centers(mask: np.ndarray) -> list[tuple[int, int, int, int, int]]:
    # Each connected white region is a possible Braille dot.
    count, _, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    dots: list[tuple[int, int, int, int, int]] = []

    for i in range(1, count):
        x, y, w, h, area = stats[i]

        # Keep only medium-sized blobs.
        if area < 80 or area > 4000:
            continue
        if w < 5 or h < 5:
            continue

        cx, cy = centroids[i]
        dots.append((int(cx), int(cy), int(w), int(h), int(area)))

    return dots


def group_cells(dots: list[tuple[int, int, int, int, int]], width: int, height: int) -> list[tuple[int, int, int, int]]:
    # We use the x positions of dots to guess where Braille columns are.
    if not dots:
        return []

    x_values = sorted([dot[0] for dot in dots])
    column_centers: list[int] = []
    tolerance = 35

    for x in x_values:
        if not column_centers or abs(x - column_centers[-1]) > tolerance:
            column_centers.append(x)
        else:
            column_centers[-1] = int((column_centers[-1] + x) / 2)

    # Two nearby columns should form one Braille cell.
    cells: list[tuple[int, int, int, int]] = []
    i = 0
    while i < len(column_centers):
        left = column_centers[i]

        if i + 1 < len(column_centers) and (column_centers[i + 1] - left) < 80:
            right = column_centers[i + 1]
            i += 2
        else:
            right = left
            i += 1

        related = [dot for dot in dots if left - 25 <= dot[0] <= right + 25]
        if not related:
            continue

        min_x = max(0, min(dot[0] for dot in related) - 25)
        max_x = min(width, max(dot[0] for dot in related) + 25)
        min_y = max(0, min(dot[1] for dot in related) - 25)
        max_y = min(height, max(dot[1] for dot in related) + 25)

        if (max_x - min_x) >= 20 and (max_y - min_y) >= 40:
            cells.append((min_x, min_y, max_x - min_x, max_y - min_y))

    return cells


def read_one_cell(cell_mask: np.ndarray) -> tuple[str, tuple[int, int, int, int, int, int]]:
    # Resize every cell to the same size so our dot checks are consistent.
    resized = cv2.resize(cell_mask, (120, 180), interpolation=cv2.INTER_AREA)

    # These are the six places where dots should be.
    probe_centers = [
        (36, 30),
        (36, 90),
        (36, 150),
        (84, 30),
        (84, 90),
        (84, 150),
    ]

    yy, xx = np.ogrid[:180, :120]
    pattern = []

    for center_x, center_y in probe_centers:
        circle = (xx - center_x) ** 2 + (yy - center_y) ** 2 <= 16 ** 2
        values = resized[circle]
        white_ratio = float(np.count_nonzero(values)) / float(values.size)
        pattern.append(1 if white_ratio > 0.10 else 0)

    pattern_tuple = tuple(pattern)
    letter = PATTERN_TO_CHAR.get(pattern_tuple, "?")
    return letter, pattern_tuple


def process_image(
    image_path: Path,
    output_dir: Path,
    manual_crop: tuple[int, int, int, int] | None = MANUAL_CROP,
) -> dict[str, str | int]:
    image = load_image(image_path)
    crop, offset_x, offset_y = crop_image(image, manual_crop)
    gray, contrast, mask = make_mask(crop)
    dots = find_dot_centers(mask)
    cells = group_cells(dots, crop.shape[1], crop.shape[0])

    annotated = image.copy()
    decoded_text = []
    debug_dots = crop.copy()

    for cx, cy, w, h, area in dots:
        cv2.circle(debug_dots, (cx, cy), 8, (255, 0, 255), 2)

    # Sort cells from left to right before reading them.
    cells.sort(key=lambda item: item[0])

    for cell_index, (x, y, w, h) in enumerate(cells, start=1):
        cell_mask = mask[y:y + h, x:x + w]
        letter, pattern = read_one_cell(cell_mask)
        decoded_text.append(letter)

        draw_x1 = x + offset_x
        draw_y1 = y + offset_y
        draw_x2 = draw_x1 + w
        draw_y2 = draw_y1 + h

        cv2.rectangle(annotated, (draw_x1, draw_y1), (draw_x2, draw_y2), (0, 255, 0), 2)
        cv2.putText(
            annotated,
            f"{cell_index}:{letter}",
            (draw_x1, max(20, draw_y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 180, 255),
            2,
            cv2.LINE_AA,
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    save_image(output_dir / "01_crop.jpeg", crop)
    save_image(output_dir / "02_gray.jpeg", gray)
    save_image(output_dir / "03_contrast.jpeg", contrast)
    save_image(output_dir / "04_mask.jpeg", mask)
    save_image(output_dir / "05_dot_centers.jpeg", debug_dots)
    save_image(output_dir / "06_annotated.jpeg", annotated)

    final_text = "".join(decoded_text).strip()
    (output_dir / "decoded_text.txt").write_text(final_text, encoding="utf-8")

    return {
        "image": str(image_path),
        "detected_dots": len(dots),
        "detected_cells": len(cells),
        "decoded_text": final_text,
        "output_dir": str(output_dir.resolve()),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple beginner Braille reader.")
    parser.add_argument(
        "--image",
        default=str(IMAGE_PATH),
        help="Path to the image you want to process.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_DIR),
        help="Folder where output files will be saved.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    image_path = Path(args.image)
    output_dir = Path(args.output_dir)

    print("Running simple Braille reader...")
    print(f"Image: {image_path}")

    results = process_image(image_path, output_dir)

    print()
    print(f"Detected dots: {results['detected_dots']}")
    print(f"Detected cells: {results['detected_cells']}")
    print(f"Decoded text: {results['decoded_text']!r}")
    print(f"Saved results in: {results['output_dir']}")
    print()
    print("If the result is bad, the first thing to try is changing MANUAL_CROP at the top of this file.")


if __name__ == "__main__":
    main()
