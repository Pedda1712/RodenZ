import argparse
import json
import itertools
import pandas as pd
import numpy as np
from .MouseDisplay import MouseDisplay
from RZVisuals import Observer, DisplayConfig

def load_measurements(filename, rescale=1.0):
    v = pd.read_csv(filename)
    v = np.array(v)
    v = v.reshape(v.shape[0], -1, 3)
    mean = v.mean(axis=(0,1))
    v[:, :] -= mean
    v[:, :] *= float(rescale)
    return v

def main():
    parser = argparse.ArgumentParser(prog = "RZView3DCSV", description = "Simple trajectory viewer.")
    parser.add_argument("--csv", help="csv file where columns are (x,y,z) for each keypoint", type=str, required = True)
    parser.add_argument("--skeleton-definition", help="JSON file with skeleton definition.", type=str, required = True)
    parser.add_argument("--rescale-to", help="all 3D values have the mean substracted off of them and then get multiplied by this factor.", default = 1)
    args = parser.parse_args()

    lists_of_balls = load_measurements(args.csv, args.rescale_to)

    config = json.load(open(args.skeleton_definition))
    points = config["KeypointNames"]
    skeleton = [[points.index(start), points.index(end)] for (start, end) in config["Skeleton"]]

    display = MouseDisplay(DisplayConfig())

    for row in itertools.cycle(lists_of_balls):
        if not display.display(row.tolist(), skeleton):
            break

if __name__ == "__main__":
    main()
