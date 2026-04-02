import argparse
import logging
from pathlib import Path
import csv
import numpy as np

from aniposelib.cameras import CameraGroup
from aniposelib.utils import load_pose2d_fnames
from anipose.filter_pose import filter_pose_medfilt, filter_pose_viterbi

# CSV → H5 conversion
def convert_csv_to_h5(files, scorer=None, userfeedback=False):
    import pandas as pd
    from itertools import islice

    for fn in files:
        fn = Path(fn)
        if not fn.exists():
            print(f"Warning: {fn} does not exist. Skipping.")
            continue

        if userfeedback:
            askuser = input(f"Convert {fn}? (yes/no): ").strip().lower()
            if askuser not in ("y", "yes"):
                continue

        try:
            with open(fn) as f:
                head = list(islice(f, 0, 5))

            header = list(range(4)) if "individuals" in head[1] else list(range(3))
            index_col = [0, 1, 2] if head[-1].split(",")[0] == "labeled-data" else 0
            data = pd.read_csv(fn, index_col=index_col, header=header)

            if scorer:
                data.columns = data.columns.set_levels([scorer], level="scorer")

            if not isinstance(data.index, pd.MultiIndex):
                data.index = pd.MultiIndex.from_arrays([data.index], names=["index"])

            h5_fn = fn.with_suffix(".h5")
            data.to_hdf(h5_fn, key="df_with_missing", mode="w")
            print(f"Converted {fn} → {h5_fn}")

        except Exception as e:
            print(f"Error converting {fn}: {e}")


# Filtering + triangulation
def filter_and_triangulate(d, cgroup, config=None, use_viterbi=False):
    n_cams, n_points, n_joints, _ = d["points"].shape
    points = d["points"].copy()
    scores = d["scores"].copy()
    bodyparts = d["bodyparts"]

    points_filtered = np.empty_like(points)
    scores_filtered = np.empty_like(scores)

    for cam in range(n_cams):
        cam_points = np.full((n_points, n_joints, 1, 3), np.nan)
        cam_points[:, :, 0, :2] = points[cam]
        cam_points[:, :, 0, 2] = scores[cam]

        if use_viterbi:
            pts_filt, sc_filt = filter_pose_viterbi(config, cam_points, bodyparts)
        else:
            pts_filt, sc_filt = filter_pose_medfilt(config, cam_points, bodyparts)

        points_filtered[cam] = pts_filt
        scores_filtered[cam] = sc_filt

    points_flat = points_filtered.reshape(n_cams, -1, 2)

    p3ds_flat = cgroup.triangulate(points_flat, progress=True)
    reprojerr_flat = cgroup.reprojection_error(
        p3ds_flat, points_flat, mean=True
    )

    p3ds = p3ds_flat.reshape(n_points, n_joints, 3)
    reprojerr = reprojerr_flat.reshape(n_points, n_joints)

    return p3ds, reprojerr, points_filtered, scores_filtered


# Helpers
def run_triangulation(pose_data, cgroup, config, use_viterbi):
    return filter_and_triangulate(
        pose_data, cgroup, config=config, use_viterbi=use_viterbi
    )


def run_bundle_adjustment(cgroup, pose_data, refine_intrinsics, logger, max_frames=None,
                          save_calibration=True,output_calibration=None,):
    logger.info("Running bundle adjustment...")

    n_cams, n_frames, n_joints, _ = pose_data["points"].shape
    points_sub = pose_data["points"]

    # Subsample frames if max_frames is set
    if max_frames is not None and max_frames < n_frames:
        step = max(1, n_frames // max_frames)
        frame_indices = np.arange(0, n_frames, step)
        points_sub = points_sub[:, frame_indices, :, :]
        logger.info(f"Subsampled to {len(frame_indices)} frames for BA")

    # Remove frames with any NaNs
    valid_frames = ~np.isnan(points_sub).any(axis=(0, 2, 3))
    points_clean = points_sub[:, valid_frames, :, :].reshape(n_cams, -1, 2)
    logger.info(f"{points_clean.shape[1]//n_cams} frames used for BA after removing NaNs")

    # Run bundle adjustment
    cgroup.bundle_adjust(
        points_clean,
        only_extrinsics=not refine_intrinsics,
        verbose=True,
    )

    logger.info("Bundle adjustment completed.")
    
    updated_params = cgroup.get_dicts()
    for i, cam_dict in enumerate(updated_params):
        print(f"\nCamera {i} parameters after BA:")
        for k, v in cam_dict.items():
            print(f"  {k}: {v}")

    # Save updated calibration if requested
    if save_calibration:
        if output_calibration is not None:
            output_calibration.parent.mkdir(parents=True, exist_ok=True)
            cgroup.dump(output_calibration)
            logger.info(f"Updated calibration saved to {output_calibration}")
        elif hasattr(cgroup, "_calibration_file") and cgroup._calibration_file is not None:
            cgroup.dump(cgroup._calibration_file)
            logger.info(f"Updated calibration overwritten at {cgroup._calibration_file}")
        else:
            logger.warning("No calibration output path provided; calibration not saved.")

def main():
    parser = argparse.ArgumentParser(description="Anipose triangulation pipeline")

    parser.add_argument("--calibration", type=Path, required=True)
    parser.add_argument("--keypoints", type=Path, nargs="+", required=True)

    parser.add_argument("--likelihood-threshold", type=float, default=0.5)
    parser.add_argument("--median-size", type=int, default=1)
    parser.add_argument("--scorer", type=str, default=None)
    parser.add_argument("--use-viterbi", action="store_true")

    parser.add_argument(
        "--triangulation-mode",
        choices=["direct", "ba_before"],
        default="direct",
    )

    parser.add_argument(
        "--ba-refine-intrinsics",
        action="store_true",
    )

    parser.add_argument(
        "--max-ba-frames",
        type=int,
        default=None,
        help="Maximum number of frames to use for bundle adjustment (subsampled if too large)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output CSV file for triangulated 3D points (must include filename)"
    )

    parser.add_argument(
        "--output-reprojected-2d",
        type=Path,
        default=None,
        help="Output CSV file for reprojected 2D points (must include filename)"
    )

    parser.add_argument(
    "--output-calibration",
    type=Path,
    default=None,
    help="Optional output path for updated calibration after bundle adjustment"
    )
    
    parser.add_argument("--log-level", type=str, default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))
    logger = logging.getLogger("Triangulation")

    # Load cameras
    cgroup = CameraGroup.load(args.calibration)
    cgroup._calibration_file = args.calibration  # store original path for saving

    # Convert CSV → H5 if needed
    csv_files = [f for f in args.keypoints if f.suffix.lower() == ".csv"]
    if csv_files:
        convert_csv_to_h5(csv_files, scorer=args.scorer, userfeedback=False)

    h5_files = [
        f.with_suffix(".h5") if f.suffix.lower() == ".csv" else f
        for f in args.keypoints
    ]

    # Load 2D poses
    fname_dict = {f"cam_{i}": f for i, f in enumerate(h5_files)}
    pose_data = load_pose2d_fnames(fname_dict, cam_names=sorted(fname_dict.keys()))

    # Likelihood threshold
    mask = pose_data["scores"] < args.likelihood_threshold
    pose_data["points"][mask] = np.nan

    # Filter config
    config = {
        "filter": {
            "medfilt": args.median_size,
            "offset_threshold": 8.0,
            "score_threshold": args.likelihood_threshold,
            "spline": False,
            "multiprocessing": True,
            "n_back": 3,
        }
    }

    # Triangulation modes
    if args.triangulation_mode == "direct":
        logger.info("Mode: direct triangulation")
        p3d, reprojerr, _, _ = run_triangulation(
            pose_data, cgroup, config, args.use_viterbi
        )

    elif args.triangulation_mode == "ba_before":
        logger.info("Mode: bundle adjustment before triangulation")
        run_bundle_adjustment(
            cgroup,
            pose_data,
            refine_intrinsics=args.ba_refine_intrinsics,
            logger=logger,
            max_frames=args.max_ba_frames,
            output_calibration=args.output_calibration,
        )
        p3d, reprojerr, _, _ = run_triangulation(
            pose_data, cgroup, config, args.use_viterbi
        )

    # Save outputs
    mean_error_per_joint = np.nanmean(reprojerr, axis=0)
    for j, err in enumerate(mean_error_per_joint):
        print(f"Joint {j}: Average reprojection error = {err:.3f}")

    header = [f"{bp}_{ax}" for bp in pose_data["bodyparts"] for ax in ("X", "Y", "Z")]
    output_file = args.output
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for frame in range(p3d.shape[0]):
            w.writerow(p3d[frame].flatten())
    logger.info(f"Saved 3D points to {output_file}")

    # Save reprojected 2D CSV
    if args.output_reprojected_2d:
        out_csv = args.output_reprojected_2d
        out_csv.parent.mkdir(parents=True, exist_ok=True)


        n_points, n_joints, _ = p3d.shape
        n_cams = len(cgroup.cameras)
        p3d_flat = p3d.reshape(-1, 3)

        reprojected = {}
        for cam_idx, cam in enumerate(cgroup.cameras):
            proj = cam.project(p3d_flat)
            reprojected[cam_idx] = proj.reshape(n_points, n_joints, 2)

        with open(out_csv, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["frame", "camera", "joint", "x", "y", "reproj_error"])
            for frame in range(n_points):
                for joint_idx, joint_name in enumerate(pose_data["bodyparts"]):
                    for cam_idx in range(n_cams):
                        x, y = reprojected[cam_idx][frame, joint_idx]
                        err = reprojerr[frame, joint_idx]
                        writer.writerow([frame + 1, cam_idx, joint_name, x, y, err])
        logger.info(f"Saved reprojected 2D keypoints to {out_csv}")

    logger.info("Triangulation pipeline completed successfully.")


if __name__ == "__main__":
    main()
