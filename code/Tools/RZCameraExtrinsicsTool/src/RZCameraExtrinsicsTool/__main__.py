from RZVisuals import DisplayConfig, Observer
from .CameraExtrinsicsToolDisplay import CameraExtrinsicsToolDisplay

import sys
import argparse
import os
import json
import dataclasses

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "RZCameraExtrinsicsTool",
        description = "A tool for aligning a virtual view with actual camera images to deduce camera positions."
    )

    parser.add_argument("--image", help="Path to the image which is to be displayed over the virtual geometry.", required=True)
    parser.add_argument("--output", help="Path to save to.", required=True)
    args = parser.parse_args()

    if os.path.isfile(args.output) or os.path.isfile(args.output):
        print("error: specified output path already exists")
        exit()

    print("\n--- CONTROLS ---")
    print("Use W/A/S/D to position the camera around the center point.")
    print("Use Q/E to change the camera distance from the center point.")
    print("Use I/J/K/L to change the cameras local viewing angle (to look away from the center point)")
    print("Use M/N to change the camera fov.")
    print("")
    print("The rendered geometry represents the floor of the experiment box. Align the virtual camera such that it corresponds with the overlay texture drawn ontop of it.")
    print("")
    print("Once you have aligned the cameras, close the program. The parameters will be saved automatically to your specified output location.")
    print("--- ---")
    initial_position = Observer(42.4, 29.62, -89.8, 53, -7.35, 0.66)
    config = DisplayConfig(dimensions = (int(1000 * 4/3), 1000))
    display = CameraExtrinsicsToolDisplay(config, args.image, initial_position)
    while display.display([35, 35, 35]):
        continue
    
    with open(f"{args.output}.json", "w") as f:
        f.write(json.dumps(dataclasses.asdict(display.camera.observer)))
        f.close()
