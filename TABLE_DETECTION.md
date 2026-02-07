# Table & Net Detection — What to Use

Your current **classical CV** detector (pink/white lines, Hough) is failing on this video: it draws a big wrong polygon and doesn’t match the real table or net. To get **correct table + net** you have two practical options.

---

## Option 1: Use a model (best accuracy)

### Model to use: **TTNet** (already in `tt/`)

- **What it does:** Segments each frame into **human**, **table**, **scoreboard**. The **table** channel is the playing surface; the net is the **middle** of that (we draw it as the line between left and right midpoints).
- **Where it is:** `tt/` (TTNet-Real-time-Analysis-System-for-Table-Tennis-Pytorch).
- **What you need:** A **pretrained checkpoint** (`.pth`). The official repo does **not** provide one; you must either train it or find community weights.

**Steps:**

1. **Get a TTNet checkpoint**
   - **Train yourself:** Use the dataset and scripts in `tt/` (see `tt/README.md`, `prepare_dataset/`, `train_1st_phase.sh` etc.). You need the TTNet dataset (table tennis frames + segmentation masks).
   - **Or search:** Look for “TTNet pretrained”, “TTNet weights”, “TTNet checkpoint” on GitHub / Papers With Code. Someone may have shared weights.

2. **Put the checkpoint in your project**  
   e.g. `tt/checkpoints/ttnet_best.pth`

3. **Run the pipeline with TTNet for table**
   ```bash
   py -3 main.py --video "your_video.mp4" --ttnet
   # or with explicit checkpoint:
   py -3 main.py --video "your_video.mp4" --ttnet --ttnet-checkpoint tt/checkpoints/ttnet_best.pth
   ```

4. **What you get:** Table from the **table** segmentation; net drawn as the **middle line** of that table. No separate “net” class in TTNet — net = midline of the table box.

**Other models (alternatives):**

- **Generic segmentation (e.g. DeepLab, Segment Anything):** Only useful if you have (or train) a “table” or “table tennis table” class. Not plug-and-play for table tennis.
- **Object detection (YOLO, etc.):** Could detect “table” as a box; you’d still need a trained or fine-tuned model for table tennis. TTNet is already designed for this.

So: **use TTNet for table (and thus net as midline)**; you only need to get a `.pth` checkpoint.

---

## Option 2: Manual calibration (works immediately, no model)

If you don’t have a TTNet checkpoint, you can **define the table once** by clicking the 4 corners. The pipeline then uses that for every frame and draws the **net as the line between the left and right midpoints** of that quad.

**Steps:**

1. **Run the calibration script** on your video:
   ```bash
   py -3 calibrate_table.py --video "Recording 2026-02-05 165944.mp4"
   ```
2. **Click the 4 corners** in order: **1 = Top-Left, 2 = Top-Right, 3 = Bottom-Right, 4 = Bottom-Left** (the table rectangle only). Press **R** to clear and re-click, **S** to save, **Q** to quit.
3. The script saves **`table_lines.json`** in the project folder.
4. **Run the main pipeline** with that file:
   ```bash
   py -3 main.py --video "Recording 2026-02-05 165944.mp4" --table-lines table_lines.json
   ```

You’ll get **correct table boundaries + net** (net = cyan line between left and right midpoints), no model required.

---

## Summary

| Goal                     | What to use              | What you need                    |
|--------------------------|--------------------------|----------------------------------|
| **See table + net right**| **TTNet** (model)        | TTNet pretrained `.pth`          |
| **See table + net right**| **Manual calibration**   | One-time click 4 corners        |

- **Net:** In both options the **net is the line in the middle** of the table (between the two long sides). We don’t use a separate “net” model; table first, then net = midline.
- **Models to use:** For table (and thus net), use **TTNet**. For ball/players you already have your current detectors; no extra model is required for “see table first” beyond TTNet or manual calibration.
