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

# Optional: pose tracker (deferred import so K2 runs first and mediapipe/PortAudio don't block startup)
POSE_AVAILABLE = False
PoseTracker = PoseDet = draw_skeleton = None
_pose_loaded = False

def _ensure_pose_tracker():
    global POSE_AVAILABLE, PoseTracker, PoseDet, draw_skeleton, _pose_loaded
    if _pose_loaded:
        return POSE_AVAILABLE
    _pose_loaded = True
    try:
        from modules.pose_tracker import PoseTracker as _PT, PoseDet as _PD
        from modules.visual_skeleton import draw_skeleton as _DS
        PoseTracker, PoseDet, draw_skeleton = _PT, _PD, _DS
        POSE_AVAILABLE = True
    except Exception as e:
        print("[Warning] Pose tracker not available:", e)
    return POSE_AVAILABLE

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

# Optional: TTNet (tt/) for table detection via segmentation (same code as tt)
try:
    from tt_table_detector import detect_table_corners_ttnet, is_available as ttnet_available
    TTNET_TABLE_AVAILABLE = ttnet_available()
except ImportError:
    detect_table_corners_ttnet = None
    TTNET_TABLE_AVAILABLE = False

# Optional: Snowflake (match + analysis storage for K2 / analytics)
DB_AVAILABLE = False
TrackingDB = None
try:
    from modules.snowflake_db import TrackingDB
    DB_AVAILABLE = bool(os.getenv("SNOWFLAKE_ACCOUNT") and os.getenv("SNOWFLAKE_USER"))
except ImportError:
    pass


# Optional: Database (Snowflake)
try:
    from modules.snowflake_db import TrackingDB
    DB_AVAILABLE = True
except ImportError:
    try:
        from snowflake_db import TrackingDB
        DB_AVAILABLE = True
    except ImportError:
        TrackingDB = None
        DB_AVAILABLE = False
        print("[Warning] Database module not found. DB features disabled.")

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
    result = detect_table_corners(frame)
    corners = result[0] if isinstance(result, tuple) else result
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
    """Draw table lines from manual calibration JSON + net (cyan) between left/right midpoints."""
    if not table_data or 'lines' not in table_data:
        return frame
    lines = table_data['lines']
    for line_name, line_data in lines.items():
        p1 = tuple(map(int, line_data['point1']))
        p2 = tuple(map(int, line_data['point2']))
        color = (255, 255, 255) if 'net' in line_name else (0, 200, 0)
        cv2.line(frame, p1, p2, color, 2, cv2.LINE_AA)
    # Draw net (cyan) when we have table_top and table_bottom: mid-left to mid-right
    if 'table_top' in lines and 'table_bottom' in lines:
        tt = sorted([lines['table_top']['point1'], lines['table_top']['point2']], key=lambda p: p[0])
        tb = sorted([lines['table_bottom']['point1'], lines['table_bottom']['point2']], key=lambda p: p[0])
        tl, tr = np.array(tt[0]), np.array(tt[1])
        bl, br = np.array(tb[0]), np.array(tb[1])
        mid_left = tuple(((tl + bl) / 2).astype(int))
        mid_right = tuple(((tr + br) / 2).astype(int))
        cv2.line(frame, mid_left, mid_right, (255, 255, 0), 3, cv2.LINE_AA)
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
    Tennis-style ball tracker for table tennis:
    - 6D Kalman (x, y, vx, vy, ax, ay) for fast ball with acceleration
    - Outlier rejection that relaxes with missing frames
    - Re-acquisition: widens search when ball lost
    - Temporal confirmation: needs N consecutive detections to lock
    - Bounce detection via vertical velocity sign change
    """

    # Re-acquisition modes
    MODE_TRACKING = 0     # normal: tight outlier, narrow search
    MODE_SEARCHING = 1    # lost 5+ frames: relax outlier, wider search
    MODE_DESPERATE = 2    # lost 12+ frames: accept anything in ROI

    def __init__(self, fps=30, table_bounds=None):
        """
        table_bounds: (x_min, y_min, x_max, y_max) of the table surface.
        Bounces only register when ball is inside these bounds.
        """
        self.fps = fps
        self.dt = 1.0 / fps
        self.table_bounds = table_bounds  # set after table detection

        # 6D Kalman: [x, y, vx, vy, ax, ay]
        self.kf = KalmanFilter(dim_x=6, dim_z=2)
        dt = self.dt
        self.kf.F = np.array([
            [1, 0, dt, 0, 0.5*dt*dt, 0],
            [0, 1, 0, dt, 0, 0.5*dt*dt],
            [0, 0, 1, 0, dt, 0],
            [0, 0, 0, 1, 0, dt],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])
        self.kf.H = np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
        ])
        self.kf.P *= 200
        self.kf.R = np.eye(2) * 3        # measurement noise
        self.kf.Q = np.eye(6) * 0.2      # process noise
        self.kf.Q[4, 4] = 0.5            # more accel noise
        self.kf.Q[5, 5] = 0.8            # gravity accel noise (vertical)

        self.initialized = False
        self.missing_frames = 0
        self.max_missing = 45             # keep predicting up to 1.5s
        self.mode = self.MODE_TRACKING
        self.bounces = []
        self.prev_vy = 0
        self.last_bounce_frame = -30     # min gap between bounces
        self.history = deque(maxlen=300)

        # Temporal confirmation: need N of last M detections to "lock"
        self.confirm_window = deque(maxlen=5)  # last 5 frames
        self.confirmed = False

    @property
    def predicted_center(self):
        """Return current Kalman predicted position, or None."""
        if not self.initialized:
            return None
        return (float(self.kf.x[0, 0]), float(self.kf.x[1, 0]))

    def get_search_radius(self):
        """Search radius depends on mode."""
        if self.mode == self.MODE_TRACKING:
            return 100
        elif self.mode == self.MODE_SEARCHING:
            return 200
        else:
            return 9999  # full ROI

    def get_outlier_threshold(self):
        """Outlier threshold depends on mode."""
        if self.mode == self.MODE_TRACKING:
            return 80 + self.missing_frames * 8
        elif self.mode == self.MODE_SEARCHING:
            return 250
        else:
            return 9999  # accept anything

    def _update_mode(self):
        if self.missing_frames == 0:
            self.mode = self.MODE_TRACKING
        elif self.missing_frames >= 12:
            self.mode = self.MODE_DESPERATE
        elif self.missing_frames >= 5:
            self.mode = self.MODE_SEARCHING

    def update(self, detection_center, frame_num):
        """
        Update tracker with new detection.
        Returns dict with position, velocity, is_bounce, is_predicted, mode.
        """
        self._update_mode()

        if detection_center is not None:
            x, y = float(detection_center[0]), float(detection_center[1])

            if not self.initialized:
                self.kf.x = np.array([x, y, 0, 0, 0, 0]).reshape(6, 1)
                self.initialized = True
                self.missing_frames = 0
                self.confirm_window.append(True)
            else:
                pred = self.kf.x[:2].flatten()
                dist = np.linalg.norm([x - pred[0], y - pred[1]])
                thresh = self.get_outlier_threshold()

                if dist > thresh:
                    # Outlier: skip this detection
                    self.confirm_window.append(False)
                    self.kf.predict()
                    self.missing_frames += 1
                    self._update_mode()
                    pos = self.kf.x[:2].flatten()
                    vel = self.kf.x[2:4].flatten()
                    self.history.append((pos[0], pos[1], frame_num))
                    return {
                        'position': (pos[0], pos[1]) if self.confirmed else None,
                        'velocity': (vel[0], vel[1]),
                        'is_bounce': False,
                        'is_predicted': True,
                        'mode': self.mode,
                    }

                # Accept detection
                self.kf.predict()
                self.kf.update(np.array([x, y]).reshape(2, 1))
                self.missing_frames = 0
                self.confirm_window.append(True)

            # Temporal confirmation: need 3/5 recent frames detected
            n_detected = sum(self.confirm_window)
            if n_detected >= 3:
                self.confirmed = True
            elif n_detected <= 1 and len(self.confirm_window) >= 5:
                self.confirmed = False

            pos = self.kf.x[:2].flatten()
            vel = self.kf.x[2:4].flatten()

            # Bounce detection: velocity reversal AND ball must be on the table
            is_bounce = False
            cur_vy = vel[1]
            on_table = True
            if self.table_bounds is not None:
                tx1, ty1, tx2, ty2 = self.table_bounds
                margin_x = (tx2 - tx1) * 0.1
                margin_y = (ty2 - ty1) * 0.15
                on_table = (tx1 - margin_x <= pos[0] <= tx2 + margin_x and
                            ty1 - margin_y <= pos[1] <= ty2 + margin_y)
            # Bounce: ball was going down (vy>0), now going up or slowed sharply, and on table
            # Also enforce minimum gap of 8 frames between bounces to avoid duplicates
            frames_since_last = frame_num - self.last_bounce_frame
            if (self.prev_vy > 0.3 and cur_vy < 0 and on_table and frames_since_last > 8):
                is_bounce = True
                self.last_bounce_frame = frame_num
                self.bounces.append({
                    'frame': frame_num,
                    'image_xy': (pos[0], pos[1]),
                })
            self.prev_vy = cur_vy

            self.history.append((pos[0], pos[1], frame_num))
            return {
                'position': (pos[0], pos[1]) if self.confirmed else None,
                'velocity': (vel[0], vel[1]),
                'is_bounce': is_bounce,
                'is_predicted': False,
                'mode': self.mode,
            }

        else:
            # No detection
            self.confirm_window.append(False)
            if not self.initialized:
                return {'position': None, 'velocity': None, 'is_bounce': False, 'is_predicted': False, 'mode': self.mode}

            self.missing_frames += 1
            self._update_mode()

            if self.missing_frames > self.max_missing:
                self.confirmed = False
                return {'position': None, 'velocity': None, 'is_bounce': False, 'is_predicted': True, 'mode': self.mode}

            self.kf.predict()
            pos = self.kf.x[:2].flatten()
            vel = self.kf.x[2:4].flatten()
            self.history.append((pos[0], pos[1], frame_num))

            # Only show predicted position for first ~8 frames, then hide
            show = self.confirmed and self.missing_frames <= 8
            return {
                'position': (pos[0], pos[1]) if show else None,
                'velocity': (vel[0], vel[1]),
                'is_bounce': False,
                'is_predicted': True,
                'mode': self.mode,
            }

    def get_bounces(self):
        return self.bounces


# ============================================================
# MINI TABLE (small overlay, only bounce dots)
# ============================================================

class MiniTable:
    """Small table overlay showing ball position, trail, and bounce points."""

    def __init__(self, homography, width=160, height=100):
        self.H = homography
        self.width = width
        self.height = height
        self.pad_x = 8
        self.pad_top = 16   # extra top room for "FALLS" label
        self.pad_bot = 8
        self.dw = width - 2 * self.pad_x
        self.dh = height - self.pad_top - self.pad_bot
        self.table_w = 274.0
        self.table_h = 152.0

    def draw(self, bounces, ball_pos=None, court_dots=None, current_frame=0, fps=30):
        canvas = np.full((self.height, self.width, 3), (30, 60, 30), dtype=np.uint8)
        cx, cy = self.pad_x, self.pad_top

        # Table surface (blue)
        cv2.rectangle(canvas, (cx, cy), (cx + self.dw, cy + self.dh), (160, 90, 20), -1)
        # Border
        cv2.rectangle(canvas, (cx, cy), (cx + self.dw, cy + self.dh), (255, 255, 255), 1)
        # Net
        net_y = cy + self.dh // 2
        cv2.line(canvas, (cx, net_y), (cx + self.dw, net_y), (255, 255, 255), 1)
        # Center line
        mid_x = cx + self.dw // 2
        cv2.line(canvas, (mid_x, cy), (mid_x, cy + self.dh), (180, 180, 180), 1)

        # Court dots trail (where ball has been on the table) — fading
        if court_dots:
            for dx, dy, df in court_dots:
                age = current_frame - df
                fade = int(fps * 3)
                if age > fade:
                    continue
                mini_pos = self._to_mini((dx, dy))
                if mini_pos:
                    alpha = max(0.2, 1.0 - age / fade)
                    r = max(1, int(2 * alpha))
                    color = (int(180 * alpha), int(180 * alpha), int(40 * alpha))
                    cv2.circle(canvas, mini_pos, r, color, -1)

        # ALL bounce/fall points — permanent bright dots (never fade)
        for i, bounce in enumerate(bounces):
            image_xy = bounce.get('image_xy') if isinstance(bounce, dict) else None
            if image_xy is None:
                continue
            mini_pos = self._to_mini(image_xy)
            if mini_pos:
                # Bright red dot with white ring — permanent
                cv2.circle(canvas, mini_pos, 4, (0, 0, 255), -1)
                cv2.circle(canvas, mini_pos, 4, (255, 255, 255), 1)
                # Tiny label number
                cv2.putText(canvas, str(i + 1), (mini_pos[0] + 4, mini_pos[1] - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 255, 255), 1, cv2.LINE_AA)

        # Current ball position (yellow dot on top)
        if ball_pos is not None:
            mini_pos = self._to_mini(ball_pos)
            if mini_pos:
                cv2.circle(canvas, mini_pos, 3, (0, 255, 255), -1)
                cv2.circle(canvas, mini_pos, 3, (255, 255, 255), 1)

        # Label at top (above the table drawing)
        cv2.putText(canvas, "BALL FALLS", (cx + 2, cy - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1, cv2.LINE_AA)

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
            mx = int(self.pad_x + nx * self.dw)
            my = int(self.pad_top + ny * self.dh)
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
      1. Restrict search to table ROI (if corners given) to avoid false positives
      2. Compute difference between consecutive frames (motion)
      3. Filter for bright/white or orange pixels (ball color)
      4. Find small circular contours, prefer candidates near previous position
    """

    def __init__(self):
        self.prev_gray = None
        self.prev_prev_gray = None
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=120, varThreshold=35, detectShadows=False
        )
        self.kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.kernel_med = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        self.frame_count = 0

    def detect(self, frame, prev_center=None, table_corners=None,
               search_radius=120, desperate=False):
        """
        Detect table tennis ball using motion + appearance.
        table_corners: optional (4,2) array - restrict search to table + margin.
        search_radius: how far from prev_center to search (from tracker mode).
        desperate: if True, accept lower confidence candidates.
        Returns {'center': (x,y), 'conf': float, 'bbox': ...} or None.
        """
        h, w = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.frame_count += 1

        # --- 0. Table ROI: only search on/near table to avoid scoreboard, floor, hands ---
        roi_mask = None
        if table_corners is not None and len(table_corners) >= 4:
            roi_mask = np.zeros((h, w), dtype=np.uint8)
            pts = np.array(table_corners, dtype=np.int32).reshape(4, 2)
            top_y = int(pts[:, 1].min())
            center_x = int(pts[:, 0].mean())
            margin_up = int(h * 0.15)
            # Table polygon + cap above for air shots
            above = np.array([[center_x, max(0, top_y - margin_up)]], dtype=np.int32)
            hull = np.vstack([pts, above])
            hull = cv2.convexHull(hull)
            cv2.fillConvexPoly(roi_mask, hull.reshape(-1, 2), 255)
            margin_out = max(6, min(w, h) // 50)
            roi_mask = cv2.dilate(roi_mask, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (margin_out * 2 + 1, margin_out * 2 + 1)))

        # --- 1. Motion mask (slightly lower threshold for sensitivity) ---
        motion_mask = np.zeros((h, w), dtype=np.uint8)
        if self.prev_gray is not None:
            diff1 = cv2.absdiff(gray, self.prev_gray)
            _, motion1 = cv2.threshold(diff1, 15, 255, cv2.THRESH_BINARY)
            motion_mask = motion1
            if self.prev_prev_gray is not None:
                diff2 = cv2.absdiff(gray, self.prev_prev_gray)
                _, motion2 = cv2.threshold(diff2, 15, 255, cv2.THRESH_BINARY)
                motion_mask = cv2.bitwise_or(motion1, motion2)

        fg_mask = self.bg_subtractor.apply(frame, learningRate=0.005)
        _, fg_mask = cv2.threshold(fg_mask, 180, 255, cv2.THRESH_BINARY)
        combined_motion = cv2.bitwise_or(motion_mask, fg_mask)
        if roi_mask is not None:
            combined_motion = cv2.bitwise_and(combined_motion, roi_mask)

        # --- 2. Color mask: white / orange / yellow ball ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        white_mask = cv2.inRange(hsv, np.array([0, 0, 170]), np.array([180, 75, 255]))
        orange_mask = cv2.inRange(hsv, np.array([5, 90, 140]), np.array([28, 255, 255]))
        yellow_mask = cv2.inRange(hsv, np.array([18, 70, 170]), np.array([42, 255, 255]))
        color_mask = cv2.bitwise_or(white_mask, cv2.bitwise_or(orange_mask, yellow_mask))
        if roi_mask is not None:
            color_mask = cv2.bitwise_and(color_mask, roi_mask)

        # --- 3. Moving + ball-colored ---
        ball_mask = cv2.bitwise_and(combined_motion, color_mask)
        ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_OPEN, self.kernel_small)
        ball_mask = cv2.morphologyEx(ball_mask, cv2.MORPH_CLOSE, self.kernel_med)

        # Update history
        self.prev_prev_gray = self.prev_gray
        self.prev_gray = gray.copy()

        # Skip first 2 frames (need history for differencing)
        if self.frame_count < 3:
            return None

        # --- 4. Find contours (area range scales with resolution) ---
        contours, _ = cv2.findContours(ball_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = max(3, (w * h) // 100000)
        max_area = min(2500, (w * h) // 800)
        min_circ = 0.15 if desperate else 0.20

        candidates = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue
            peri = cv2.arcLength(cnt, True)
            if peri == 0:
                continue
            circularity = 4 * np.pi * area / (peri * peri)
            if circularity < min_circ:
                continue
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                continue
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            if roi_mask is not None and 0 <= int(cx) < w and 0 <= int(cy) < h:
                if roi_mask[int(cy), int(cx)] == 0:
                    continue
            x, y, bw, bh = cv2.boundingRect(cnt)
            if bw > 0 and bh > 0:
                aspect = max(bw, bh) / min(bw, bh)
                if aspect > 2.8:
                    continue
            size_score = min(area, 350) / 350.0
            conf = circularity * 0.55 + size_score * 0.45
            candidates.append({
                'center': (cx, cy),
                'conf': conf,
                'bbox': (float(x), float(y), float(x + bw), float(y + bh)),
                'area': area,
            })

        if not candidates and roi_mask is not None:
            bright_motion = cv2.bitwise_and(combined_motion, white_mask)
            bright_motion = cv2.bitwise_and(bright_motion, roi_mask)
            bright_motion = cv2.morphologyEx(bright_motion, cv2.MORPH_OPEN, self.kernel_small)
            contours2, _ = cv2.findContours(bright_motion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours2:
                area = cv2.contourArea(cnt)
                if min_area <= area <= max_area:
                    M = cv2.moments(cnt)
                    if M["m00"] == 0:
                        continue
                    cx, cy = M["m10"] / M["m00"], M["m01"] / M["m00"]
                    ix, iy = int(cx), int(cy)
                    if not (0 <= ix < w and 0 <= iy < h) or roi_mask[iy, ix] == 0:
                        continue
                    x, y, bw, bh = cv2.boundingRect(cnt)
                    candidates.append({
                        'center': (cx, cy),
                        'conf': 0.35,
                        'bbox': (float(x), float(y), float(x + bw), float(y + bh)),
                        'area': area,
                    })
        elif not candidates:
            bright_motion = cv2.bitwise_and(combined_motion, white_mask)
            bright_motion = cv2.morphologyEx(bright_motion, cv2.MORPH_OPEN, self.kernel_small)
            contours2, _ = cv2.findContours(bright_motion, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours2:
                area = cv2.contourArea(cnt)
                if min_area <= area <= max_area:
                    M = cv2.moments(cnt)
                    if M["m00"] == 0:
                        continue
                    cx, cy = M["m10"] / M["m00"], M["m01"] / M["m00"]
                    x, y, bw, bh = cv2.boundingRect(cnt)
                    candidates.append({
                        'center': (cx, cy),
                        'conf': 0.3,
                        'bbox': (float(x), float(y), float(x + bw), float(y + bh)),
                        'area': area,
                    })

        if not candidates:
            return None

        # --- 5. Pick best: prefer near prev position, then highest conf ---
        if prev_center is not None:
            max_dist = search_radius
            near_candidates = []
            for c in candidates:
                dist = np.sqrt((c['center'][0] - prev_center[0])**2 +
                               (c['center'][1] - prev_center[1])**2)
                if dist < max_dist:
                    proximity = 1.0 - (dist / max_dist)
                    c = dict(c)
                    c['conf'] = c['conf'] * 0.35 + proximity * 0.65
                    near_candidates.append(c)
            if near_candidates:
                return max(near_candidates, key=lambda c: c['conf'])

        # No prev or nothing near prev: return highest confidence
        return max(candidates, key=lambda c: c['conf'])


# ============================================================
# MAIN PIPELINE
# ============================================================

def main(video_path, output_path=None, table_calibration_path=None, show_preview=True, use_kimi=False,
<<<<<<< HEAD
         use_ttnet_table=False, ttnet_checkpoint_path=None, use_cortex_coach=False, live_stream=False):
=======
         use_ttnet_table=False, ttnet_checkpoint_path=None, use_coach=False):
>>>>>>> 9e0a16c (changes)
    """
    Table tennis analysis pipeline.

    Args:
        video_path: Input video
        output_path: Output video path
        table_calibration_path: JSON with table line calibration
        show_preview: Show live preview window
        use_kimi: Use Kimi K2.5 AI for detection
        use_ttnet_table: Use TTNet (tt/) segmentation to detect table lines (same code as tt)
        ttnet_checkpoint_path: Path to TTNet .pth checkpoint (required if use_ttnet_table)
        live_stream: Save frames to live_frames/current.jpg for browser streaming
    """
    
    # Live stream setup: save frames for browser to poll
    live_frame_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'live_frames')
    if live_stream:
        os.makedirs(live_frame_dir, exist_ok=True)
        print(f"[LIVE] Streaming frames to: {live_frame_dir}")
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
            print("[K2] AI detector initialized", flush=True)
            ret_f, first_frame = cap.read()
            if ret_f:
                print("[K2] Analyzing first frame (K2 Think may take 30-90s)...", flush=True)
                kimi_result = kimi_detector.detect(first_frame)
                if kimi_result.get('locked') and kimi_result.get('corners') is not None:
                    method = kimi_result.get('method', 'unknown')
                    net_info = f", net_y={kimi_result.get('net_y')}" if kimi_result.get('net_y') else ""
                    print(f"  [K2] Court lines detected via {method}{net_info}")
                    homography = kimi_result['homography']
                    table_info = {
                        'corners': kimi_result['corners'],
                        'net_y': kimi_result.get('net_y'),
                    }
                    use_keypoint_detector = False
                else:
                    print("  [K2] Table not detected, falling back to local CV...")
                    kimi_detector = None
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        except Exception as e:
            print(f"[Kimi K2] Error: {e}")
            kimi_detector = None

    # === LOCAL CV DETECTION (fallback) ===
    if table_info is None and homography is None:
        if os.path.exists(calib_path):
            calib_data = load_table_calibration(calib_path)
            print(f"Loaded manual table calibration: {calib_path}")
            # Support both 'corners' format (modern) and 'lines' format (legacy)
            if calib_data and 'corners' in calib_data:
                corners_list = calib_data['corners']
                corners_arr = np.array(corners_list, dtype=np.float32).reshape(4, 2)
                table_info = {
                    'corners': corners_arr,
                    'net_y': calib_data.get('net_y'),
                }
                homography = create_table_homography_from_corners(corners_arr)
                print(f"  Table corners loaded: {corners_arr.tolist()}")
            elif calib_data and 'lines' in calib_data:
                table_data = calib_data
                homography, _ = create_table_homography(table_data)
            use_keypoint_detector = False
        elif use_ttnet_table and TTNET_TABLE_AVAILABLE:
            if ttnet_checkpoint_path is None:
                ttnet_checkpoint_path = os.path.join(os.path.dirname(__file__), "tt", "checkpoints", "ttnet_best.pth")
            if ttnet_checkpoint_path and os.path.isfile(ttnet_checkpoint_path):
                # Use TTNet (tt/) segmentation to get table corners — same code as tt
                print("Running TTNet table detection (segmentation from tt)...")
                court_corners = detect_table_corners_ttnet(
                    video_path, ttnet_checkpoint_path,
                    frame_height=height, frame_width=width,
                )
                if court_corners is not None:
                    table_info = {'corners': court_corners}
                    homography = create_table_homography_from_corners(court_corners)
                    use_keypoint_detector = False
                else:
                    print("  TTNet table detection failed, falling back to court_lines_detector.")
        if table_info is None and homography is None:
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
                # 2) Court lines: surface+net detector (then fallback strategies)
                if table_info is None:
                    print(f"Running adaptive court detection (frame {try_frame_idx})...")
                    court_corners, net_y = detect_table_corners(try_frame)
                    if court_corners is not None:
                        table_info = {'corners': court_corners, 'net_y': net_y}
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
    # Set table bounds for bounce detection (ball must be on table to register bounce)
    _table_bounds = None
    if table_info and table_info.get('corners') is not None:
        _c = table_info['corners']
        _table_bounds = (float(np.min(_c[:, 0])), float(np.min(_c[:, 1])),
                         float(np.max(_c[:, 0])), float(np.max(_c[:, 1])))
    ball_tracker = TableTennisBallTracker(fps=fps, table_bounds=_table_bounds)
    print("Ball detector (frame-diff + color) + Kalman tracker initialized")

    # Pose tracker (optional; mediapipe loads here so K2 can run first)
    pose_tracker = None
    if _ensure_pose_tracker() and PoseTracker is not None:
        pose_tracker = PoseTracker(width, height, min_conf=0.3, smooth=15, num_players=2)
        print("Pose tracker initialized (both players: skeleton)")
    else:
        print("Pose tracker skipped (module not available).")

    # Tracking state
    frame_count = 0
    last_ball_center = None
    ball_trail = deque(maxlen=60)
    bounce_markers = []  # list of (x, y, frame_num) — where ball hit the table
    court_dots = deque(maxlen=150)  # trail dots on court surface: (x, y, frame_num)
    COLOR_P1 = (0, 0, 255)    # Red
    COLOR_P2 = (255, 0, 0)    # Blue

    # Analysis JSON: frame-level samples (perception) and state for derived metrics
    FRAME_SAMPLE_INTERVAL = 10  # sample every N frames for JSON
    frame_samples = []
    last_centroid_self = None
    last_centroid_opp = None
    last_sample_frame_self = 0
    last_sample_frame_opp = 0
    last_wrist_self = None       # for arm speed
    last_wrist_opp = None
    last_ball_speed_px = 0.0     # for acceleration

    # MediaPipe landmark indices
    LM_L_SHOULDER, LM_R_SHOULDER = 11, 12
    LM_L_ELBOW, LM_R_ELBOW = 13, 14
    LM_L_WRIST, LM_R_WRIST = 15, 16
    LM_L_HIP, LM_R_HIP = 23, 24
    LM_L_KNEE, LM_R_KNEE = 25, 26
    LM_L_ANKLE, LM_R_ANKLE = 27, 28
    LM_L_HEEL, LM_R_HEEL = 29, 30
    LM_L_FOOT_IDX, LM_R_FOOT_IDX = 31, 32

    def _lm_xy(lm, idx):
        """Get (x, y) of landmark; returns None if low visibility."""
        if lm and len(lm) > idx and lm[idx][3] > 0.3:
            return (float(lm[idx][0]), float(lm[idx][1]))
        return None

    def _angle_3pt(a, b, c):
        """Angle at point b between segments ba and bc, in degrees."""
        if a is None or b is None or c is None:
            return None
        ba = (a[0] - b[0], a[1] - b[1])
        bc = (c[0] - b[0], c[1] - b[1])
        dot = ba[0]*bc[0] + ba[1]*bc[1]
        mag_ba = np.sqrt(ba[0]**2 + ba[1]**2)
        mag_bc = np.sqrt(bc[0]**2 + bc[1]**2)
        if mag_ba < 1e-6 or mag_bc < 1e-6:
            return None
        cos_a = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
        return round(float(np.degrees(np.arccos(cos_a))), 1)

    def _dist(a, b):
        if a is None or b is None:
            return None
        return round(float(np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)), 1)

    def _extract_pose_data(lm, pose_det, last_centroid, last_wrist, last_frame, cur_frame,
                           table_bounds, label):
        """Extract rich body data from MediaPipe landmarks for one player."""
        data = {
            "center_of_mass": [],
            "bbox": None,
            "foot_pos": [],
            "stance_width": None,
            "footwork_speed": 0.0,
            "wrist_pos": {"left": None, "right": None},
            "elbow_pos": {"left": None, "right": None},
            "arm_speed": 0.0,
            "elbow_angle_left": None,
            "elbow_angle_right": None,
            "knee_angle_left": None,
            "knee_angle_right": None,
            "shoulder_angle_left": None,
            "shoulder_angle_right": None,
            "hip_center": None,
            "body_lean": None,
            "position_zone": None,
            "confidence": 0.0,
        }
        if lm is None or len(lm) <= 32:
            return data, last_centroid, last_wrist

        # Centroid + bbox
        if pose_det is not None:
            data["center_of_mass"] = [int(pose_det.centroid[0]), int(pose_det.centroid[1])]
            data["confidence"] = round(float(pose_det.score), 2)
            if pose_det.bbox is not None:
                data["bbox"] = [int(v) for v in pose_det.bbox]

        # Feet
        l_ankle = _lm_xy(lm, LM_L_ANKLE)
        r_ankle = _lm_xy(lm, LM_R_ANKLE)
        if l_ankle and r_ankle:
            data["foot_pos"] = [[int(l_ankle[0]), int(l_ankle[1])],
                                [int(r_ankle[0]), int(r_ankle[1])]]
            data["stance_width"] = _dist(l_ankle, r_ankle)

        # Wrists
        l_wrist = _lm_xy(lm, LM_L_WRIST)
        r_wrist = _lm_xy(lm, LM_R_WRIST)
        if l_wrist:
            data["wrist_pos"]["left"] = [int(l_wrist[0]), int(l_wrist[1])]
        if r_wrist:
            data["wrist_pos"]["right"] = [int(r_wrist[0]), int(r_wrist[1])]

        # Elbows
        l_elbow = _lm_xy(lm, LM_L_ELBOW)
        r_elbow = _lm_xy(lm, LM_R_ELBOW)
        if l_elbow:
            data["elbow_pos"]["left"] = [int(l_elbow[0]), int(l_elbow[1])]
        if r_elbow:
            data["elbow_pos"]["right"] = [int(r_elbow[0]), int(r_elbow[1])]

        # Shoulders + hips
        l_shoulder = _lm_xy(lm, LM_L_SHOULDER)
        r_shoulder = _lm_xy(lm, LM_R_SHOULDER)
        l_hip = _lm_xy(lm, LM_L_HIP)
        r_hip = _lm_xy(lm, LM_R_HIP)
        l_knee = _lm_xy(lm, LM_L_KNEE)
        r_knee = _lm_xy(lm, LM_R_KNEE)

        # Joint angles
        data["elbow_angle_left"] = _angle_3pt(l_shoulder, l_elbow, l_wrist)
        data["elbow_angle_right"] = _angle_3pt(r_shoulder, r_elbow, r_wrist)
        data["knee_angle_left"] = _angle_3pt(l_hip, l_knee, l_ankle)
        data["knee_angle_right"] = _angle_3pt(r_hip, r_knee, r_ankle)
        data["shoulder_angle_left"] = _angle_3pt(l_hip, l_shoulder, l_elbow)
        data["shoulder_angle_right"] = _angle_3pt(r_hip, r_shoulder, r_elbow)

        # Hip center + body lean (degrees from vertical)
        if l_hip and r_hip:
            hc = ((l_hip[0]+r_hip[0])/2, (l_hip[1]+r_hip[1])/2)
            data["hip_center"] = [int(hc[0]), int(hc[1])]
            if l_shoulder and r_shoulder:
                sc = ((l_shoulder[0]+r_shoulder[0])/2, (l_shoulder[1]+r_shoulder[1])/2)
                dx = sc[0] - hc[0]
                dy = hc[1] - sc[1]  # y inverted
                if dy > 1e-3:
                    data["body_lean"] = round(float(np.degrees(np.arctan2(dx, dy))), 1)

        # Footwork speed
        if last_centroid is not None and pose_det is not None:
            df = cur_frame - last_frame
            if df > 0:
                ddx = pose_det.centroid[0] - last_centroid[0]
                ddy = pose_det.centroid[1] - last_centroid[1]
                data["footwork_speed"] = round(float(np.sqrt(ddx*ddx + ddy*ddy)) / max(df, 1), 2)
        new_centroid = (pose_det.centroid[0], pose_det.centroid[1]) if pose_det else last_centroid

        # Arm speed (dominant wrist displacement per frame)
        dom_wrist = r_wrist or l_wrist
        new_wrist = dom_wrist
        if dom_wrist and last_wrist is not None:
            df = cur_frame - last_frame
            if df > 0:
                wdx = dom_wrist[0] - last_wrist[0]
                wdy = dom_wrist[1] - last_wrist[1]
                data["arm_speed"] = round(float(np.sqrt(wdx*wdx + wdy*wdy)) / max(df, 1), 2)

        # Position zone relative to table
        if table_bounds and pose_det is not None:
            tx1, ty1, tx2, ty2 = table_bounds
            cx = pose_det.centroid[0]
            tw = tx2 - tx1
            third = tw / 3
            if cx < tx1 + third:
                lr = "left"
            elif cx > tx2 - third:
                lr = "right"
            else:
                lr = "center"
            cy = pose_det.centroid[1]
            net_y_approx = (ty1 + ty2) / 2
            fb = "near" if cy > net_y_approx else "far"
            data["position_zone"] = f"{fb}_{lr}"

        return data, new_centroid, new_wrist

    print(f"\nProcessing {total_frames} frames...")
    print("-" * 60)

    # --- DB SETUP ---
    tracking_db = None
    match_id = None
    if DB_AVAILABLE:
        try:
            tracking_db = TrackingDB()
            if tracking_db.connect():
                # Use video filename as identifier
                vid_name = os.path.basename(video_path)
                match_id = tracking_db.create_new_match(video_file=vid_name)
                print(f"[DB] Match created: {match_id}")
            else:
                tracking_db = None
        except Exception as e:
            print(f"[DB] Error initializing DB: {e}")
            tracking_db = None

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
            table_corners = table_info.get('corners') if table_info else None
            # Use tracker state for adaptive search
            search_r = ball_tracker.get_search_radius()
            is_desperate = ball_tracker.mode == ball_tracker.MODE_DESPERATE
            # Use Kalman prediction as search center when available
            search_center = ball_tracker.predicted_center or last_ball_center

            if kimi_ball_center is not None:
                ball_center = kimi_ball_center
            else:
                ball_det = ball_detector.detect(
                    frame, prev_center=search_center,
                    table_corners=table_corners,
                    search_radius=search_r, desperate=is_desperate)
                ball_center = ball_det['center'] if ball_det else None

            result = ball_tracker.update(ball_center, frame_count)
            ball_pos = result['position']
            is_bounce = result['is_bounce']
            is_predicted = result['is_predicted']
            ball_velocity = result.get('velocity') or (0.0, 0.0)

            if ball_pos:
                last_ball_center = ball_pos
                ball_trail.append(ball_pos)

            # --- FRAME-LEVEL SAMPLE for analysis JSON (every N frames) ---
            if frame_count % FRAME_SAMPLE_INTERVAL == 0:
                t_sec = frame_count / fps
                vx, vy = float(ball_velocity[0]), float(ball_velocity[1])
                speed_px = np.sqrt(vx*vx + vy*vy)
                ball_speed_val = round(float(speed_px) * fps / 100.0, 1) if ball_pos else 0.0
                ball_conf = 0.85 if (ball_pos and not is_predicted) else (0.5 if ball_pos else 0.0)

                # Ball acceleration (change in speed)
                ball_accel = round(ball_speed_val - last_ball_speed_px, 1)
                last_ball_speed_px = ball_speed_val

                # Ball trajectory direction
                ball_direction = None
                if ball_pos and vx != 0:
                    angle_deg = round(float(np.degrees(np.arctan2(-vy, vx))), 1)
                    ball_direction = angle_deg

                # Ball height relative to table
                ball_height_rel = None
                if ball_pos and _table_bounds:
                    ty1 = _table_bounds[1]
                    ball_height_rel = round(float(ty1 - ball_pos[1]), 1)  # >0 means above table top edge

                # Ball landing zone (quadrant: near/far x left/center/right)
                ball_zone = None
                if ball_pos and _table_bounds:
                    tx1, ty1, tx2, ty2 = _table_bounds
                    bx, by = ball_pos[0], ball_pos[1]
                    if tx1 <= bx <= tx2 and ty1 <= by <= ty2:
                        tw = tx2 - tx1
                        net_approx = (ty1 + ty2) / 2
                        lr = "left" if bx < tx1 + tw/3 else ("right" if bx > tx2 - tw/3 else "center")
                        fb = "near" if by > net_approx else "far"
                        ball_zone = f"{fb}_{lr}"

                sample = {
                    "t": round(t_sec, 3),
                    "frame_id": frame_count,
                    "ball": {
                        "x": int(ball_pos[0]) if ball_pos else None,
                        "y": int(ball_pos[1]) if ball_pos else None,
                        "speed": ball_speed_val,
                        "acceleration": ball_accel,
                        "direction_deg": ball_direction,
                        "height_above_table": ball_height_rel,
                        "zone": ball_zone,
                        "confidence": round(ball_conf, 2),
                    },
                    "player": {},
                    "opponent": {},
                }

                # Player (near camera = pose_L)
                lm_L = pose_L.landmarks if (pose_L and hasattr(pose_L, 'landmarks')) else None
                p_data, last_centroid_self, last_wrist_self = _extract_pose_data(
                    lm_L, pose_L, last_centroid_self, last_wrist_self,
                    last_sample_frame_self, frame_count, _table_bounds, "self")
                p_data["id"] = "self"
                sample["player"] = p_data
                last_sample_frame_self = frame_count

                # Opponent (far camera = pose_R)
                lm_R = pose_R.landmarks if (pose_R and hasattr(pose_R, 'landmarks')) else None
                o_data, last_centroid_opp, last_wrist_opp = _extract_pose_data(
                    lm_R, pose_R, last_centroid_opp, last_wrist_opp,
                    last_sample_frame_opp, frame_count, _table_bounds, "opponent")
                o_data["id"] = "opponent"
                sample["opponent"] = o_data
                last_sample_frame_opp = frame_count

                frame_samples.append(sample)

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
                frame = draw_court_overlay(frame, table_info['corners'], color=(0, 255, 0), thickness=2,
                                           net_y=table_info.get('net_y'))

            # 4. Ball: yellow circle + bounce impact markers on court
            # Only add bounce marker if ball is on the table surface
            if is_bounce and ball_pos and table_info and table_info.get('corners') is not None:
                corners = table_info['corners']
                bx_f, by_f = float(ball_pos[0]), float(ball_pos[1])
                ty_min = float(np.min(corners[:, 1]))
                ty_max = float(np.max(corners[:, 1]))
                tx_min = float(np.min(corners[:, 0]))
                tx_max = float(np.max(corners[:, 0]))
                margin_y = (ty_max - ty_min) * 0.1
                if (tx_min <= bx_f <= tx_max and ty_min - margin_y <= by_f <= ty_max + margin_y):
                    bounce_markers.append((int(bx_f), int(by_f), frame_count))

            # Draw bounce impact markers (persist for 2 seconds = 60 frames)
            active_markers = []
            for mx, my, mf in bounce_markers:
                age = frame_count - mf
                if age > fps * 2:
                    continue  # expired
                active_markers.append((mx, my, mf))
                # Fade: start bright, fade out over 2s
                alpha = max(0.2, 1.0 - age / (fps * 2))
                radius = int(10 + 4 * (1.0 - alpha))  # grows as it fades
                # Red impact circle with white ring
                color_r = (0, 0, int(255 * alpha))  # red fading
                color_w = (int(200 * alpha), int(200 * alpha), int(255 * alpha))
                cv2.circle(frame, (mx, my), radius, color_r, -1)
                cv2.circle(frame, (mx, my), radius + 1, color_w, 2)
                # "X" cross mark at center
                d = max(3, radius // 3)
                cv2.line(frame, (mx - d, my - d), (mx + d, my + d), (255, 255, 255), 1)
                cv2.line(frame, (mx - d, my + d), (mx + d, my - d), (255, 255, 255), 1)
                # Label: bounce number
                bounce_idx = bounce_markers.index((mx, my, mf)) + 1
                if age < fps:  # show label for 1 second
                    cv2.putText(frame, f"B{bounce_idx}", (mx + radius + 3, my - 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1, cv2.LINE_AA)
            bounce_markers[:] = active_markers

            # Ball trail dots on court: ONLY when ball is strictly on the table surface
            if (ball_pos and not is_predicted and table_info
                    and table_info.get('corners') is not None):
                corners = table_info['corners']
                ty_min = float(np.min(corners[:, 1]))
                ty_max = float(np.max(corners[:, 1]))
                tx_min = float(np.min(corners[:, 0]))
                tx_max = float(np.max(corners[:, 0]))
                bx_f, by_f = float(ball_pos[0]), float(ball_pos[1])
                # Ball must be INSIDE the table rectangle (no margin)
                if (tx_min <= bx_f <= tx_max and ty_min <= by_f <= ty_max):
                    court_dots.append((int(bx_f), int(by_f), frame_count))

            # Draw court dots (fade over 2 seconds)
            for dx, dy, df in court_dots:
                age = frame_count - df
                fade_frames = int(fps * 2)
                if age > fade_frames:
                    continue
                alpha = max(0.15, 1.0 - age / fade_frames)
                r = max(2, int(3 * alpha))
                # Cyan dots on the table
                color = (int(200 * alpha), int(200 * alpha), int(50 * alpha))
                cv2.circle(frame, (dx, dy), r, color, -1)

            # Ball position dot (on top)
            if ball_pos:
                bx, by = int(ball_pos[0]), int(ball_pos[1])
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
                mini_img = mini_table.draw(
                    mini_table.last_bounces,
                    ball_pos=ball_pos,
                    court_dots=court_dots,
                    current_frame=frame_count,
                    fps=fps)
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
            
            # Live stream: save frame for browser to poll (every 2nd frame to reduce I/O)
            if live_stream and frame_count % 2 == 0:
                live_path = os.path.join(live_frame_dir, 'current.jpg')
                temp_path = os.path.join(live_frame_dir, 'temp.jpg')
                # Resize for faster streaming (max 720p width)
                stream_frame = frame
                if frame.shape[1] > 720:
                    scale = 720 / frame.shape[1]
                    stream_frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                # Atomic write: write to temp, then rename to avoid partial reads
                cv2.imwrite(temp_path, stream_frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                try:
                    if os.path.exists(live_path):
                        os.remove(live_path)
                    os.rename(temp_path, live_path)
                except Exception:
                    pass  # Ignore race conditions

            # Preview
            if show_preview:
                cv2.imshow('Table Tennis Analysis (Q to quit)', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user")
                    break

    except KeyboardInterrupt:
        print("\nInterrupted")

    finally:
        # Cleanup
        cap.release()
        out.release()
        if show_preview:
            cv2.destroyAllWindows()
        
        if tracking_db:
            print("[DB] Flushing data for video segment...")
            tracking_db.flush() # Just flush, don't close yet

    print(f"\n{'=' * 60}")
    print(f"Done! {frame_count} frames processed")
    print(f"Bounces detected: {len(ball_tracker.get_bounces())}")
    print(f"Output: {output_path}")
    print(f"{'=' * 60}")

    # --- Build judge-safe analysis JSON (perception → shots → rallies → semantics) ---
    json_path = output_path.replace('.mp4', '.json').replace('.avi', '.json')
    bounces = ball_tracker.get_bounces()
    net_y = float(table_info.get('net_y')) if table_info and table_info.get('net_y') is not None else None
    corners = table_info['corners'] if table_info and table_info.get('corners') is not None else None

    # 1. Court geometry (static + zones)
    court_json = {}
    if corners is not None:
        c_net_y = float(np.mean(corners[:, 1])) if net_y is None else net_y
        c_width = int(float(np.max(corners[:, 0]) - np.min(corners[:, 0])))
        c_height = int(float(np.max(corners[:, 1]) - np.min(corners[:, 1])))
        c_x_min = float(np.min(corners[:, 0]))
        c_x_max = float(np.max(corners[:, 0]))
        c_y_min = float(np.min(corners[:, 1]))
        c_y_max = float(np.max(corners[:, 1]))
        third_w = c_width / 3
        court_json = {
            "court": {
                "corners": [[float(c[0]), float(c[1])] for c in corners],
                "net_y": c_net_y,
                "width_px": c_width,
                "height_px": c_height,
                "zones": {
                    "far_left":   {"x": [round(c_x_min, 1), round(c_x_min + third_w, 1)], "y": [round(c_y_min, 1), round(c_net_y, 1)]},
                    "far_center": {"x": [round(c_x_min + third_w, 1), round(c_x_max - third_w, 1)], "y": [round(c_y_min, 1), round(c_net_y, 1)]},
                    "far_right":  {"x": [round(c_x_max - third_w, 1), round(c_x_max, 1)], "y": [round(c_y_min, 1), round(c_net_y, 1)]},
                    "near_left":  {"x": [round(c_x_min, 1), round(c_x_min + third_w, 1)], "y": [round(c_net_y, 1), round(c_y_max, 1)]},
                    "near_center":{"x": [round(c_x_min + third_w, 1), round(c_x_max - third_w, 1)], "y": [round(c_net_y, 1), round(c_y_max, 1)]},
                    "near_right": {"x": [round(c_x_max - third_w, 1), round(c_x_max, 1)], "y": [round(c_net_y, 1), round(c_y_max, 1)]},
                },
            }
        }
    if not court_json:
        court_json = {"court": {"corners": [], "net_y": None, "width_px": 0, "height_px": 0, "zones": {}}}

    # 2. Frame-level perception (already collected; fps at top level only)
    frame_level = {"sample_interval": FRAME_SAMPLE_INTERVAL, "samples": frame_samples}

    # 3. Shot-level events (each bounce = one landing; one stroke per shot, duration <= 1.0s)
    shots_list = []
    net_y_val = court_json.get("court", {}).get("net_y")
    for i, b in enumerate(bounces):
        frame_num = b["frame"]
        x, y = float(b["image_xy"][0]), float(b["image_xy"][1])
        t_end = frame_num / fps
        t_contact = round(t_end - 0.05, 2)
        t_start = round(max(0.0, t_contact - 0.35), 2)
        if t_end - t_start > 1.0:
            t_start = round(t_end - 1.0, 2)
        depth = "short" if (net_y_val is not None and y > net_y_val) else "long"
        player_id = "opponent" if (i % 2 == 0) else "self"

        # Determine forehand/backhand from frame sample nearest to this shot
        hand = "unknown"
        nearest_sample = None
        min_dt = 9999
        for s in frame_samples:
            dt = abs(s["t"] - t_contact)
            if dt < min_dt:
                min_dt = dt
                nearest_sample = s
        if nearest_sample is not None:
            p = nearest_sample["player"] if player_id == "self" else nearest_sample["opponent"]
            lw = p.get("wrist_pos", {}).get("left")
            rw = p.get("wrist_pos", {}).get("right")
            com = p.get("center_of_mass", [])
            if lw and rw and len(com) == 2:
                l_ext = np.sqrt((lw[0]-com[0])**2 + (lw[1]-com[1])**2)
                r_ext = np.sqrt((rw[0]-com[0])**2 + (rw[1]-com[1])**2)
                hand = "forehand" if r_ext > l_ext * 1.15 else ("backhand" if l_ext > r_ext * 1.15 else "neutral")

        # Landing zone (quadrant on table)
        landing_zone = None
        if _table_bounds:
            tx1, ty1, tx2, ty2 = _table_bounds
            tw = tx2 - tx1
            net_approx = (ty1 + ty2) / 2
            lr = "left" if x < tx1 + tw/3 else ("right" if x > tx2 - tw/3 else "center")
            fb = "near" if y > net_approx else "far"
            landing_zone = f"{fb}_{lr}"

        shots_list.append({
            "shot_id": i + 1,
            "t_start": t_start,
            "t_contact": t_contact,
            "t_end": round(t_end, 2),
            "player": player_id,
            "shot_type": "push",
            "hand": hand,
            "contact_zone": "neutral",
            "landing": {"x": int(x), "y": int(y), "in": True, "depth": depth, "zone": landing_zone},
        })
    shots_json = {"shots": shots_list}

    # 4. Rally-level aggregation (group shots by time gap < 2s)
    RALLY_GAP_SEC = 2.0
    rallies_list = []
    shot_ids_in_rally = []
    rally_start_t = None
    for s in shots_list:
        t = s["t_end"]
        if rally_start_t is None:
            rally_start_t = s["t_start"]
        if shot_ids_in_rally and (t - shots_list[shot_ids_in_rally[-1] - 1]["t_end"] > RALLY_GAP_SEC):
            rallies_list.append({
                "rally_id": len(rallies_list) + 1,
                "t_start": round(rally_start_t, 2),
                "t_end": round(shots_list[shot_ids_in_rally[-1] - 1]["t_end"], 2),
                "shots": list(shot_ids_in_rally),
                "winner": "opponent" if (shots_list[shot_ids_in_rally[-1] - 1]["player"] == "self") else "self",
                "length": len(shot_ids_in_rally),
                "pressure": {"score": "unknown", "is_game_point": False},
            })
            rally_start_t = s["t_start"]
            shot_ids_in_rally = []
        shot_ids_in_rally.append(s["shot_id"])
    if shot_ids_in_rally:
        rallies_list.append({
            "rally_id": len(rallies_list) + 1,
            "t_start": round(rally_start_t, 2),
            "t_end": round(shots_list[shot_ids_in_rally[-1] - 1]["t_end"], 2),
            "shots": list(shot_ids_in_rally),
            "winner": "opponent" if (shots_list[shot_ids_in_rally[-1] - 1]["player"] == "self") else "self",
            "length": len(shot_ids_in_rally),
            "pressure": {"score": "unknown", "is_game_point": False},
        })
    rallies_json = {"rallies": rallies_list}

    # Enrich frame samples with pressure context (frame_level_perception.samples references frame_samples)
    for s in frame_samples:
        t = s["t"]
        for r in rallies_list:
            if r["t_start"] <= t <= r["t_end"] and r["length"] >= 4:
                s["context"] = {"is_pressure_point": True}
                break

    # 5. Behavioral metrics (derived from frame samples)
    footwork_speeds = [s["player"].get("footwork_speed", 0.0) for s in frame_samples]
    arm_speeds = [s["player"].get("arm_speed", 0.0) for s in frame_samples]
    opp_footwork = [s["opponent"].get("footwork_speed", 0.0) for s in frame_samples]
    avg_footwork = float(np.mean(footwork_speeds)) if footwork_speeds else 0.0
    threshold = max(0.1, avg_footwork * 0.5)
    drop_count = sum(1 for v in footwork_speeds if v < threshold)
    footwork_drop_pct = int(round(100.0 * drop_count / len(footwork_speeds))) if footwork_speeds else 0
    RALLY_GAP_FOR_DUR = 2.0
    rally_durations = [
        shots_list[i]["t_end"] - shots_list[i - 1]["t_end"]
        for i in range(1, len(shots_list))
        if shots_list[i]["t_end"] - shots_list[i - 1]["t_end"] < RALLY_GAP_FOR_DUR
    ]
    avg_rally_duration = round(float(np.mean(rally_durations)), 2) if rally_durations else 0.0
    max_footwork = max(footwork_speeds) if footwork_speeds else 1.0
    aggression_value = round(avg_footwork / max_footwork, 2) if max_footwork > 0 else 0.0
    aggression_value = min(1.0, max(0.0, aggression_value))
    avg_arm_speed = round(float(np.mean(arm_speeds)), 2) if arm_speeds else 0.0
    avg_opp_footwork = round(float(np.mean(opp_footwork)), 2) if opp_footwork else 0.0
    # Shot placement distribution
    fh_count = sum(1 for s in shots_list if s["hand"] == "forehand")
    bh_count = sum(1 for s in shots_list if s["hand"] == "backhand")
    total_shots = len(shots_list)
    near_count = sum(1 for s in shots_list if s["landing"]["depth"] == "short")
    far_count = sum(1 for s in shots_list if s["landing"]["depth"] == "long")
    behavioral_json = {
        "behavioral_metrics": {
            "player": {
                "footwork_drop_pct": footwork_drop_pct,
                "avg_footwork_speed": round(avg_footwork, 2),
                "avg_arm_speed": avg_arm_speed,
                "aggression_index": {"value": aggression_value, "scale": "0_to_1"},
            },
            "opponent": {
                "avg_footwork_speed": avg_opp_footwork,
            },
            "match": {
                "avg_rally_duration": avg_rally_duration,
                "total_shots": total_shots,
                "total_rallies": len(rallies_list),
                "total_bounces": len(bounces),
                "forehand_pct": round(100.0 * fh_count / total_shots, 1) if total_shots else 0,
                "backhand_pct": round(100.0 * bh_count / total_shots, 1) if total_shots else 0,
                "short_pct": round(100.0 * near_count / total_shots, 1) if total_shots else 0,
                "long_pct": round(100.0 * far_count / total_shots, 1) if total_shots else 0,
                "baseline_distance": None,
            },
        }
    }

    # 6. Match context (placeholder)
    match_context_json = {
        "match_context": {
            "player_level": "intermediate",
            "opponent_style": "unknown",
            "score_state": "unknown",
            "set": 1,
        }
    }

    # 7. Semantic summary (K2-ready; derived, not raw)
    num_rallies = len(rallies_list)
    num_shots = len(shots_list)
    fh_pct = round(100.0 * fh_count / total_shots, 1) if total_shots else 0
    bh_pct = round(100.0 * bh_count / total_shots, 1) if total_shots else 0
    semantic_summary = (
        f"Match analysis: {num_shots} shots across {num_rallies} rallies ({frame_count} frames, {round(frame_count/fps, 1)}s). "
        f"Player footwork drop: {footwork_drop_pct}%. Avg arm speed: {avg_arm_speed} px/f. "
        f"Shot distribution: {fh_pct}% forehand, {bh_pct}% backhand. "
        f"Avg rally duration: {avg_rally_duration}s. "
        "Perception separated from reasoning: frames capture movement + joint angles, shots capture intent + placement, "
        "rallies capture pressure context, and the reasoning model infers tactical and mental patterns from these abstractions."
    )
    semantic_json = {"semantic_summary": semantic_summary}

    analysis = {
        "video": video_path,
        "frames": frame_count,
        "fps": fps,
        "units": {"ball_speed": "px_per_sec", "footwork_speed": "px_per_sec"},
        "court": court_json["court"],
        "frame_level_perception": frame_level,
        "shots": shots_json["shots"],
        "rallies": rallies_json["rallies"],
        "behavioral_metrics": behavioral_json["behavioral_metrics"],
        "match_context": match_context_json["match_context"],
        "semantic_summary": semantic_json["semantic_summary"],
    }
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"Analysis JSON: {json_path}")

<<<<<<< HEAD
<<<<<<< HEAD
=======
<<<<<<< HEAD
=======
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35
    # --- Push full analysis + Cortex vector embedding to Snowflake ---
    if tracking_db is not None and match_id is not None:
        try:
            success = tracking_db.db.insert_full_analysis(match_id, analysis)
            if success:
                print("[Snowflake] Full analysis + vector embedding stored in ANALYSIS_OUTPUT")

<<<<<<< HEAD
                # Optionally run Gemini coaching (if --coach flag)
                if use_cortex_coach:
                    try:
                        from modules.llm_coach import GeminiCoach, print_coaching_result
                        coach = GeminiCoach()
                        coach.db = tracking_db.db  # reuse Snowflake connection
                        print("\n[Gemini] Generating AI coaching insight...")
                        result = coach.analyze_match(match_id)
                        print_coaching_result(result)
                    except Exception as e:
                        print(f"[Gemini] Coaching failed: {e}")
        except Exception as e:
            print(f"[Snowflake] Push failed: {e}")

=======
                # Optionally run Cortex coaching (if --coach flag)
                if use_cortex_coach:
                    try:
                        from modules.llm_coach import CortexCoach
                        coach = CortexCoach()
                        coach.db = tracking_db.db  # reuse connection
                        print("\n[Cortex] Generating AI coaching insight...")
                        insight = coach.analyze_match(match_id)
                        print(f"\n{'=' * 60}")
                        print("AI COACHING INSIGHT (Cortex)")
                        print(f"{'=' * 60}")
                        print(insight)
                        print(f"{'=' * 60}\n")
                    except Exception as e:
                        print(f"[Cortex] Coaching failed: {e}")
=======
    # ---------------------------------------------------------
    # EXTENDED PIPELINE: Stats, Coach, DB
    # ---------------------------------------------------------

    # 1. Pre-process Stats (StatsEngine)
    match_stats = None
    try:
        from HH.stats_engine import StatsEngine
        stats_engine = StatsEngine(fps=fps)
        print("\n[Stats] Running StatsEngine Enrichment...")
        match_stats = stats_engine.process_match(analysis)
        
        # Save Stats JSON
        stats_path = output_path.replace('.mp4', '_stats.json').replace('.avi', '_stats.json')
        with open(stats_path, 'w') as f:
            json.dump(match_stats, f, indent=2)
        print(f"[File] Stats JSON saved: {stats_path}")

        # DB: Stats
        if tracking_db and match_id and match_stats:
             tracking_db.db.insert_match_stats(match_id, match_stats.get('match_summary', {}), match_stats.get('rallies', []))
             print("[Snowflake] Match stats saved to MATCH_STATS")
    except ImportError:
        print("[Warning] StatsEngine not found, skipping stats enrichment.")
    except Exception as e:
        print(f"[Error] Stats processing failed: {e}")

    # 2. Push Full Analysis to Snowflake (Cortex Embeddings)
    if tracking_db and match_id:
        try:
            tracking_db.db.insert_full_analysis(match_id, analysis)
>>>>>>> 9e0a16c (changes)
        except Exception as e:
            print(f"[Snowflake] Full Analysis push failed: {e}")

    # 3. AI Coaching (DedalusCoach)
    # Check args.coach usually, but since the user requested "run pipeline... prompt... response", we assume they want it if the module is there
    # But strictly we should use the flag. The user said "run pipeline...", implying I will run the command WITH the flag.
    # I need to access 'args' variable? No, I am inside 'main' function. I don't have 'args' here.
    # 'main' function signature needs to accept 'use_coach'.
    # I will modify 'main' signature in another chunk.
    if use_coach and match_stats:
        try:
            from modules.dedalus_coach import DedalusCoach
            print("\n[Coach] Initializing DedalusCoach...")
            coach = DedalusCoach()
            
            # Generate Prompt
            prompt = coach._prepare_input(match_stats)
            prompt_path = output_path.replace('.mp4', '_prompt.txt')
            with open(prompt_path, 'w') as f:
                f.write(prompt)
            print(f"[File] Prompt saved: {prompt_path}")

            # Run Analysis
            print("[Coach] Running Analysis (this may take a moment)...")
            response = coach.analyze_match(match_stats)
            
            # Save Response
            response_path = output_path.replace('.mp4', '_response.json')
            with open(response_path, 'w') as f:
                f.write(response)
            print(f"[File] LLM Response saved: {response_path}")

            # DB: Insight
            if tracking_db and match_id:
                # Try to parse response if it's JSON
                try:
                    processed = json.loads(response)
                except:
                    processed = None
                tracking_db.db.insert_coaching_insight(match_id, prompt, response, processed)
                print("[Snowflake] Coaching insight saved to COACHING_INSIGHTS")

        except Exception as e:
            print(f"[Coach] Error: {e}")

    # --- Cleanup DB connection at the very end ---
    if tracking_db:
        print("[DB] Closing connection...")
        tracking_db.close()
        print("[DB] Closed.")
>>>>>>> e5f71e94f5f64b882f6db0e1faece12978f80c35

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Table Tennis Analysis Pipeline')
    parser.add_argument('--video', type=str, default='Videos/Recording 2026-02-07 134224.mp4',
                        help='Input video path (default: Videos/Recording 2026-02-07 134224.mp4)')
    parser.add_argument('--output', type=str, default=None, help='Output video path')
    parser.add_argument('--table-lines', type=str, default=None,
                        help='Table calibration JSON (default: table_lines.json)')
    parser.add_argument('--no-preview', action='store_true', help='Disable live preview')
    parser.add_argument('--kimi', action='store_true',
                        help='Use Kimi K2.5 AI for table/ball detection (requires MOONSHOT_API_KEY)')
    parser.add_argument('--ttnet', action='store_true',
                        help='Use TTNet (tt/) segmentation to track table lines (same code as tt)')
    parser.add_argument('--ttnet-checkpoint', type=str, default=None,
                        help='Path to TTNet .pth checkpoint (required for --ttnet; e.g. tt/checkpoints/ttnet_best.pth)')
<<<<<<< HEAD
    parser.add_argument('--coach', action='store_true',
                        help='Run Cortex AI coaching after analysis (requires Snowflake + Cortex)')
    parser.add_argument('--live-stream', action='store_true',
                        help='Stream processed frames to live_frames/ for browser real-time display')
=======
    parser.add_argument('--coach', action='store_true', help='Enable AI Coaching (Dedalus/Cortex)')
>>>>>>> 9e0a16c (changes)

    args = parser.parse_args()

    main(args.video, args.output,
         table_calibration_path=args.table_lines,
         show_preview=not args.no_preview,
         use_kimi=args.kimi,
         use_ttnet_table=args.ttnet,
         ttnet_checkpoint_path=args.ttnet_checkpoint,
<<<<<<< HEAD
         use_cortex_coach=args.coach,
         live_stream=args.live_stream)
=======
         use_coach=args.coach)
>>>>>>> 9e0a16c (changes)
