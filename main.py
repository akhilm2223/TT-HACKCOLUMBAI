"""
Table Tennis Match Analysis Pipeline
Tracks: ball, two players, table with net
Clean output: skeletons, ball dot, table lines, mini table

Upgraded with Hawk-Eye level table detection using:
- RANSAC-based corner detection
- Hough Line Transform for precise edge finding
- Homography for pixel-to-world coordinate mapping
- Lucas-Kanade optical flow for stability
"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import cv2
import numpy as np
import os
import json
import argparse
from collections import deque
from filterpy.kalman import KalmanFilter

# Court lines: K-means + Hough (from table_lines_detection)
from court_lines_detector import detect_table_corners, draw_court_overlay

# Optional: pose tracker and skeleton (player detection)
try:
    from modules.pose_tracker import PoseTracker, PoseDet
    from modules.visual_skeleton import draw_skeleton
    POSE_AVAILABLE = True
except ImportError:
    PoseTracker = PoseDet = draw_skeleton = None
    POSE_AVAILABLE = False
    print("[Warning] modules.pose_tracker / visual_skeleton not found. Skipping player skeletons.")

# Optional: Hawk-Eye keypoint detector
try:
    from table_keypoint_detector import TableKeypointDetector, TopDownMiniMap
    KEYPOINT_AVAILABLE = True
except ImportError:
    TableKeypointDetector = TopDownMiniMap = None
    KEYPOINT_AVAILABLE = False
    print("[Warning] table_keypoint_detector not found. Using court_lines_detector + legacy table detection.")

# Optional: Kimi K2.5 AI-powered detection
try:
    from kimi_k2_detector import KimiK2Detector, KimiK2HybridDetector
    KIMI_AVAILABLE = True
except ImportError:
    KIMI_AVAILABLE = False
    print("[Warning] Kimi K2 detector not available. Using local CV only.")


# ============================================================
# TABLE DETECTION (automatic + manual fallback)
# ============================================================

def load_table_calibration(json_path):
    """Load table calibration from JSON file."""
    if not os.path.exists(json_path):
        return None
    with open(json_path, 'r') as f:
        return json.load(f)


def auto_detect_table(frame):
    """
    Detect table tennis table using the adaptive court_lines_detector.
    Uses TTNet-inspired strategies: adaptive edges, color segmentation,
    GrabCut, and improved Hough -- no hardcoded pink/blue assumptions.
    Detects ONCE and locks.
    """
    corners = detect_table_corners(frame)
    if corners is not None:
        tw = np.linalg.norm(corners[1] - corners[0])
        th = np.linalg.norm(corners[3] - corners[0])
        aspect = tw / (th + 1e-6)
        print(f"  [table-detect] LOCKED table: {tw:.0f}x{th:.0f}, aspect={aspect:.2f}")
        return {'corners': corners}
    print("  [table-detect] Could not detect table")
    return None


def draw_table_overlay(frame, table_info):
    """Draw detected table edges and net on frame."""
    if table_info is None:
        return frame

    corners = table_info.get('corners')
    if corners is None:
        return frame

    pts = np.int32(corners)  # TL, TR, BR, BL

    # Draw table edges only (green = playing surface boundary)
    for i in range(4):
        p1 = tuple(pts[i])
        p2 = tuple(pts[(i + 1) % 4])
        cv2.line(frame, p1, p2, (0, 255, 0), 2, cv2.LINE_AA)

    # NET: thick cyan line so it's clearly separate from the table (not "net as table")
    mid_left = ((pts[0][0] + pts[3][0]) // 2, (pts[0][1] + pts[3][1]) // 2)
    mid_right = ((pts[1][0] + pts[2][0]) // 2, (pts[1][1] + pts[2][1]) // 2)
    cv2.line(frame, mid_left, mid_right, (255, 255, 0), 3, cv2.LINE_AA)  # BGR cyan
    net_center = ((mid_left[0] + mid_right[0]) // 2, (mid_left[1] + mid_right[1]) // 2)
    cv2.putText(frame, "Net", (net_center[0] - 18, net_center[1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1, cv2.LINE_AA)

    # Centre line (doubles) — thin white
    mid_top = ((pts[0][0] + pts[1][0]) // 2, (pts[0][1] + pts[1][1]) // 2)
    mid_bot = ((pts[2][0] + pts[3][0]) // 2, (pts[2][1] + pts[3][1]) // 2)
    cv2.line(frame, mid_top, mid_bot, (255, 255, 255), 1, cv2.LINE_AA)

    return frame


def draw_table_lines_from_json(frame, table_data):
    """Draw table lines from manual calibration JSON."""
    if not table_data or 'lines' not in table_data:
        return frame
    for line_name, line_data in table_data['lines'].items():
        p1 = tuple(map(int, line_data['point1']))
        p2 = tuple(map(int, line_data['point2']))
        color = (255, 255, 255) if 'net' in line_name else (0, 200, 0)
        cv2.line(frame, p1, p2, color, 2, cv2.LINE_AA)
    return frame


def create_table_homography_from_corners(corners):
    """Create homography from 4 corner points [tl, tr, br, bl]."""
    if corners is None:
        return None
    src = np.array(corners, dtype=np.float32).reshape(4, 2)
    TABLE_W, TABLE_H = 274, 152
    dst = np.array([[0, 0], [TABLE_W, 0], [TABLE_W, TABLE_H], [0, TABLE_H]], dtype=np.float32)
    return cv2.getPerspectiveTransform(src, dst)


def create_table_homography(table_data):
    """Create homography from manual calibration JSON."""
    if not table_data or 'lines' not in table_data:
        return None, None
    lines = table_data['lines']
    try:
        if 'table_top' in lines and 'table_bottom' in lines:
            tt = sorted([lines['table_top']['point1'], lines['table_top']['point2']], key=lambda p: p[0])
            tb = sorted([lines['table_bottom']['point1'], lines['table_bottom']['point2']], key=lambda p: p[0])
            tl, tr = tt[0], tt[1]
            bl, br = tb[0], tb[1]
            src = np.array([tl, tr, br, bl], dtype=np.float32)
            TABLE_W, TABLE_H = 274, 152
            dst = np.array([[0, 0], [TABLE_W, 0], [TABLE_W, TABLE_H], [0, TABLE_H]], dtype=np.float32)
            return cv2.getPerspectiveTransform(src, dst), src
        return None, None
    except Exception as e:
        print(f"Could not create table homography: {e}")
        return None, None


# ============================================================
# TABLE TENNIS BALL TRACKER (Kalman + YOLO)
# ============================================================

class TableTennisBallTracker:
    """
    Ball tracker tuned for table tennis:
    - Smaller ball (40mm), very fast
    - Uses YOLO sports_ball detection + Kalman filter
    - Bounce detection via velocity reversal
    """

    def __init__(self, fps=30):
        self.fps = fps
        self.dt = 1.0 / fps

        # Kalman: [x, y, vx, vy]
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        self.kf.F = np.array([
            [1, 0, self.dt, 0],
            [0, 1, 0, self.dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
        self.kf.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ])
        self.kf.P *= 500
        self.kf.R = np.eye(2) * 5
        self.kf.Q = np.eye(4) * 0.5

        self.initialized = False
        self.missing_frames = 0
        self.max_missing = 15
        self.bounces = []
        self.prev_vy = 0
        self.history = deque(maxlen=200)

    def update(self, detection_center, frame_num):
        """
        Update tracker with new detection.
        Returns dict with position, velocity, is_bounce, is_predicted.
        """
        if detection_center is not None:
            x, y = float(detection_center[0]), float(detection_center[1])

            if not self.initialized:
                self.kf.x = np.array([x, y, 0, 0]).reshape(4, 1)
                self.initialized = True
                self.missing_frames = 0
            else:
                # Outlier check: reject jumps > 200px
                pred = self.kf.x[:2].flatten()
                dist = np.linalg.norm([x - pred[0], y - pred[1]])
                if dist > 200 and self.missing_frames == 0:
                    # Probably noise, skip
                    self.kf.predict()
                    pos = self.kf.x[:2].flatten()
                    vel = self.kf.x[2:4].flatten()
                    self.history.append((pos[0], pos[1], frame_num))
                    return {
                        'position': (pos[0], pos[1]),
                        'velocity': (vel[0], vel[1]),
                        'is_bounce': False,
                        'is_predicted': True,
                    }

                self.kf.predict()
                self.kf.update(np.array([x, y]).reshape(2, 1))
                self.missing_frames = 0

            pos = self.kf.x[:2].flatten()
            vel = self.kf.x[2:4].flatten()

            # Bounce detection: vertical velocity sign change (going down → going up)
            is_bounce = False
            cur_vy = vel[1]
            if self.prev_vy > 2 and cur_vy < -1:
                is_bounce = True
                self.bounces.append({
                    'frame': frame_num,
                    'image_xy': (pos[0], pos[1]),
                })
            self.prev_vy = cur_vy

            self.history.append((pos[0], pos[1], frame_num))
            return {
                'position': (pos[0], pos[1]),
                'velocity': (vel[0], vel[1]),
                'is_bounce': is_bounce,
                'is_predicted': False,
            }

        else:
            # No detection
            if not self.initialized:
                return {'position': None, 'velocity': None, 'is_bounce': False, 'is_predicted': False}

            self.missing_frames += 1
            if self.missing_frames > self.max_missing:
                return {'position': None, 'velocity': None, 'is_bounce': False, 'is_predicted': True}

            self.kf.predict()
            pos = self.kf.x[:2].flatten()
            vel = self.kf.x[2:4].flatten()
            self.history.append((pos[0], pos[1], frame_num))
            return {
                'position': (pos[0], pos[1]),
                'velocity': (vel[0], vel[1]),
                'is_bounce': False,
                'is_predicted': True,
            }

    def get_bounces(self):
        return self.bounces


# ============================================================
# MINI TABLE (small overlay, only bounce dots)
# ============================================================

class MiniTable:
    """Small table overlay showing only where ball bounced."""

    def __init__(self, homography, width=80, height=48):
        self.H = homography
        self.width = width
        self.height = height
        self.pad = 4
        self.dw = width - 2 * self.pad
        self.dh = height - 2 * self.pad
        # Table tennis: 274 x 152 units
        self.table_w = 274.0
        self.table_h = 152.0

    def draw(self, bounces):
        canvas = np.full((self.height, self.width, 3), (40, 80, 40), dtype=np.uint8)
        cx, cy = self.pad, self.pad

        # Table surface (blue, like real table)
        cv2.rectangle(canvas, (cx, cy), (cx + self.dw, cy + self.dh), (140, 80, 20), -1)
        # Border
        cv2.rectangle(canvas, (cx, cy), (cx + self.dw, cy + self.dh), (255, 255, 255), 1)
        # Net (horizontal center)
        net_y = cy + self.dh // 2
        cv2.line(canvas, (cx, net_y), (cx + self.dw, net_y), (255, 255, 255), 1)
        # Center line (vertical, for doubles)
        mid_x = cx + self.dw // 2
        cv2.line(canvas, (mid_x, cy), (mid_x, cy + self.dh), (200, 200, 200), 1)

        # Bounce dots
        for bounce in bounces:
            image_xy = bounce.get('image_xy') if isinstance(bounce, dict) else None
            if image_xy is None:
                continue
            mini_pos = self._to_mini(image_xy)
            if mini_pos:
                cv2.circle(canvas, mini_pos, 2, (0, 255, 255), -1)
                cv2.circle(canvas, mini_pos, 2, (255, 255, 255), 1)

        return canvas

    def _to_mini(self, image_xy):
        """Convert image pixel to mini table pixel using homography."""
        if self.H is None or image_xy is None:
            return None
        try:
            pt = np.array([[[float(image_xy[0]), float(image_xy[1])]]], dtype=np.float32)
            t = cv2.perspectiveTransform(pt, self.H)
            tx, ty = t[0][0]
            nx = tx / self.table_w
            ny = ty / self.table_h
            nx = max(0, min(1, nx))
            ny = max(0, min(1, ny))
            mx = int(self.pad + nx * self.dw)
            my = int(self.pad + ny * self.dh)
            return (mx, my)
        except:
            return None

    def overlay(self, frame, position='top_right', margin=10):
        mini = self.draw(self.last_bounces if hasattr(self, 'last_bounces') else [])
        h, w = frame.shape[:2]
        mh, mw = mini.shape[:2]
        if position == 'top_right':
            y1, x1 = margin, w - mw - margin
        else:
            y1, x1 = margin, margin
        y2, x2 = y1 + mh, x1 + mw
        y1, y2 = max(0, y1), min(h, y2)
        x1, x2 = max(0, x1), min(w, x2)
        rh, rw = y2 - y1, x2 - x1
        if mini.shape[0] != rh or mini.shape[1] != rw:
            mini = cv2.resize(mini, (rw, rh))
        try:
            frame[y1:y2, x1:x2] = cv2.addWeighted(frame[y1:y2, x1:x2], 0.15, mini, 0.85, 0)
        except:
            frame[y1:y2, x1:x2] = mini
        return frame


# ============================================================
# BALL DETECTOR (YOLO, tuned for small table tennis ball)
# ============================================================

class TableTennisBallDetector:
    """
    Frame-differencing + color filtering ball detector.
    Works by:
      1. Compute difference between consecutive frames (motion)
      2. Filter for bright/white or orange pixels (ball color)
      3. Find small circular contours in the intersection
      4. If previous position known, prefer candidates near it
    No deep learning model needed - works on any table tennis ball.
    """

    def __init__(self):
        self.prev_gray = None
        self.prev_prev_gray = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120, varThreshold=40, detectShadows=False
        )
        # Morphology kernel for cleaning masks
        self.kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.kernel_med = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.frame_count = 0

    def detect(self, frame, prev_center=None):
        """
        Detect table tennis ball using motion + appearance.
        Returns {'center': (x,y), 'conf': float, 'bbox': ...} or None.
        """
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.frame_count += 1

        # --- 1. Motion mask from frame differencing ---
        motion_mask = np.zeros((h, w), dtype=np.uint8)

        if self.prev_gray is not None:
            diff1 = cv2.absdiff(gray, self.prev_gray)
            _, motion1 = cv2.threshold(diff1, 20, 255, cv2.THRESH_BINARY)
            motion_mask = motion1

            if self.prev_prev_gray is not None:
                diff2 = cv2.absdiff(gray, self.prev_prev_gray)
                _, motion2 = cv2.threshold(diff2, 20, 255, cv2.THRESH_BINARY)
                # Union of both diffs for better coverage
                motion_mask = cv2.bitwise_or(motion1, motion2)

        # Also use background subtractor
        fg_mask = self.bg_subtractor.apply(frame, learningRate=0.005)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)

        # Combine: motion OR foreground
        combined_motion = cv2.bitwise_or(motion_mask, fg_mask)

        # --- 2. Color mask: bright/white ball or orange ball ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # White ball: high value, low saturation
        white_mask = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 80, 255]))

        # Orange ball: typical orange hue
        orange_mask = cv2.inRange(hsv, np.array([5, 100, 150]), np.array([25, 255, 255]))

        # Bright yellow ball
        yellow_mask = cv2.inRange(hsv, np.array([20, 80, 180]), np.array([40, 255, 255]))

        color_mask = cv2.bitwise_or(white_mask, cv2.bitwise_or(orange_mask, yellow_mask))

        # --- 3. Intersection: moving + ball-colored ---
        ball_mask = cv2.bitwise_and(combined_motion, color_mask)

        # Clean up
        ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_OPEN, self.kernel_small)
        ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_CLOSE, self.kernel_med)

        # Update history
        self.prev_prev_gray = self.prev_gray
        self.prev_gray = gray.copy()

        # Skip first 2 frames (need history for differencing)
        if self.frame_count < 3:
            return None

        # --- 4. Find contours ---
        contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Ball is tiny: typically 10-800 px area depending on resolution
            if area < 4 or area > 1500:
                continue

            # Check circularity
            peri = cv2.arcLength(cnt, True)
            if peri == 0:
                continue
            circularity = 4 * np.pi * area / (peri * peri)
            if circularity < 0.25:  # Not round enough
                continue

            # Get centroid
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]

            # Bounding rect
            x, y, bw, bh = cv2.boundingRect(cnt)
            # Aspect ratio check
            if bw > 0 and bh > 0:
                aspect = max(bw, bh) / min(bw, bh)
                if aspect > 3.0:
                    continue

            # Score: circularity * area-based score
            # Prefer medium-sized blobs (not too tiny, not big)
            size_score = min(area, 400) / 400.0
            conf = circularity * 0.6 + size_score * 0.4

            candidates.append({
                'center': (cx, cy),
                'conf': conf,
                'bbox': (float(x), float(y), float(x + bw), float(y + bh)),
                'area': area,
            })

        if not candidates:
            # Fallback: use motion-only mask for very bright spots
            bright_motion = cv2.bitwise_and(combined_motion, white_mask)
            bright_motion = cv2.morphologyEx(bright_motion, cv2.MORPH_OPEN, self.kernel_small)
            contours2, _ = cv2.findContours(bright_motion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours2:
                area = cv2.contourArea(cnt)
                if 3 <= area <= 2000:
                    M = cv2.moments(cnt)
                    if M["m00"] == 0:
                        continue
                    cx = M["m10"] / M["m00"]
                    cy = M["m01"] / M["m00"]
                    x, y, bw, bh = cv2.boundingRect(cnt)
                    candidates.append({
                        'center': (cx, cy),
                        'conf': 0.3,
                        'bbox': (float(x), float(y), float(x + bw), float(y + bh)),
                        'area': area,
                    })

        if not candidates:
            return None

        # --- 5. Pick best candidate ---
        if prev_center is not None:
            # Prefer candidates near previous position (within search radius)
            max_dist = 150
            near_candidates = []
            for c in candidates:
                dist = np.sqrt((c['center'][0] - prev_center[0])**2 +
                               (c['center'][1] - prev_center[1])**2)
                if dist < max_dist:
                    # Boost score for closer candidates
                    proximity_score = 1.0 - (dist / max_dist)
                    c['conf'] = c['conf'] * 0.5 + proximity_score * 0.5
                    near_candidates.append(c)

            if near_candidates:
                return max(near_candidates, key=lambda c: c['conf'])

        # No previous position or nothing nearby: return highest confidence
        return max(candidates, key=lambda c: c['conf'])


# ============================================================
# MAIN PIPELINE
# ============================================================

def main(video_path, output_path=None, table_calibration_path=None, show_preview=True, use_kimi=False):
    """
    Table tennis analysis pipeline.

    Args:
        video_path: Input video
        output_path: Output video path
        table_calibration_path: JSON with table line calibration
        show_preview: Show live preview window
        use_kimi: Use Kimi K2.5 AI for detection
    """
    print("=" * 60)
    print("TABLE TENNIS ANALYSIS PIPELINE")
    if use_kimi:
        print("MODE: Kimi K2.5 AI-Powered Detection")
    else:
        print("MODE: Local CV Detection")
    print("=" * 60)

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    # Apply rotation metadata so output matches how the video is meant to be viewed
    # (fixes "video small then zooms out" when source has portrait/rotation tag)
    ORIENT_AUTO = getattr(cv2, 'CAP_PROP_ORIENTATION_AUTO', 49)
    try:
        cap.set(ORIENT_AUTO, 1)
    except Exception:
        pass

    # Get output size from first frame so it's consistent (no size change / zoom effect)
    ret_probe, probe_frame = cap.read()
    if ret_probe and probe_frame is not None:
        height, width = probe_frame.shape[0], probe_frame.shape[1]
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    else:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video: {width}x{height} @ {fps}fps, {total_frames} frames ({total_frames/fps:.1f}s)")

    # Output (fixed size = no "small then zoom out")
    if output_path is None:
        output_path = "output_videos/table_tennis_analysis.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    out_size = (width, height)  # (w, h) for resize

    # --- TABLE DETECTION ---
    # Priority: 1) Kimi K2  2) manual JSON  3) Hawk-Eye keypoint (if available)
    #           4) Court lines (K-means + Hough from table_lines_detection)  5) legacy pink
    table_data = None
    table_info = None  # {'corners': np.array (4,2)} for overlay + homography
    homography = None
    calib_path = table_calibration_path or "table_lines.json"

    keypoint_detector = None
    kimi_detector = None
    keypoint_result = None
    use_keypoint_detector = False
    continuous_tracking = True
    if KEYPOINT_AVAILABLE:
        keypoint_detector = TableKeypointDetector(debug=False, fps=fps)
        use_keypoint_detector = True

    # === KIMI K2 DETECTION ===
    if use_kimi and KIMI_AVAILABLE:
        try:
            kimi_detector = KimiK2HybridDetector(redetect_every=90)
            print("[Kimi K2] AI detector initialized")
            ret_f, first_frame = cap.read()
            if ret_f:
                print("[Kimi K2] Analyzing first frame...")
                kimi_result = kimi_detector.detect(first_frame)
                if kimi_result.get('locked') and kimi_result.get('corners') is not None:
                    print(f"  [Kimi K2] Table detected! Method: {kimi_result.get('method')}")
                    homography = kimi_result['homography']
                    table_info = {'corners': kimi_result['corners']}
                    use_keypoint_detector = False
                else:
                    kimi_detector = None
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        except Exception as e:
            print(f"[Kimi K2] Error: {e}")
            kimi_detector = None

    # === LOCAL CV DETECTION (fallback) ===
    if table_info is None and homography is None:
        if os.path.exists(calib_path):
            table_data = load_table_calibration(calib_path)
            print(f"Loaded manual table calibration: {calib_path}")
            homography, _ = create_table_homography(table_data)
            use_keypoint_detector = False
        else:
            # Try multiple frames (some frames may have occlusion/motion blur)
            retry_frames = [0, 30, 60, 90, 150]
            for try_frame_idx in retry_frames:
                cap.set(cv2.CAP_PROP_POS_FRAMES, try_frame_idx)
                ret_f, try_frame = cap.read()
                if not ret_f:
                    continue
                # 1) Try Hawk-Eye keypoint detector if available
                if use_keypoint_detector and keypoint_detector is not None and table_info is None:
                    keypoint_result = keypoint_detector.detect(try_frame)
                    if keypoint_result.get('locked') and keypoint_result.get('corners') is not None:
                        print(f"[Hawk-Eye] Table detected at frame {try_frame_idx}")
                        homography = keypoint_result['homography']
                        table_info = {'corners': keypoint_result['corners']}
                        use_keypoint_detector = True
                        break
                # 2) Court lines: 8-strategy adaptive detector
                if table_info is None:
                    print(f"Running adaptive court detection (frame {try_frame_idx})...")
                    court_corners = detect_table_corners(try_frame)
                    if court_corners is not None:
                        table_info = {'corners': court_corners}
                        homography = create_table_homography_from_corners(court_corners)
                        use_keypoint_detector = False
                        break
                    else:
                        print(f"  Detection failed on frame {try_frame_idx}, trying next...")
            if table_info is None:
                print("  Court detection failed on all attempted frames.")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Initialize mini-map
    mini_table = None
    top_down_map = None
    if homography is not None:
        if use_keypoint_detector and KEYPOINT_AVAILABLE and keypoint_detector is not None:
            top_down_map = TopDownMiniMap(width=140, height=77)
            print("[Hawk-Eye] Top-down mini-map enabled")
        else:
            mini_table = MiniTable(homography)
            print("Mini table overlay enabled")

    # Ball detector + tracker
    ball_detector = TableTennisBallDetector()
    ball_tracker = TableTennisBallTracker(fps=fps)
    print("Ball detector (frame-diff + color) + Kalman tracker initialized")

    # Pose tracker (optional)
    pose_tracker = None
    if POSE_AVAILABLE and PoseTracker is not None:
        pose_tracker = PoseTracker(width, height, min_conf=0.3, smooth=15, num_players=2)
        print("Pose tracker initialized (both players: skeleton)")
    else:
        print("Pose tracker skipped (module not available).")

    # Tracking state
    frame_count = 0
    last_ball_center = None
    ball_trail = deque(maxlen=60)
    COLOR_P1 = (0, 0, 255)    # Red
    COLOR_P2 = (255, 0, 0)    # Blue

    print(f"\nProcessing {total_frames} frames...")
    print("-" * 60)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            if frame_count % 30 == 0:
                pct = frame_count / total_frames * 100
                print(f"  {pct:.0f}% ({frame_count}/{total_frames})", end='\r')

            # --- POSE TRACKING: both players get skeleton (if available) ---
            pose_L, pose_R = (None, None)
            if pose_tracker is not None:
                pose_L, pose_R = pose_tracker.detect_two(frame)

            # --- TABLE TRACKING ---
            kimi_ball_center = None
            if kimi_detector is not None and frame_count % 30 == 0:
                try:
                    ball_result = kimi_detector.kimi.detect_ball(frame)
                    if ball_result and ball_result.get('ball_found'):
                        kimi_ball_center = tuple(ball_result['center'])
                except Exception:
                    pass

            # Keypoint-based table tracking (if detector available and in use)
            if use_keypoint_detector and keypoint_detector is not None and continuous_tracking:
                try:
                    keypoint_result = keypoint_detector.detect_and_update(frame, kimi_detector=kimi_detector)
                    if keypoint_result.get('corners') is not None:
                        homography = keypoint_result['homography']
                except Exception:
                    pass

            # --- BALL DETECTION ---
            # Use Kimi detection if available, otherwise fall back to local CV
            if kimi_ball_center is not None:
                ball_center = kimi_ball_center
            else:
                ball_det = ball_detector.detect(frame, prev_center=last_ball_center)
                ball_center = ball_det['center'] if ball_det else None

            result = ball_tracker.update(ball_center, frame_count)
            ball_pos = result['position']
            is_bounce = result['is_bounce']
            is_predicted = result['is_predicted']

            if ball_pos:
                last_ball_center = ball_pos
                ball_trail.append(ball_pos)

            # --- DRAW ---

            # 1. Player skeletons (if pose tracker available)
            if POSE_AVAILABLE and draw_skeleton is not None:
                if pose_L:
                    draw_skeleton(frame, pose_L, COLOR_P1, "",
                                  draw_joints=True, draw_bones=True,
                                  draw_centroid=True, draw_bbox=False,
                                  bone_thickness=2, joint_radius=3)
                if pose_R:
                    draw_skeleton(frame, pose_R, COLOR_P2, "",
                                  draw_joints=True, draw_bones=True,
                                  draw_centroid=True, draw_bbox=False,
                                  bone_thickness=2, joint_radius=3)

            # 2. Table / court overlay (keypoint, manual JSON, or K-means+Hough/legacy corners)
            if use_keypoint_detector and keypoint_detector is not None and getattr(keypoint_detector, 'corners', None) is not None:
                frame = keypoint_detector.draw_overlay(frame, show_corners=True)
            elif table_data:
                frame = draw_table_lines_from_json(frame, table_data)
            elif table_info is not None and table_info.get('corners') is not None:
                frame = draw_court_overlay(frame, table_info['corners'], color=(0, 255, 0), thickness=2)

            # 4. Ball: small yellow circle
            if ball_pos:
                bx, by = int(ball_pos[0]), int(ball_pos[1])
                if is_bounce:
                    cv2.circle(frame, (bx, by), 7, (0, 255, 255), -1)
                    cv2.circle(frame, (bx, by), 8, (255, 255, 255), 1)
                else:
                    cv2.circle(frame, (bx, by), 5, (0, 255, 255), -1)
                    cv2.circle(frame, (bx, by), 6, (255, 255, 255), 1)

            # 5. Mini table / Top-down map
            if top_down_map is not None and keypoint_detector is not None:
                bounces_world = []
                for b in ball_tracker.get_bounces():
                    world_xy = keypoint_detector.pixel_to_world(b['image_xy'])
                    if world_xy:
                        bounces_world.append({'world_xy': world_xy})
                current_ball_world = keypoint_detector.pixel_to_world(ball_pos) if ball_pos else None
                mini_img = top_down_map.render(bounces=bounces_world, current_ball=current_ball_world)
                frame = top_down_map.overlay_on_frame(frame, mini_img, position='top_right')
            elif mini_table is not None:
                mini_table.last_bounces = ball_tracker.get_bounces()
                mini_img = mini_table.draw(mini_table.last_bounces)
                h_f, w_f = frame.shape[:2]
                mh, mw = mini_img.shape[:2]
                mx1 = w_f - mw - 10
                my1 = 10
                mx2, my2 = mx1 + mw, my1 + mh
                if mx1 >= 0 and my2 <= h_f:
                    try:
                        frame[my1:my2, mx1:mx2] = cv2.addWeighted(
                            frame[my1:my2, mx1:mx2], 0.15, mini_img, 0.85, 0)
                    except:
                        frame[my1:my2, mx1:mx2] = mini_img

            # Write frame (ensure fixed size so no "small then zoom out" in playback)
            if frame.shape[1] != out_size[0] or frame.shape[0] != out_size[1]:
                frame = cv2.resize(frame, out_size, interpolation=cv2.INTER_LINEAR)
            out.write(frame)

            # Preview
            if show_preview:
                cv2.imshow('Table Tennis Analysis (Q to quit)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted")

    # Cleanup
    cap.release()
    out.release()
    if show_preview:
        cv2.destroyAllWindows()

    print(f"\n{'=' * 60}")
    print(f"Done! {frame_count} frames processed")
    print(f"Bounces detected: {len(ball_tracker.get_bounces())}")
    print(f"Output: {output_path}")
    print(f"{'=' * 60}")

    # Save analysis JSON
    json_path = output_path.replace('.mp4', '.json').replace('.avi', '.json')
    analysis = {
        'video': video_path,
        'frames': frame_count,
        'fps': fps,
        'bounces': [
            {'frame': b['frame'], 'x': float(b['image_xy'][0]), 'y': float(b['image_xy'][1])}
            for b in ball_tracker.get_bounces()
        ],
    }
    with open(json_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"Analysis JSON: {json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Table Tennis Analysis Pipeline')
    parser.add_argument('--video', type=str, default='Recording 2026-02-05 165944.mp4',
                        help='Input video path (default: Recording 2026-02-05 165944.mp4)')
    parser.add_argument('--output', type=str, default=None, help='Output video path')
    parser.add_argument('--table-lines', type=str, default=None,
                        help='Table calibration JSON (default: table_lines.json)')
    parser.add_argument('--no-preview', action='store_true', help='Disable live preview')
    parser.add_argument('--kimi', action='store_true',
                        help='Use Kimi K2.5 AI for table/ball detection (requires MOONSHOT_API_KEY)')

    args = parser.parse_args()

    main(args.video, args.output,
         table_calibration_path=args.table_lines,
         show_preview=not args.no_preview,
         use_kimi=args.kimi)
