## CLI Model Trainer for DLC
A CLI tool, with which you can directly train different DLC models in the CLI.

### Intended Use
This tool exist to provide a baseline method to use DLC without depending on the GUI.

### Usage
In the Examples/DLCPipeline directory, example files are given to give guidance to the requried formats.
After following the installation instructions from the README in the code/ directory. Invoke as such in your virtual environment with installed RZ* packages:

#### Case 1: No current project no inference
```bash
rztrain \
    --bodyparts-file /path/to/bodyparts.txt \
    --training-label /path/to/labeled_data \
    --training-src /path/to/videos
    --shuffle Int
```

#### Case 2: No current project with inference
```bash
rztrain \
    --bodyparts-file /path/to/bodyparts.txt \
    --training-label /path/to/labeled_data \
    --training-src /path/to/videos
    --shuffle Int
    --inference True
    --inference-dest /path/to/save/csv
    --inference-src /path/to/videos
    --inference-suf ["avi", "mp4", "mov", "mpeg", "mkv"]
```

#### Case 3: Current project no inference
```bash
rztrain \
    --bodyparts-file /path/to/bodyparts.txt \
    --training-label /path/to/labeled_data \
    --working-dir /path/to/config.yaml
    --shuffle Int
```

#### Case 4: Current project with inference
```bash
rztrain \
    --bodyparts-file /path/to/bodyparts.txt \
    --training-label /path/to/labeled_data \
    --working-dir /path/to/config.yaml
    --shuffle Int
    --inference True
    --inference-dest /path/to/save/csv
    --inference-src /path/to/videos
    --inference-suf ["avi", "mp4", "mov", "mpeg", "mkv"]
```
#### Case 5: Inference only
```bash
rzinfer \
    --bodyparts-file /path/to/bodyparts.txt \
    --training-label /path/to/labeled_data \
    --working-dir /path/to/config.yaml
    --shuffle Int
    --inference True
    --inference-dest /path/to/save/csv
    --inference-src /path/to/videos
    --inference-suf ["avi", "mp4", "mov", "mpeg", "mkv"]
```

For additional informations about the full argument set and its purposes, run:
```bash
rztrain --help
```
```bash
rzinfer --help
```

### Testing on example data
This script has to be run from the project root.
```bash
rztrain --bodyparts-file Examples/DLCPipeline/bodyparts.txt --training-label Examples/DLCPipeline/labeled_data/     --training-src Examples/DLCPipeline/dummy.mp4 --shuffle 1 --inference True --inference-dest Examples/DLCPipeline/inference_output/ --inference-src Examples/DLCPipeline/inference_videos/ --inference-suf avi
```
