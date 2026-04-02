import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse

# -------------------------
# Functions
# -------------------------
def load_csvs(names, paths):
    """Load multiple L1/L2 CSVs and tag with dataset names."""
    dfs = []
    for name, path in zip(names, paths):
        df = pd.read_csv(path)
        df["dataset"] = name
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def plot_shared_hist_box(df, metric, out_path, colors=None, n_bins=100, alpha=0.35):
    """
    Overlay histograms and smooth KDEs for all datasets.
    Removes top 1% of values as outliers.
    Histograms are continuous (no gaps), and negative x-values are clipped to zero.
    """
    datasets = df["dataset"].unique()
    
    # Assign colors to datasets
    if colors is None:
        colors = ["green", "blue", "red", "purple", "orange", "brown"]
    
    color_map = {ds: colors[i] if i < len(colors) else "gray"
                 for i, ds in enumerate(datasets)}
    
    plt.figure(figsize=(10, 6))
    
    # Get all values for this metric
    values_all = df[df["metric"] == metric]["value"]
    if len(values_all) == 0:
        raise ValueError(f"No data found for metric '{metric}'")
    
    # Remove top 1% outliers
    upper_limit = np.percentile(values_all, 99)
    
    # Clip negative values to zero
    values_all = np.clip(values_all, 0, upper_limit)
    
    bins = np.linspace(0, upper_limit, n_bins + 1)
    
    # Plot histograms and KDEs
    for ds in datasets:
        vals = df[(df["dataset"] == ds) & (df["metric"] == metric)]["value"]
        vals = np.clip(vals, 0, upper_limit)
        if len(vals) == 0:
            print(f"Warning: dataset '{ds}' has no values for metric '{metric}', skipping.")
            continue
        
        # Histogram
        plt.hist(
            vals,
            bins=bins,
            color=color_map[ds],
            alpha=alpha,
            edgecolor=None,
            linewidth=0,
            label=f"{ds} hist",
            density=True
        )
        
        # KDE overlay
        sns.kdeplot(
            vals,
            color=color_map[ds],
            linewidth=2,
            alpha=0.9,
            label=f"{ds} KDE"
        )
    
    plt.xlabel("Deviation from hand annotations [pixels]")
    plt.ylabel("Density")
    plt.title(f"{metric.upper()} Error Distribution")
    plt.legend()
    
    # Improve y-axis labels (nice rounded numbers)
    y_max = plt.gca().get_ylim()[1]
    y_ticks = np.linspace(0, y_max, 10)
    plt.yticks(y_ticks, [f"{ytick:.2f}" for ytick in y_ticks])
    
    # Set x-axis minimum to zero
    plt.xlim(left=0)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()


# -------------------------
# Main
# -------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csvs", nargs="+", required=True, help="Paths to L1/L2 CSVs")
    parser.add_argument("--names", nargs="+", required=True, help="Names of datasets (for legend)")
    parser.add_argument("--out", required=True, help="Output PNG path")
    parser.add_argument("--metric", default="l2", choices=["l1","l2"], help="Metric to plot")
    parser.add_argument("--colors", nargs="+", help="Colors for datasets in order (e.g. green blue red)")
    args = parser.parse_args()

    df = load_csvs(args.names, args.csvs)
    plot_shared_hist_box(df, args.metric, Path(args.out), colors=args.colors)


# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    main()
