"""
Use TTNet (from tt/) to detect the table via segmentation — same code as tt/src.
Returns 4 corners [TL, TR, BR, BL] from the "table" channel of TTNet's segmentation.
Requires: tt/ folder, PyTorch, and a TTNet pretrained checkpoint.
"""
import os
import sys

import cv2
import numpy as np

# TTNet lives in tt/src
_tt_src = os.path.join(os.path.dirname(__file__), "tt", "src")
if os.path.isdir(_tt_src):
    if _tt_src not in sys.path:
        sys.path.insert(0, _tt_src)
else:
    _tt_src = None

# Segmentation output: 3 channels = human, table, scoreboard (TTNet paper)
TABLE_CHANNEL_INDEX = 1


def _make_ttnet_config(device="cuda", gpu_idx=0):
    """Minimal config to create TTNet model (no argparse, no easydict)."""
    import torch
    class C:
        pass
    o = C()
    o.arch = "ttnet"
    o.dropout_p = 0.5
    o.tasks = ["global", "local", "event", "seg"]
    o.input_size = (320, 128)
    o.thresh_ball_pos_mask = 0.05
    o.num_frames_sequence = 9
    o.multitask_learning = False
    o.tasks_loss_weight = [1.0, 1.0, 1.0, 1.0]
    o.events_weights_loss = (1.0, 3.0)
    o.num_events = 2
    o.sigma = 1.0
    o.device = torch.device("cpu" if device == "cpu" else f"cuda:{gpu_idx}")
    o.gpu_idx = gpu_idx
    return o


def _order_corners(pts):
    """Order 4 points as TL, TR, BR, BL."""
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).flatten()
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(d)]
    bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def detect_table_corners_ttnet(video_path, checkpoint_path, frame_height=None, frame_width=None,
                               device="cuda", gpu_idx=0, seg_thresh=0.5):
    """
    Use TTNet segmentation (same code as tt) to get table mask, then extract 4 corners.

    Args:
        video_path: path to video file
        checkpoint_path: path to TTNet .pth checkpoint (required)
        frame_height, frame_width: original video size (for resizing mask). If None, from video.
        device: 'cuda' or 'cpu'
        gpu_idx: GPU index if cuda
        seg_thresh: threshold for segmentation mask

    Returns:
        np.array (4, 2) [TL, TR, BR, BL] in pixel coords, or None if failed.
    """
    if _tt_src is None:
        print("[TTNet] tt/src not found. Install tt (TTNet) repo in project.")
        return None
    if not os.path.isfile(checkpoint_path):
        print(f"[TTNet] Checkpoint not found: {checkpoint_path}")
        return None

    import torch

    # Config and model (same as tt/src)
    configs = _make_ttnet_config(device=device, gpu_idx=gpu_idx)
    from models.model_utils import create_model, load_pretrained_model

    model = create_model(configs)
    model = load_pretrained_model(model, checkpoint_path, gpu_idx, overwrite_global_2_local=False)
    model.eval()
    if configs.device.type == "cuda":
        model = model.cuda(configs.gpu_idx)

    # Load first 9-frame sequence from video (same as tt TTNet_Video_Loader)
    from data_process.ttnet_video_loader import TTNet_Video_Loader

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[TTNet] Could not open video:", video_path)
        return None
    if frame_width is None or frame_height is None:
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    video_loader = TTNet_Video_Loader(
        video_path,
        input_size=configs.input_size,
        num_frames_sequence=configs.num_frames_sequence,
    )
    try:
        count, resized_imgs = next(iter(video_loader))
    except (StopIteration, Exception) as e:
        print("[TTNet] Failed to load first frame sequence:", e)
        return None

    # (27, 128, 320) float, RGB
    resized_imgs = torch.from_numpy(resized_imgs).to(configs.device).float().unsqueeze(0)
    with torch.no_grad():
        pred_ball_global, pred_ball_local, pred_events, pred_seg = model.run_demo(resized_imgs)

    # Same post-processing as tt/src
    from utils.post_processing import get_prediction_seg

    prediction_seg = get_prediction_seg(pred_seg, seg_thresh)
    # prediction_seg: (H, W, 3) int 0/1 — channels: human, table, scoreboard
    if prediction_seg.ndim == 3:
        table_mask = prediction_seg[:, :, TABLE_CHANNEL_INDEX]
    else:
        table_mask = prediction_seg

    # Resize to original frame size
    table_mask = (table_mask * 255).astype(np.uint8)
    table_mask = cv2.resize(table_mask, (frame_width, frame_height), interpolation=cv2.INTER_NEAREST)
    _, table_bin = cv2.threshold(table_mask, 127, 255, cv2.THRESH_BINARY)

    # Largest contour -> 4 corners (minAreaRect or approxPolyDP)
    contours, _ = cv2.findContours(table_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("[TTNet] No table contour in segmentation mask.")
        return None
    cnt = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(cnt)
    if area < 500:
        print("[TTNet] Table contour too small.")
        return None

    # Prefer 4-vertex approx for table quad
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    if len(approx) >= 4:
        # Take 4 corners (or reduce to 4 via minAreaRect)
        pts = approx.reshape(-1, 2).astype(np.float32)
        if len(pts) > 4:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            pts = box
        corners = _order_corners(pts)
    else:
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        corners = _order_corners(box)

    # Sanity: aspect and size
    w1 = np.linalg.norm(corners[1] - corners[0])
    w2 = np.linalg.norm(corners[2] - corners[3])
    h1 = np.linalg.norm(corners[3] - corners[0])
    h2 = np.linalg.norm(corners[2] - corners[1])
    tw = (w1 + w2) / 2
    th = (h1 + h2) / 2
    if tw < 40 or th < 20:
        return None
    aspect = tw / (th + 1e-6)
    if aspect < 1.2 or aspect > 4.5:
        return None

    print(f"[TTNet] Table from segmentation: {tw:.0f}x{th:.0f} px, aspect {aspect:.2f}")
    return corners


def is_available():
    """Return True if TTNet (tt/src) and checkpoint can be used."""
    if _tt_src is None:
        return False
    try:
        import torch
        from models.model_utils import create_model
        _make_ttnet_config(device="cpu", gpu_idx=0)
        return True
    except Exception:
        return False
