import argparse
import json

import cv2

import pandas as pd
import numpy as np

def fetch_keypoint_locations(filename: str):
    table = pd.read_csv(filename, header = None)
    dlc_head = table[:3]
    table = np.array(table)[3:, 1:].astype(float) # remove DLC header

    indices = np.array([False] * table.shape[1])
    indices[2::3] = True

    coords = table[:, ~indices].reshape(table.shape[0], -1, 2)
    likelihoods = table[:, indices]
    return dlc_head, coords, likelihoods

def get_intrinsics_from_fov(fov_deg, width, height):
    f = (width / 2) / np.tan(np.radians(fov_deg / 2))
    K = np.array([
        [f, 0, width/2],
        [0, f, height/2],
        [0, 0, 1]
    ])
    return K

def fetch_undistortion_parameters(filename: str):
    if not filename:
        return None
    d = json.loads(open(filename).read())
    return np.array([
        d["distortion"]["k1"],
        d["distortion"]["k2"],
        d["distortion"]["p1"],
        d["distortion"]["p2"],
        d["distortion"]["k3"]
    ]), get_intrinsics_from_fov(d["camera_fov"], d["resolution"]["x"], d["resolution"]["y"])

def export_corrected(filename: str, dlc_head, keypoints, likelihoods):
    keypoints = keypoints.reshape(keypoints.shape[0], -1)

    interleaved = np.zeros((keypoints.shape[0], keypoints.shape[1] + likelihoods.shape[1]))
    indices = np.array([False] * interleaved.shape[1])
    indices[2::3] = True
    interleaved[:, indices] = likelihoods
    interleaved[:, ~indices] = keypoints
    interleaved = np.hstack((np.arange(interleaved.shape[0]).reshape(-1, 1), interleaved))

    pd.concat((dlc_head, pd.DataFrame(interleaved))).to_csv(filename, header = False, index = False)

    exit()

def main():
    parser = argparse.ArgumentParser(
        prog = "RZCorrect2D",
        description = "A tool for removing radial distortion from 2D keypoints. Provided a CSV of DLC output and a camera parameters file, this tool will output a corrected CSV."
    )

    parser.add_argument("--input", help="Path to DLC output csv to correct.", required=True, type = str)
    parser.add_argument("--output", help="Path to use for saving corrected keypoints.", required=True, type = str)
    parser.add_argument("--camera-parameters", help="Path to CamX.json for undistortion parameters.", required = True, type = str)
    args = parser.parse_args()

    dist_coefficients, cam_mat = fetch_undistortion_parameters(args.camera_parameters)
    dlc_head, keypoints, likelihoods = fetch_keypoint_locations(args.input)

    for time in range(keypoints.shape[0]):
        keypoints[time] = cv2.undistortPoints(keypoints[time], cam_mat, dist_coefficients, None, cam_mat)[:, 0]

    export_corrected(args.output, dlc_head, keypoints, likelihoods)
    
if __name__ == "__main__":
    main()
