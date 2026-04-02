import sys
import argparse
import json

import cv2

import pandas as pd
import numpy as np

def fetch_keypoint_locations(filename: str):
    table = np.array(pd.read_csv(filename, header = None))
    table = table[3:, 1:].astype(float) # remove DLC header

    indices = np.array([False] * table.shape[1])
    indices[2::3] = True

    coords = table[:, ~indices].reshape(table.shape[0], -1, 2)
    likelihoods = table[:, indices]
    return coords, likelihoods

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
        return None, None
    d = json.loads(open(filename).read())
    return np.array([
        d["distortion"]["k1"],
        d["distortion"]["k2"],
        d["distortion"]["p1"],
        d["distortion"]["p2"],
        d["distortion"]["k3"]
    ]), get_intrinsics_from_fov(d["camera_fov"], d["resolution"]["x"], d["resolution"]["y"])

def main():
    parser = argparse.ArgumentParser(
        prog = "RZView2DCSV",
        description = "A tool for visualizing inferred DLC trajectories and OpenCV undistortion."
    )

    parser.add_argument("--video", help="Path to the video to display.", required=True, type = str)
    parser.add_argument("--csv", help="Path to DLC output csv to display on top.", required=True, type = str)
    parser.add_argument("--camera-parameters", help="Path to CamX.json for undistortion parameters. If given, undistortion is performed (but only on the video, you need to provide undistorted keypoint detections yourself).", required = False, type = str)
    args = parser.parse_args()

    dist_coefficients, cam_mat = fetch_undistortion_parameters(args.camera_parameters)

    keypoints, likelihoods = fetch_keypoint_locations(args.csv)
    
    cap = cv2.VideoCapture(args.video)

    print("[INFO] Press 'Q' to quit!")

    frame_counter = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        keypoint_list = keypoints[frame_counter]
        likelihood_list = likelihoods[frame_counter]

        if dist_coefficients is not None:
            frame = cv2.undistort(frame, cam_mat, dist_coefficients)

        for (x, y), likelihood in zip(keypoint_list, likelihood_list):
            cv2.circle(frame, (int(x), int(y)), 2, (255, 0, 255), -1)

        cv2.imshow('view2Dcsv', frame)
        if cv2.waitKey(1) == ord('q'):
            break
        frame_counter += 1
    
if __name__ == "__main__":
    main()
