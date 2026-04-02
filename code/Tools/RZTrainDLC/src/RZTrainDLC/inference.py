import argparse
import deeplabcut
from pathlib import Path

def infer(config_path, video_dir, video_type, destfolder, shuffle):
    deeplabcut.analyze_videos(
        config_path,
        videos=video_dir,
        videotype=video_type,
        save_as_csv=True,
        destfolder=destfolder,
        shuffle=shuffle,
        batchsize=64
    )

def main():
    parser = argparse.ArgumentParser(description="Run DeepLabCut inference only.")
    parser.add_argument('--config', type=Path, required=True,
                        help='Existing DLC config path; if not provided, a temporary project will be created')
    parser.add_argument('--shuffle',type=int,required=True,
                         help='The shuffle is a integer ID which is used to identify the trained model. This ID is also needed for inference.')
    parser.add_argument('--inference-dest',type=Path,required=True,
                        help='Path where the infered CSV file is getting saved.')
    parser.add_argument('--inference-src',type=Path,required=True,
                        help='Path where the source videos for inference are saved.')
    parser.add_argument('--inference-suf',choices= ['avi', 'mp4', 'mov', 'mpeg', 'mkv', 'AVI', 'MP4', 'MOV', 'MPEG', 'MKV']
                        ,required=True,
                         help='File suffix of the source videos in inference_src.')
    
    args = parser.parse_args()

    infer(
        config_path=args.config,
        video_dir=args.inference_src,
        video_type=args.inference_suf,
        destfolder=args.inference_dest,
        shuffle=args.shuffle
    )

if __name__ == "__main__":
    main()
