## CLI Evaluation Tool (`rzplot`, `rzshare`)

A command-line interface for **quantitative evaluation of 2D reprojections** against **ground-truth 2D annotations**.  
The tool computes **per-joint**, **per-camera**, and **global** error statistics and produces **plots** and CSV summaries.

Supported metrics:
- **L1** (mean absolute pixel error)
- **L2** (Euclidean pixel error)
- **RMSE**

---

### Intended Use

This tool is intended to evaluate:
- 2D reprojections from **triangulation**
- Results of **bundle adjustment**
- Results of **temporal smoothing** (e.g. RodenZ)

Evaluation is performed by comparing reprojected 2D keypoints against **ground-truth DLC annotations** for each camera.

---

### Input Requirements

- **Reprojection CSVs**  
  One CSV per camera, containing:
  - `frame`
  - `joint`
  - `x`, `y`
  - `camera`

- **Ground-truth CSVs**  
  DLC-style CSVs (`CollectedData_*.csv`) with multi-index headers.

- **Camera mapping**  
  Cameras must be provided in the same order as reprojection and GT files.

---

### Usage

#### `rzplot` – Reprojection vs Ground Truth Evaluation

```bash
rzplot \
  --rp <reprojection_cam1.csv> <reprojection_cam2.csv> ... \
  --gt <gt_cam1.csv> <gt_cam2.csv> ... \
  --cams <cam_id_1> <cam_id_2> ... \
  --out <output_directory>
```

#### `rzshare` – Shared Distribution Comparison
rzshare overlays L1/L2 error distributions from multiple evaluations.into a single figure.
```bash
rzshare \
  --csvs <l1_l2_dist_1.csv> <l1_l2_dist_2.csv> ... \
  --names <Name1> <Name2> ... \
  --metric (l1|l2) \
  --out <output.png> \
  --colors <color1> <color2> ...
```