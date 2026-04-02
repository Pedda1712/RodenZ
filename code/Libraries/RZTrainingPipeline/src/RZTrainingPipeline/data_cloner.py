from pathlib import Path
import csv
import random
import shutil
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def collect_csv_rows(labeled_path: Path) -> Tuple[List[List[str]], List[List[str]]]:
    """Collect all rows and headers from CSV files under labeled_path recursively."""
    cam_rows, cam_header = [], []

    for csv_file in labeled_path.rglob("*.csv"):
        with csv_file.open(newline='') as f:
            reader = csv.reader(f)
            # Read headers (first 3 lines)
            if not cam_header:
                for _ in range(3):
                    cam_header.append(next(reader, None))
            else:
                for _ in range(3):
                    next(reader, None)
            cam_rows.extend(list(reader))

    return cam_header, cam_rows


def prepare_rows(
    cam_header: List[List[str]], 
    cam_rows: List[List[str]], 
    cam_dir: str,
    mode: str = "single"
) -> Tuple[List[List[str]], List[List[str]]]:
    """
    Prepare rows for DLC, either bootstrapped or exact.

    Parameters:
    - cam_header: CSV header lines.
    - cam_rows: Rows from all CSVs.
    - cam_dir: Name of the camera folder.
    - mode: "ensemble" to bootstrap rows, "single" to keep them unchanged.
    """
    if not cam_rows:
        return [], []

    if mode == "ensemble":
        n_samples = len(cam_rows)
        selected_rows = [random.choice(cam_rows) for _ in range(n_samples)]
    elif mode == "single":
        selected_rows = cam_rows
    else:
        raise ValueError(f"Invalid mode '{mode}'. Use 'ensemble' or 'single'.")

    fixed_rows = []
    for row in selected_rows:
        if len(row) < 4:
            continue
        # row[2] = filename (e.g. "img0001.png")
        rel_path = ["labeled-data", cam_dir, row[2]]
        new_row = rel_path + row[3:]
        fixed_rows.append(new_row)

    # Keep headers exactly as in original CSVs
    fixed_header = cam_header

    return fixed_header, fixed_rows


def copy_images_for_rows(
    labeled_path: Path,
    cam_dir: str,
    rows: List[List[str]],
    out_dir: Path 
):
    """
    Copy images to out_dir.
    Assumes row[2] = filename (e.g., "img0001.png")
    
    Parameters:
    - labeled_path: Path to the original labeled_data folder
    - cam_dir: Name of the camera folder (e.g., "Cam_1")
    - rows: Bootstrapped or exact rows from prepare_rows
    - out_dir: Default DLC output folder
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    cam_path = labeled_path / cam_dir
    img_map = {
        p.name: p
        for p in cam_path.rglob("*")
        if p.is_file() and p.suffix.lower() in [".png", ".jpg", ".jpeg"]
    }

    for row in rows:
        if len(row) < 3:
            continue

        img_name = row[2]  # filename
        dest_img = out_dir / img_name

        if img_name in img_map:
            src_img = img_map[img_name]
            
            if not src_img.exists():
                logger.warning(f"Skipping non-existent source: {src_img}")
                continue
            
            if not dest_img.exists():
                shutil.copy(src_img, dest_img)
        else:
            logger.warning(f"Image not found: {cam_path}/{img_name}")
