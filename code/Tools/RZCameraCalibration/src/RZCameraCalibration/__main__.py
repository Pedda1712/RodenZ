import cv2
import numpy as np
import logging
import argparse
from pathlib import Path
import toml

from aniposelib.boards import CharucoBoard
from aniposelib.cameras import CameraGroup


# -------------------------------------------------------
#  Detect dictionary in video
# -------------------------------------------------------
def detect_best_dictionary(video_path):
    cap = cv2.VideoCapture(str(video_path))
    DICT_NAMES = [d for d in dir(cv2.aruco) if "DICT_" in d]

    def test_dictionary(frame):
        results = []
        for name in DICT_NAMES:
            try:
                d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, name))
                corners, ids, _ = cv2.aruco.detectMarkers(frame, d)
                if ids is not None and len(ids) > 5:
                    results.append((name, len(ids)))
            except Exception:
                pass
        return results

    best_dict = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = test_dictionary(frame)
        if results:
            best_dict = max(results, key=lambda x: x[1])[0]
            break

    cap.release()
    return best_dict


# -------------------------------------------------------
#  Estimate marker/square pixel ratio
# -------------------------------------------------------
def estimate_marker_square_ratio(video_path, dict_name):
    cap = cv2.VideoCapture(str(video_path))
    d = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dict_name))
    marker_pixels = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        corners, ids, _ = cv2.aruco.detectMarkers(frame, d)
        if ids is None:
            continue

        for c in corners:
            pts = c[0]
            side_px = np.mean([
                np.linalg.norm(pts[0] - pts[1]),
                np.linalg.norm(pts[1] - pts[2]),
                np.linalg.norm(pts[2] - pts[3]),
                np.linalg.norm(pts[3] - pts[0])
            ])
            marker_pixels.append(side_px)

    cap.release()

    if not marker_pixels:
        raise RuntimeError("Could not detect markers to estimate sizes.")

    marker_mean_px = np.mean(marker_pixels)
    square_mean_px = marker_mean_px / 0.75  # typical Charuco ratio

    return marker_mean_px, square_mean_px


# -------------------------------------------------------
# Main calibration function
# -------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Charuco board camera calibration.")

    parser.add_argument('--calibration-vids', type=Path, required=True, nargs="+",help="Paths to the calibration videos.")
    
    parser.add_argument('--fisheye', action='store_true', help="Enable fisheye calibration model.")
    parser.add_argument('--no-fisheye', dest='fisheye', action='store_false', help="Disable fisheye model.")

    parser.set_defaults(fisheye=False)

    parser.add_argument('--output', type=Path, required=True, help="Output path for the calibration toml.")
    parser.add_argument('--log-level', type=str, default="INFO")

    # Manual board parameters
    parser.add_argument('--squaresX', type=int, help="Ammount of sqaures in X direction.")
    parser.add_argument('--squaresY', type=int, help="Ammount of sqaures in Y direction.")
    parser.add_argument('--square-length', type=float,help="Length of squares in arbitary units.")
    parser.add_argument('--marker-length', type=float,help="Length of markers in arbitary units.")
    parser.add_argument('--dictionary', type=str,help="Dictonary size.")
    parser.add_argument('--auto-board', action='store_true',help="Flag for automatical board parameter etimation.")

    parser.add_argument('--initial', action='store_true',
                        help="Load existing camera calibration as initialization.")
    parser.add_argument('--initial-file', type=Path,
                        help="TOML file containing stored calibration.")

    args = parser.parse_args()

    # -----------------------
    # Logging setup
    # -----------------------
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("calibration")

    logger.info("=== Starting Charuco Calibration ===")
    logger.info(f"FISHEYE = {args.fisheye}")

    # Determine if manual board params provided
    manual_board_supplied = (
        args.squaresX is not None and
        args.squaresY is not None and
        args.square_length is not None and
        args.marker_length is not None and
        args.dictionary is not None
    )

    # ---------------------------------------------------
    # Manual board
    # ---------------------------------------------------
    if manual_board_supplied and not args.auto_board:
        logger.info("Using manually specified Charuco board parameters.")

        dict_name = args.dictionary
        if not hasattr(cv2.aruco, dict_name):
            raise ValueError(f"Invalid dictionary name: {dict_name}")

        parts = dict_name.split("_")
        marker_bits = int(parts[1][0])
        dict_size = int(parts[2])

        board = CharucoBoard(
            squaresX=args.squaresX,
            squaresY=args.squaresY,
            square_length=args.square_length,
            marker_length=args.marker_length,
            marker_bits=marker_bits,
            dict_size=dict_size
        )

    else:
        # ---------------------------------------------------
        # Auto-detect board parameters
        # ---------------------------------------------------
        logger.info("Auto mode: Detecting dictionary from video...")

        dict_name = detect_best_dictionary(args.calibration_vids[0])
        if dict_name is None:
            raise RuntimeError("Could not detect markers in video.")

        logger.info(f"Detected ArUco dictionary: {dict_name}")

        marker_px, square_px = estimate_marker_square_ratio(args.calibration_vids[0], dict_name)
        logger.info(f"Marker px = {marker_px:.2f}, square px = {square_px:.2f}")

        marker_length = round(marker_px, 2)
        square_length = round(square_px, 2)

        parts = dict_name.split("_")
        marker_bits = int(parts[1][0])
        dict_size = int(parts[2])

        board = CharucoBoard(
            squaresX=7,
            squaresY=4,
            square_length=square_length,
            marker_length=marker_length,
            marker_bits=marker_bits,
            dict_size=dict_size
        )

        logger.info("Auto board constructed successfully.")

    cam_names = [f"cam_{i}" for i in range(len(args.calibration_vids))]
    vidnames = [[str(p)] for p in args.calibration_vids]

    logger.info("Determining camera frame sizes...")
    sizes = []
    for vid in args.calibration_vids:
        cap = cv2.VideoCapture(str(vid))
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise RuntimeError(f"Could not read first frame from {vid}")
        h, w = frame.shape[:2]
        sizes.append((w, h))

    logger.info(f"Detected sizes: {sizes}")

    logger.info("Initializing CameraGroup...")
    fisheye = args.fisheye
    cgroup = CameraGroup.from_names(cam_names, fisheye=fisheye)

    for cam, (w, h) in zip(cgroup.cameras, sizes):
        cam.set_size((w, h))

    # -------------------------------------------------------
    # Preload calibration
    # -------------------------------------------------------
    if args.initial:
        if args.initial_file is None:
            raise ValueError("--initial requires --initial_file")

        logger.info(f"Loading initial camera data from {args.initial_file}")

        data = toml.load(args.initial_file)

        for cam in cgroup.cameras:
            name = cam.name
            if name not in data:
                logger.warning(f"No initial data for {name}, skipping.")
                continue

            entry = data[name]

            cam.set_camera_matrix(np.array(entry["matrix"]))
            cam.set_distortions(np.array(entry["distortions"]))
            cam.set_rotation(np.array(entry["rotation"]))
            cam.set_translation(np.array(entry["translation"]))
            cam.fisheye = args.fisheye

        logger.info("Initial parameters loaded successfully.")

        logger.info("Calibrating with initial parameters...")
        cgroup.calibrate_videos(
            vidnames, board,
            init_intrinsics=False,
            init_extrinsics=False
        )

    else:
        logger.info("Calibrating without initial parameters...")
        cgroup.calibrate_videos(vidnames, board)

    # -------------------------------------------------------
    # Output results
    # -------------------------------------------------------
    for cam in cgroup.cameras:
        logger.info(f"Camera: {cam.name}")
        logger.info(f"K =\n{cam.get_camera_matrix()}")
        logger.info(f"D = {cam.get_distortions()}")
        logger.info(f"R =\n{cam.get_rotation()}")
        logger.info(f"t = {cam.get_translation()}")

    args.output.mkdir(parents=True, exist_ok=True)
    save_path = args.output / "calibration.toml"
    logger.info(f"Saving calibration to {save_path}")
    cgroup.dump(save_path)

    logger.info("Calibration completed successfully.")


if __name__ == "__main__":
    main()
