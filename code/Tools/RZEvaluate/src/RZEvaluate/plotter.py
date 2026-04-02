import argparse
import numpy as np
import pandas as pd
import re
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import logging
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# -------------------------
# Utils
# -------------------------
def extract_frame_number(name):
    m = re.search(r"(\d+)", str(name))
    if not m:
        raise ValueError(f"No frame number in {name}")
    return int(m.group(1))


def load_dlc_gt_csv(csv_path):
    logging.info(f"Loading GT CSV: {csv_path}")
    df = pd.read_csv(csv_path, header=[0, 1, 2])
    meta = df.columns[:3]
    kp = df.columns[3:]

    rows = []
    for _, r in df.iterrows():
        frame = extract_frame_number(r[meta[2]])
        joints = defaultdict(dict)
        for scorer, joint, coord in kp:
            if coord in ("x", "y") and not pd.isna(r[(scorer, joint, coord)]):
                joints[joint][coord] = float(r[(scorer, joint, coord)])
        for j, c in joints.items():
            if "x" in c and "y" in c:
                rows.append({
                    "frame": frame,
                    "joint": j,
                    "x_gt": c["x"],
                    "y_gt": c["y"],
                })
    logging.info(f"Loaded {len(rows)} GT points from {csv_path}")
    return pd.DataFrame(rows)


def compute_errors(gt, rp):
    df = pd.merge(gt, rp, on=["frame", "joint"])
    logging.info(f"Merged GT and RP: {len(df)} points matched")
    df["err_x"] = df.x_gt - df.x_rp
    df["err_y"] = df.y_gt - df.y_rp
    df["err_e"] = np.hypot(df.err_x, df.err_y)
    df["err_avg"] = (np.abs(df.err_x) + np.abs(df.err_y))
    return df


def rmse(series):
    return np.sqrt(np.mean(series**2))


def mean_pixel_error(series):
    return np.mean(series)


# -------------------------
# Save full L1/L2 distributions
# -------------------------
def save_l1_l2_distribution(df, out_csv):
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "camera": r["camera"],
            "joint": r["joint"],
            "metric": "l1",
            "value": r["err_avg"],
            "count": 1
        })
        rows.append({
            "camera": r["camera"],
            "joint": r["joint"],
            "metric": "l2",
            "value": r["err_e"],
            "count": 1
        })
    pd.DataFrame(rows).to_csv(out_csv, index=False)


# -------------------------
# Plotting
# -------------------------
class ErrorPlotter:
    PERCENTILES = [75, 90]
    COLORS = ["green", "purple"]

    @staticmethod
    def plot_histogram(data, title, out):
        plt.figure(figsize=(8, 6))
        count, bins, _ = plt.hist(
            data,
            bins=40,
            color="#2FBCF4",
            edgecolor="black",
            alpha=0.7
        )
        for p, c in zip(ErrorPlotter.PERCENTILES, ErrorPlotter.COLORS):
            v = np.percentile(data, p)
            plt.axvline(v, color=c, linestyle="--", linewidth=2)
        plt.xlabel("Pixel error (RMSE)")
        plt.ylabel("Count")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(out, dpi=300)
        plt.close()

    @staticmethod
    def plot_violin(data_dict, title, out):
        joints = list(data_dict.keys())
        data = [data_dict[j] for j in joints]
        plt.figure(figsize=(10, 6))
        sns.violinplot(data=data, inner="quartile")
        plt.xticks(range(len(joints)), joints, rotation=45, ha="right")
        plt.ylabel("Pixel error (RMSE)")
        plt.title(title)
        plt.tight_layout()
        plt.savefig(out, dpi=300)
        plt.close()


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser(description="GT vs 2D reprojection error analysis")
    parser.add_argument("--rp", nargs="+", required=True)
    parser.add_argument("--gt", nargs="+", required=True)
    parser.add_argument("--cams", nargs="+", type=int, required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--ignore", nargs="*", default=[])
    args = parser.parse_args()

    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    global_dfs = []

    for idx, (rp_path, gt_path, cam) in enumerate(zip(args.rp, args.gt, args.cams)):
        view_dir = outdir / f"view_{idx}_camera_{cam}"
        view_dir.mkdir(exist_ok=True)

        gt = load_dlc_gt_csv(gt_path)
        rp_all = pd.read_csv(rp_path).rename(columns={"x": "x_rp", "y": "y_rp"})
        rp = rp_all[rp_all.camera == cam]

        df = compute_errors(gt, rp)
        df["camera"] = cam

        if args.ignore:
            df = df[~df.joint.isin(args.ignore)]

        # HARD SAFETY: ensure only current cam
        assert df["camera"].nunique() == 1
        assert df["camera"].iloc[0] == cam

        global_dfs.append(df)

        # Save local distribution (ONLY this camera)
        save_l1_l2_distribution(df, view_dir / "l1_l2_distribution.csv")

        ErrorPlotter.plot_histogram(
            df.err_e.values,
            f"Camera {cam} – Error distribution",
            view_dir / "hist_all_joints.png"
        )

        ErrorPlotter.plot_violin(
            {j: g.err_e.values for j, g in df.groupby("joint")},
            f"Camera {cam} – Per-joint error",
            view_dir / "violin_all_joints.png"
        )

        joint_dir = view_dir / "per_joint"
        joint_dir.mkdir(exist_ok=True)
        for joint, g in df.groupby("joint"):
            ErrorPlotter.plot_histogram(
                g.err_e.values,
                f"Camera {cam} – {joint}",
                joint_dir / f"{joint}_hist.png"
            )
            save_l1_l2_distribution(
                g,
                joint_dir / f"{joint}_l1_l2_distribution.csv"
            )

        # ------------------------- Local per-joint summary -------------------------
        local_summary = df.groupby("joint").agg(
            rmse=("err_e", rmse),
            l1=("err_avg", mean_pixel_error),
            l2=("err_e", "mean")
        ).round(3)

        print(f"\nCamera {cam} – Per-joint errors (RMSE, L1, L2):")
        print(local_summary)

        avg_rmse = rmse(df["err_e"])
        avg_l1 = mean_pixel_error(df["err_avg"])
        avg_l2 = df["err_e"].mean()
        print(f"Camera {cam} – Average RMSE: {avg_rmse:.3f}")
        print(f"Camera {cam} – Average L1 error: {avg_l1:.3f}")
        print(f"Camera {cam} – Average L2 error: {avg_l2:.3f}")

        # Save local summary CSV
        summary_csv = view_dir / "summary.csv"
        local_summary.to_csv(summary_csv)

    # ------------------------- Global summary -------------------------
    global_df = pd.concat(global_dfs, ignore_index=True)
    global_dir = outdir / "global"
    global_dir.mkdir(exist_ok=True)

    save_l1_l2_distribution(global_df, global_dir / "l1_l2_distribution.csv")

    ErrorPlotter.plot_histogram(
        global_df.err_e.values,
        "Global – Error distribution",
        global_dir / "hist_all.png"
    )

    ErrorPlotter.plot_violin(
        {j: g.err_e.values for j, g in global_df.groupby("joint")},
        "Global – Per-joint error",
        global_dir / "violin_all.png"
    )

    joint_dir = global_dir / "per_joint"
    joint_dir.mkdir(exist_ok=True)
    for joint, g in global_df.groupby("joint"):
        ErrorPlotter.plot_histogram(
            g.err_e.values,
            f"Global – {joint}",
            joint_dir / f"{joint}_hist.png"
        )
        save_l1_l2_distribution(
            g,
            joint_dir / f"{joint}_l1_l2_distribution.csv"
        )

    # Global per-joint summary
    global_summary = global_df.groupby("joint").agg(
        rmse=("err_e", rmse),
        l1=("err_avg", mean_pixel_error),
        l2=("err_e", "mean")
    ).round(3)

    print("\nGlobal – Per-joint errors (RMSE, L1, L2):")
    print(global_summary)

    global_avg_rmse = rmse(global_df["err_e"])
    global_avg_l1 = mean_pixel_error(global_df["err_avg"])
    global_avg_l2 = global_df["err_e"].mean()
    print(f"Global – Average RMSE: {global_avg_rmse:.3f}")
    print(f"Global – Average L1 error: {global_avg_l1:.3f}")
    print(f"Global – Average L2 error: {global_avg_l2:.3f}")

    # Save global summary CSV
    global_summary_csv = global_dir / "summary.csv"
    global_summary.to_csv(global_summary_csv)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    main()
