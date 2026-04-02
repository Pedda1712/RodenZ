import argparse
import logging
import csv
from pathlib import Path
import deeplabcut
from RZTrainingPipeline import data_cloner, config, utils
from . import inference


def main():
    default_working_dir = Path.home() / "temp"
    parser = argparse.ArgumentParser(description="Run RZ DLC Training Pipeline")
    parser.add_argument('--config', type=Path, default=None,
                        help='Existing DLC config path; if not provided, a temporary project will be created')
    parser.add_argument('--bodyparts-file', type=Path,required=True,
                        help='Path to a TXT or file containing bodyparts to use')
    parser.add_argument('--training-label', type=Path, required=True,
                        help='Folder containing labeled data CSVs and images')
    parser.add_argument('--mode', choices=['ensemble', 'single'], default='single',help='Dataset preparation mode: "single" keeps the data as-is, '
         '"ensemble" bootstraps (resamples) the data for training.')
    parser.add_argument('--epochs', type=int, default=100)
    parser.add_argument('--working-dir', type=Path, default=default_working_dir,
                        help='Working directory to create temporary project or use for existing project')
    parser.add_argument('--scorer', type=str, default='temp_user',
                        help='Name of the scorer for labeling/bootstrapping (default: temp_user)')
    parser.add_argument( '--training-src',type=str,nargs='+',default=None,
    help='Path(s) to video file(s) to use when creating a temporary DLC project (required if --config is not provided)'
    )
    parser.add_argument('--shuffle',type=int,required=True,
                         help='The shuffle is a integer ID which is used to identify the trained model. This ID is also needed for inference.')
    parser.add_argument('--inference',type=bool,default=False,
                        help='Determines if the pipeline should infer after training.')
    parser.add_argument('--inference-dest',type=Path,default=None,
                        help='Path where the infered CSV file is getting saved.')
    parser.add_argument('--inference-src',type=Path,default=None,
                        help='Path where the source videos for inference are saved.')
    parser.add_argument('--inference-suf',choices= ['avi', 'mp4', 'mov', 'mpeg', 'mkv','AVI', 'MP4', 'MOV', 'MPEG', 'MKV']
                        ,default='avi',
                         help='File suffix of the source videos in inference_src.')
    parser.add_argument(
    '--net',
    choices=[
        # ResNets
        'resnet_50', 'resnet_101',
        'top_down_resnet_50', 'top_down_resnet_101',

        # HRNet
        'hrnet_w18', 'hrnet_w32', 'hrnet_w48',
        'top_down_hrnet_w18', 'top_down_hrnet_w32', 'top_down_hrnet_w48',

        # DEKR
        'dekr_w18', 'dekr_w32', 'dekr_w48',

        # CTD (COAM and Prenet)
        'ctd_coam_w32', 'ctd_coam_w48', 'ctd_coam_w48_human',
        'ctd_prenet_hrnet_w32', 'ctd_prenet_hrnet_w48',
        'ctd_prenet_rtmpose_s', 'ctd_prenet_rtmpose_m',
        'ctd_prenet_rtmpose_x', 'ctd_prenet_rtmpose_x_human',

        # DLC-specific
        'dlcrnet_stride16_ms5', 'dlcrnet_stride32_ms5',

        # RTMPose
        'rtmpose_s', 'rtmpose_m', 'rtmpose_x'
    ],
    default='resnet_50',
    help='Select the network architecture for training.'
    )
    args = parser.parse_args()

    # Check for inference arguments
    if args.inference and not (args.inference_dest and args.inference_src):
        raise Exception("If you want to infer, you need to add the desitination dir --inferece_dest and source video dir --inference_src.")
    
    utils.setup_logging()
    logging.info("Starting training...")

    # Use provided config or create new project in working-dir
    if args.config is None or not args.config.exists():
        if not args.training_src:
            raise ValueError("No config provided and no videos specified. Use --videos to provide input videos.")
        
        # Resolve all video paths to absolute before passing to DLC
        resolved_videos = [str(Path(v).resolve()) for v in args.training_src]
        logging.info("No config provided. Creating temporary project with provided videos.")
        
        args.config = Path(deeplabcut.create_new_project(
            "temp_training",
            args.scorer,
            videos=resolved_videos,
            working_directory=args.working_dir,
            copy_videos=False,
            multianimal=False
        ))

    # The working directory is either the project folder or the specified working-dir
    project_dir = args.config.parent

    # Load and modify config
    cfg = config.load_config(args.config)

    # Add bodyparts from file
    with open(args.bodyparts_file, 'r') as f:
        cfg['bodyparts'] = [line.strip() for line in f if line.strip()]
    logging.info(f"Loaded bodyparts from file: {args.bodyparts_file}")

    config.save_config(cfg, args.config)

    video_sets = {}
    # Process and copies each camera directory from the provided labeled folder
    for cam_dir in args.training_label.iterdir():
        if not cam_dir.is_dir():
            continue
        
        # Add video_sets with crop settings
        video_sets[cam_dir.name] = {"crop": [0, 320, 0, 240]}

        header, rows = data_cloner.collect_csv_rows(cam_dir)  # returns cam_header, cam_rows
        fixed_header, fixed_rows = data_cloner.prepare_rows(header, rows, cam_dir.name,args.mode)

        # Copy images/CSV in the working directory under labeled-data
        out_dir = project_dir / "labeled-data" / cam_dir.name
        data_cloner.copy_images_for_rows(args.training_label, cam_dir.name, fixed_rows, out_dir)

        out_file = out_dir / f'CollectedData_{args.scorer}.csv'
        with open(out_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(fixed_header)
            writer.writerows(fixed_rows)

        logging.info(f"Bootstrapped {len(fixed_rows)} rows for {cam_dir.name}")
        logging.info(f" → CSV saved to: {out_file}")
        logging.info(f" → Images copied into: {out_dir}")
    
    # Update video_sets in config
    cfg['video_sets'] = video_sets
    config.save_config(cfg, args.config)
    logging.info(f"Updated video_sets in config with {len(video_sets)} entries.")

    # Retriev the shuffle ID which is needed to identify the model and dataset in the API
    shuffle = args.shuffle
    
    # Convert the CSV to H5, create training dataset, and start training
    deeplabcut.convertcsv2h5(str(args.config), userfeedback=False)
    deeplabcut.create_training_dataset(str(args.config), net_type=args.net,num_shuffles=1,Shuffles=[shuffle],userfeedback=False)
    deeplabcut.train_network(str(args.config), shuffle=shuffle,epochs=args.epochs)
    
    # Infer if wanted
    if args.inference:
        inference.infer(config_path=str(args.config),video_dir=args.inference_src,video_type=args.inference_suf,
              destfolder=args.inference_dest,shuffle=shuffle)


if __name__ == '__main__':
    main()
