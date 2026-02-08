"""
IFM K2-Think (LLM360) "Hybrid Reasoning" Detector for Table Tennis.
- Demonstrates K2-Think's reasoning capabilities by converting visual data (lines/colors) 
  into a text-based spatial puzzle.
- Set MOONSHOT_API_KEY starting with "IFM-" to enable this mode.
- Set IFM_K2_API_BASE_URL to the provided endpoint.
"""

import base64
import json
import re
import os

import cv2
import numpy as np

# Load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Table dimensions for homography (standard table tennis table)
TABLE_W, TABLE_H = 274, 152

# One-time message when using IFM K2 Think (no vision)
_printed_no_vision = False


def _get_api_key():
    return os.environ.get("MOONSHOT_API_KEY") or os.environ.get("KIMI_K2_API_KEY")


def _get_base_url_and_model(api_key):
    """
    If key starts with IFM- (e.g. Columbia DevFest K2 Think), use IFM endpoint.
    Otherwise use Moonshot (Kimi K2.5).
    Returns (base_url, model_name).
    """
    if api_key and api_key.strip().upper().startswith("IFM-"):
        base = (os.environ.get("IFM_K2_API_BASE_URL") or "").strip().rstrip("/")
        if not base:
            raise ValueError(
                "Your API key is an IFM K2 Think key (Columbia DevFest). "
                "Set IFM_K2_API_BASE_URL in .env to the API base URL from the DevFest materials "
                "(e.g. from the cURL example in api.png or from the team/WhatsApp)."
            )
        model = os.environ.get("K2_THINK_MODEL", "k2-think")
        return base, model
    return "https://api.moonshot.ai/v1", "kimi-k2.5"


def _frame_to_base64_jpeg(frame, max_size=1280):
    """Encode BGR frame as base64 JPEG, optionally downscaling to save tokens."""
    h, w = frame.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        nw, nh = int(w * scale), int(h * scale)
        frame = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_AREA)
    _, buf = cv2.imencode(".jpg", frame)
    return base64.b64encode(buf).decode("utf-8"), frame.shape[0], frame.shape[1]


def _extract_json_object(text):
    """Find first {...} with balanced braces and return it (or None)."""
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _parse_corners_json(text, img_h, img_w):
    """
    Parse model response for 4 corners and optional net_y.
    Expect order: tl, tr, br, bl.
    Returns (corners, net_y) where net_y is int or None.
    """
    text = text.strip()
    net_y = None
    try:
        json_str = _extract_json_object(text)
        if json_str:
            obj = json.loads(json_str)
            corners = obj.get("corners")
            if isinstance(corners, list) and len(corners) >= 4:
                pts = []
                for i in range(4):
                    p = corners[i]
                    if isinstance(p, (list, tuple)) and len(p) >= 2:
                        x = float(p[0])
                        y = float(p[1])
                        pts.append([x, y])
                if len(pts) == 4:
                    ny = obj.get("net_y", obj.get("net_y_pixel"))
                    if ny is not None:
                        try:
                            net_y = int(float(ny))
                        except (TypeError, ValueError):
                            pass
                    return np.array(pts, dtype=np.float32), net_y
        # Fallback: look for four [x,y] or (x,y) pairs
        pairs = re.findall(r"\[?\s*(\d+(?:\.\d+)?)\s*[,,\s]\s*(\d+(?:\.\d+)?)\s*\]?", text)
        if len(pairs) >= 4:
            pts = [[float(a), float(b)] for a, b in pairs[:4]]
            return np.array(pts, dtype=np.float32), net_y
    except (json.JSONDecodeError, ValueError):
        pass
    return None, None


def _parse_ball_json(text):
    """Parse model response for ball position."""
    text = text.strip()
    try:
        m = re.search(r"\{[^{}]*\"ball_found\"[^{}]*\}", text, re.DOTALL)
        if m:
            obj = json.loads(m.group(0))
            found = obj.get("ball_found", False)
            if not found:
                return {"ball_found": False, "center": None}
            x = obj.get("x", obj.get("center_x"))
            y = obj.get("y", obj.get("center_y"))
            if x is not None and y is not None:
                return {"ball_found": True, "center": (float(x), float(y))}
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if len(nums) >= 2:
            return {"ball_found": True, "center": (float(nums[0]), float(nums[1]))}
    except (json.JSONDecodeError, ValueError):
        pass
    return {"ball_found": False, "center": None}


def _find_table_surface(frame):
    """
    Use color segmentation to find the blue/green table surface.
    Returns (surface_mask, bounding_box) or (None, None).
    bounding_box = (x1, y1, x2, y2).

    Filters out banners/ads by:
    - Excluding the top 25% and bottom 15% of the frame (banners live there)
    - Requiring a reasonable aspect ratio (not a thin strip like an ad banner)
    - Preferring contours near the vertical center of the frame
    """
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # The table surface is a BRIGHT, SATURATED blue/green/teal.
    # Require high saturation (S>=60) and brightness (V>=60) to
    # exclude the darker backdrop/advertising behind the table.
    blue = cv2.inRange(hsv, (95, 60, 60), (130, 255, 220))
    green = cv2.inRange(hsv, (40, 60, 60), (95, 255, 220))
    teal = cv2.inRange(hsv, (85, 50, 50), (135, 255, 230))
    surface = blue | green | teal

    # Table is in the middle portion of the frame.
    zone = np.zeros_like(surface)
    zone[int(h * 0.25):int(h * 0.80), int(w * 0.05):int(w * 0.95)] = 255
    surface = surface & zone

    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # Less closing (2 instead of 3) to avoid merging table with backdrop
    surface = cv2.morphologyEx(surface, cv2.MORPH_CLOSE, k5, iterations=2)
    surface = cv2.morphologyEx(surface, cv2.MORPH_OPEN, k5, iterations=3)

    contours, _ = cv2.findContours(surface, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None, None

    def _filter_candidates(contour_list):
        min_area = h * w * 0.01
        out = []
        for c in contour_list:
            area = cv2.contourArea(c)
            if area < min_area:
                continue
            bx, by, bw, bh = cv2.boundingRect(c)
            if bh < 10:
                continue
            aspect = bw / (bh + 1)
            if aspect > 6.0:
                continue
            cy = by + bh / 2
            center_dist = abs(cy - h * 0.45)
            out.append((c, area, center_dist, (bx, by, bw, bh)))
        return out

    candidates = _filter_candidates(contours)
    if not candidates:
        # Fallback: looser HSV for green/darker blue tables (e.g. home recordings)
        blue_loose = cv2.inRange(hsv, (90, 25, 25), (135, 255, 255))
        green_loose = cv2.inRange(hsv, (32, 25, 25), (95, 255, 255))
        surface2 = (blue_loose | green_loose) & zone
        surface2 = cv2.morphologyEx(surface2, cv2.MORPH_CLOSE, k5, iterations=2)
        surface2 = cv2.morphologyEx(surface2, cv2.MORPH_OPEN, k5, iterations=2)
        contours2, _ = cv2.findContours(surface2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = _filter_candidates(contours2)
        if candidates:
            surface = surface2

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: (-x[1], x[2]))
    best = candidates[0]
    bx, by, bw, bh = best[3]
    return surface, (bx, by, bx + bw, by + bh)


def _detect_table_local_cv(frame):
    """
    Local CV table detection using color blob + white line edges.

    The blue/green color blob includes both the table TOP surface AND
    the table FRONT FACE (vertical panel). We can't use the blob bottom
    directly. Instead:
      1. Find the blue blob -> rough bounding box
      2. Find ALL white horizontal lines inside the blob
      3. Cluster them into far-edge, net, near-edge by y-position
      4. Use far-edge for top, near-edge for bottom, middle for net
      5. Left/right from the blob with slight inset

    Returns (corners, net_y) or (None, None).
    """
    h, w = frame.shape[:2]
    surface_mask, bbox = _find_table_surface(frame)
    if bbox is None:
        return None, None

    sx1, sy1, sx2, sy2 = bbox
    surf_w, surf_h = sx2 - sx1, sy2 - sy1
    print(f"  [LocalCV] Surface blob: x=[{sx1},{sx2}] y=[{sy1},{sy2}] ({surf_w}x{surf_h})", flush=True)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- Find ALL white horizontal lines inside the blob ---
    blob_zone = np.zeros((h, w), dtype=np.uint8)
    blob_zone[sy1:sy2, sx1:sx2] = 255

    white = cv2.inRange(hsv, (0, 0, 140), (180, 70, 255))
    white_blob = white & blob_zone

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny_blob = cv2.Canny(blurred, 50, 150) & blob_zone
    edges_blob = cv2.Canny(white_blob, 30, 100) | canny_blob

    min_len = max(15, surf_w // 8)
    max_gap = max(10, surf_w // 10)
    segs = cv2.HoughLinesP(edges_blob, 1, np.pi / 180, 20,
                           minLineLength=min_len, maxLineGap=max_gap)

    # Collect all horizontal white lines with their y-position and length
    h_lines = []  # (avg_y, length, seg)
    if segs is not None:
        for seg in segs.reshape(-1, 4):
            x1s, y1s, x2s, y2s = seg
            dx, dy = abs(x2s - x1s), abs(y2s - y1s)
            if dx < 5:
                continue
            angle = np.degrees(np.arctan2(dy, dx))
            if angle > 15:
                continue  # not horizontal
            avg_y = (y1s + y2s) / 2.0
            length = np.sqrt(dx * dx + dy * dy)
            if length < min_len * 0.7:
                continue
            h_lines.append((avg_y, length, seg.tolist()))

    h_lines.sort(key=lambda x: x[0])  # sort by y position (top to bottom)

    # --- Cluster horizontal lines into groups by y-position ---
    # Each group represents a table edge (far edge, net, near edge)
    groups = []
    cluster_gap = max(10, surf_h // 8)
    for avg_y, length, seg in h_lines:
        placed = False
        for g in groups:
            if abs(avg_y - g["avg_y"]) < cluster_gap:
                g["lines"].append((avg_y, length, seg))
                # Update weighted average y
                total_len = sum(l for _, l, _ in g["lines"])
                g["avg_y"] = sum(y * l for y, l, _ in g["lines"]) / total_len
                g["total_len"] = total_len
                placed = True
                break
        if not placed:
            groups.append({"avg_y": avg_y, "total_len": length,
                           "lines": [(avg_y, length, seg)]})

    # Sort groups by total line length (strongest first)
    groups.sort(key=lambda g: -g["total_len"])

    # We expect 2-3 prominent groups: far edge, net, near edge
    # Sort the top groups by y position
    top_groups = sorted(groups[:5], key=lambda g: g["avg_y"])

    print(f"  [LocalCV] Found {len(h_lines)} white H-lines in {len(groups)} groups", flush=True)

    # --- Assign groups to far-edge, net, near-edge ---
    top_y = sy1
    bot_y = sy2
    net_y = (sy1 + sy2) // 2
    table_w = sx2 - sx1

    # Blob aspect: if height/width is small (<0.5), blob is likely just the
    # playing surface (e.g. 134224). If large (>0.5), blob may include
    # front face (e.g. 153355) and we must constrain the bottom.
    table_w = sx2 - sx1
    blob_aspect = surf_h / (table_w + 1e-6)

    if len(top_groups) >= 3:
        top_y = int(top_groups[0]["avg_y"])
        rest = top_groups[1:]
        rest.sort(key=lambda g: -g["total_len"])
        net_y = int(rest[0]["avg_y"])
        # Bottom group = the lowest by y (the near edge)
        bottom_group_y = int(top_groups[-1]["avg_y"])
        dist_top_net = net_y - top_y

        if blob_aspect <= 0.50:
            # Blob is compact: trust the white lines (134224-style)
            bot_y = bottom_group_y
        else:
            # Blob is tall, may include front face: near edge at most
            # 1.5x (net - far_edge) below net
            max_bot = net_y + int(dist_top_net * 1.5)
            if bottom_group_y <= max_bot:
                bot_y = bottom_group_y
            else:
                best_bot = None
                for g in top_groups[1:]:
                    gy = int(g["avg_y"])
                    if gy > net_y and gy <= max_bot:
                        if best_bot is None or gy > best_bot:
                            best_bot = gy
                bot_y = best_bot if best_bot is not None else max_bot
    elif len(top_groups) == 2:
        top_y = int(top_groups[0]["avg_y"])
        second_y = int(top_groups[1]["avg_y"])
        dist = second_y - top_y
        if dist < table_w * 0.25:
            # Likely far edge + net → calculate near edge
            net_y = second_y
            bot_y = net_y + int((net_y - top_y) * 1.3)
        else:
            # Far edge + near edge → net = midpoint
            bot_y = second_y
            net_y = (top_y + bot_y) // 2
    elif len(top_groups) == 1:
        line_y = int(top_groups[0]["avg_y"])
        mid = (sy1 + sy2) // 2
        if abs(line_y - sy1) < abs(line_y - mid):
            top_y = line_y
        else:
            net_y = line_y

    # Final sanity: only clamp if blob was clearly wrong (front face included)
    max_table_h = int(table_w * 0.55)
    if bot_y - top_y > max_table_h:
        bot_y = top_y + max_table_h
        print(f"  [LocalCV] Clamped height to {max_table_h}px", flush=True)

    # Net must be between top and bottom
    if net_y <= top_y or net_y >= bot_y:
        net_y = (top_y + bot_y) // 2

    # Left/right: use blob bounds with a small inset
    inset_x = max(2, surf_w // 30)
    left_x = sx1 + inset_x
    right_x = sx2 - inset_x

    # Corners: TL, TR, BR, BL
    corners = np.array([
        [left_x, top_y],
        [right_x, top_y],
        [right_x, bot_y],
        [left_x, bot_y],
    ], dtype=np.float32)

    tw = right_x - left_x
    th_t = bot_y - top_y
    print(f"  [LocalCV] Table {tw}x{th_t}, net at y={net_y}", flush=True)

    return corners, net_y


class KimiK2Detector:
    """Uses Moonshot (Kimi K2.5) or IFM K2 Think API for table/ball detection."""

    def __init__(self, api_key=None):
        self.api_key = api_key or _get_api_key()
        self._client = None
        self._base_url = None
        self._model = None

    def _client_or_raise(self):
        if not self.api_key:
            raise ValueError("MOONSHOT_API_KEY or KIMI_K2_API_KEY not set. Add to .env or environment.")
        if self._client is None:
            base_url, model = _get_base_url_and_model(self.api_key)
            self._base_url = base_url
            self._model = model
            try:
                from openai import OpenAI
                # 90s timeout so K2 Think doesn't hang (reasoning can be slow)
                self._client = OpenAI(api_key=self.api_key, base_url=base_url, timeout=90.0)
            except ImportError:
                raise ImportError("Install openai: pip install openai")
        return self._client

    def _model_name(self):
        if self._model is None:
            _, self._model = _get_base_url_and_model(self.api_key or _get_api_key())
        return self._model

    def _is_vision_supported(self):
        """K2 Think (IFM) is text/reasoning only; Moonshot Kimi K2.5 supports vision."""
        try:
            base_url, model = _get_base_url_and_model(self.api_key or _get_api_key())
        except ValueError:
            return False
        return "k2think" not in (base_url or "").lower() and "k2-think" not in (model or "").lower()

    def detect_table(self, frame):
        """
        Detect table court lines. Two modes:
        - Vision API (Kimi K2.5): sends frame image directly.
        - Reasoning API (K2 Think): uses local CV first, then K2 to refine/validate.
        Returns (corners, net_y).
        """
        if frame is None or frame.size == 0:
            return None, None

        if self._is_vision_supported():
            return self._detect_table_vision(frame)
        else:
            return self._detect_table_reasoning(frame)

    def _detect_table_vision(self, frame):
        """Send frame image to a vision-capable API (e.g. Kimi K2.5)."""
        b64, img_h, img_w = _frame_to_base64_jpeg(frame, max_size=1280)
        data_uri = f"data:image/jpeg;base64,{b64}"

        prompt = (
            f"This image is a single frame from a table tennis match (resolution {img_w}x{img_h}). "
            "Identify the COURT LINES: (1) The four corners of the table playing surface in pixel coordinates "
            "(order: top-left, top-right, bottom-right, bottom-left). "
            "(2) The horizontal net line: give the approximate y pixel of the center of the net. "
            "Reply with ONLY a valid JSON object, no other text:\n"
            '{"corners": [[x1,y1], [x2,y2], [x3,y3], [x4,y4]], "net_y": number}\n'
            "Use numbers only. net_y is the y-coordinate of the net line."
        )
        try:
            client = self._client_or_raise()
            completion = client.chat.completions.create(
                model=self._model_name(),
                messages=[
                    {"role": "system", "content": "You output only valid JSON. No markdown, no explanation."},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": prompt},
                    ]},
                ],
                max_tokens=512,
            )
            text = completion.choices[0].message.content
            corners, net_y = _parse_corners_json(text, 0, 0)
            if corners is not None and corners.shape[0] == 4:
                h, w = frame.shape[:2]
                _, img_h, img_w = _frame_to_base64_jpeg(frame, max_size=1280)
                if (img_w, img_h) != (w, h):
                    sx, sy = w / img_w, h / img_h
                    corners[:, 0] *= sx
                    corners[:, 1] *= sy
                    if net_y is not None:
                        net_y = int(net_y * sy)
                return corners, net_y
        except Exception as e:
            print(f"[K2] detect_table_vision error: {e}")
        return None, None

    def _detect_table_reasoning(self, frame):
        """
        K2 Think (text-only): Hybrid approach.
        1. Use local CV to find the table surface color region.
        2. Extract lines ONLY near that surface (not banners/scoreboards).
        3. Send filtered lines + tight surface constraints to K2 Think.
        4. Validate K2's answer against the surface region.
        5. If K2 fails validation or errors, fall back to pure local CV.
        """
        h, w = frame.shape[:2]
        print(f"  [K2 Think] Analyzing frame ({w}x{h})...", flush=True)

        # --- Step 1: Find table surface ---
        surface_mask, bbox = _find_table_surface(frame)
        if bbox is None:
            print("  [K2 Think] No surface found, trying local CV...", flush=True)
            return _detect_table_local_cv(frame)

        sx1, sy1, sx2, sy2 = bbox
        surf_w, surf_h = sx2 - sx1, sy2 - sy1
        print(f"  [K2 Think] Surface: x=[{sx1},{sx2}] y=[{sy1},{sy2}] ({surf_w}x{surf_h})", flush=True)

        # --- Step 2: Find lines ONLY near the surface ---
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        mx = int(surf_w * 0.20)
        my = int(surf_h * 0.30)
        zy1, zy2 = max(0, sy1 - my), min(h, sy2 + my)
        zx1, zx2 = max(0, sx1 - mx), min(w, sx2 + mx)

        search_zone = np.zeros((h, w), dtype=np.uint8)
        search_zone[zy1:zy2, zx1:zx2] = 255

        white = cv2.inRange(hsv, (0, 0, 140), (180, 80, 255))
        light = cv2.inRange(hsv, (0, 0, 100), (180, 50, 210))
        line_mask = (white | light) & search_zone

        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        canny = cv2.Canny(blurred, 50, 150) & search_zone
        edges = cv2.Canny(line_mask, 30, 100) | canny

        min_len = max(20, min(surf_w, surf_h) // 5)
        max_gap = max(12, min(surf_w, surf_h) // 8)
        segments = []
        for thresh in [40, 25, 15]:
            segs = cv2.HoughLinesP(edges, 1, np.pi / 180, thresh,
                                   minLineLength=min_len, maxLineGap=max_gap)
            if segs is not None:
                for s in segs.reshape(-1, 4):
                    segments.append(s.tolist())
            if len(segments) >= 25:
                break

        if len(segments) < 3:
            print("  [K2 Think] Few lines near surface, using local CV...", flush=True)
            return _detect_table_local_cv(frame)

        # Classify
        h_lines, v_lines, d_lines = [], [], []
        for seg in segments:
            x1s, y1s, x2s, y2s = seg
            dx, dy = abs(x2s - x1s), abs(y2s - y1s)
            length = int(np.sqrt(dx * dx + dy * dy))
            if length < 5:
                continue
            angle = np.degrees(np.arctan2(dy, dx))
            mid_x, mid_y = (x1s + x2s) // 2, (y1s + y2s) // 2
            entry = {"seg": seg, "len": length, "angle": round(angle, 1), "mid": [mid_x, mid_y]}
            if angle < 25:
                h_lines.append(entry)
            elif angle > 55:
                v_lines.append(entry)
            else:
                d_lines.append(entry)

        h_lines.sort(key=lambda x: -x["len"])
        v_lines.sort(key=lambda x: -x["len"])
        d_lines.sort(key=lambda x: -x["len"])
        h_top, v_top, d_top = h_lines[:10], v_lines[:10], d_lines[:6]

        print(f"  [K2 Think] {len(h_top)}H + {len(v_top)}V + {len(d_top)}D lines near surface, "
              f"calling K2 Think (30-60s)...", flush=True)

        # --- Step 3: Build prompt with TIGHT surface constraint ---
        def fmt(lines):
            return "\n".join(
                f"  L{i}: ({l['seg'][0]},{l['seg'][1]})->({l['seg'][2]},{l['seg'][3]}) "
                f"len={l['len']} angle={l['angle']}deg"
                for i, l in enumerate(lines))

        prompt = (
            f"Frame: {w}x{h} pixels.\n\n"
            f"COLOR DETECTION found the table surface (dark blue/green) at:\n"
            f"  x=[{sx1},{sx2}]  y=[{sy1},{sy2}]  size={surf_w}x{surf_h}\n"
            f"  center=({(sx1+sx2)//2},{(sy1+sy2)//2})\n\n"
            f"CRITICAL: ALL table corners MUST be within or very close to this region.\n"
            f"Any corners at y<{max(0,sy1-my)} or y>{min(h,sy2+my)} or "
            f"x<{max(0,sx1-mx)} or x>{min(w,sx2+mx)} are WRONG.\n\n"
            f"HORIZONTAL lines near surface:\n{fmt(h_top)}\n\n"
            f"VERTICAL lines near surface:\n{fmt(v_top)}\n"
        )
        if d_top:
            prompt += f"\nDIAGONAL:\n{fmt(d_top)}\n"
        prompt += (
            f"\nFind:\n"
            f"1. Four corners of TABLE SURFACE: top-left, top-right, bottom-right, bottom-left.\n"
            f"   Must be near x=[{sx1},{sx2}] y=[{sy1},{sy2}].\n"
            f"2. Net y-coordinate (horizontal line between top and bottom edges).\n\n"
            f"Reply with ONLY valid JSON:\n"
            f'  {{"corners": [[x1,y1],[x2,y2],[x3,y3],[x4,y4]], "net_y": number}}'
        )

        # --- Step 4: Call K2 Think ---
        try:
            client = self._client_or_raise()
            completion = client.chat.completions.create(
                model=self._model_name(),
                messages=[
                    {"role": "system", "content": "You are a spatial reasoning expert. You analyze text descriptions of geometric lines to identify table tennis tables."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1024,
            )
            text = completion.choices[0].message.content
            text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
            print(f"  [K2 Think] Raw: {text[:180]}...", flush=True)
            corners, net_y = _parse_corners_json(text, h, w)

            if corners is not None and corners.shape[0] == 4:
                tw = np.linalg.norm(corners[1] - corners[0])
                th_t = np.linalg.norm(corners[3] - corners[0])
                cx = np.mean(corners[:, 0])
                cy = np.mean(corners[:, 1])
                surf_cx = (sx1 + sx2) / 2.0
                surf_cy = (sy1 + sy2) / 2.0
                dist = np.sqrt((cx - surf_cx) ** 2 + (cy - surf_cy) ** 2)

                # --- Step 5: VALIDATE against surface ---
                reject = None
                if dist > max(surf_w, surf_h) * 0.6:
                    reject = f"center ({cx:.0f},{cy:.0f}) too far from surface ({surf_cx:.0f},{surf_cy:.0f})"
                elif tw > w * 0.70 or th_t > h * 0.55:
                    reject = f"size {tw:.0f}x{th_t:.0f} too large for frame"
                elif tw / (surf_w + 1) > 2.5 or tw / (surf_w + 1) < 0.25:
                    reject = f"width {tw:.0f} vs surface {surf_w} mismatch"
                elif th_t < 10:
                    reject = f"height {th_t:.0f} too small"

                if reject:
                    print(f"  [K2 Think] REJECTED: {reject}. Falling back to local CV.", flush=True)
                else:
                    print(f"  [K2 Think] Table {tw:.0f}x{th_t:.0f}" +
                          (f", net at y={net_y}" if net_y else "") +
                          " (validated)", flush=True)
                    return corners, net_y
            else:
                print("  [K2 Think] Could not parse corners.", flush=True)
        except Exception as e:
            print(f"  [K2 Think] API error: {e}", flush=True)

        # --- Step 6: Fallback to pure local CV ---
        print("  [K2 Think] Using local CV fallback...", flush=True)
        return _detect_table_local_cv(frame)

    def detect_ball(self, frame):
        """
        Ask model for ball position. Returns dict with 'ball_found' and 'center' (x,y) or None.
        """
        if frame is None or frame.size == 0:
            return {"ball_found": False, "center": None}
        if not self._is_vision_supported():
            return {"ball_found": False, "center": None}
        b64, img_h, img_w = _frame_to_base64_jpeg(frame, max_size=960)
        data_uri = f"data:image/jpeg;base64,{b64}"

        prompt = (
            f"This is a table tennis frame ({img_w}x{img_h}). "
            "Is the ball visible? If yes, give its approximate center in pixel coordinates. "
            "Reply with ONLY a JSON object: {\"ball_found\": true or false, \"x\": number, \"y\": number}. "
            "If ball_found is false, omit x and y."
        )
        try:
            client = self._client_or_raise()
            completion = client.chat.completions.create(
                model=self._model_name(),
                messages=[
                    {"role": "system", "content": "You output only valid JSON."},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": data_uri}},
                        {"type": "text", "text": prompt},
                    ]},
                ],
                max_tokens=128,
            )
            text = completion.choices[0].message.content
            out = _parse_ball_json(text)
            if out.get("ball_found") and out.get("center"):
                h, w = frame.shape[:2]
                if (img_w, img_h) != (w, h):
                    x, y = out["center"]
                    out["center"] = (x * w / img_w, y * h / img_h)
            return out
        except Exception as e:
            print(f"[Kimi K2] detect_ball error: {e}")
        return {"ball_found": False, "center": None}


class KimiK2HybridDetector:
    """
    Uses Kimi K2 for court/table line detection (4 edges + net). Returns corners + net_y for drawing.
    Main pipeline uses this for .detect(frame) and .kimi.detect_ball(frame).
    """

    def __init__(self, redetect_every=90, api_key=None):
        self.kimi = KimiK2Detector(api_key=api_key)
        self.redetect_every = redetect_every
        self._homography = None
        self._corners = None

    def detect(self, frame):
        """
        Detect court lines (table + net) on this frame using Kimi K2. Returns dict:
          locked, corners, homography, method, net_y (for drawing the net line).
        """
        corners, net_y = self.kimi.detect_table(frame)
        if corners is not None and len(corners) == 4:
            src = np.array(corners, dtype=np.float32).reshape(4, 2)
            dst = np.array([[0, 0], [TABLE_W, 0], [TABLE_W, TABLE_H], [0, TABLE_H]], dtype=np.float32)
            homography = cv2.getPerspectiveTransform(src, dst)
            self._corners = corners
            self._homography = homography
            return {
                "locked": True,
                "corners": corners,
                "homography": homography,
                "method": "kimi-k2",
                "net_y": net_y,
            }
        return {"locked": False, "corners": None, "homography": None, "method": None, "net_y": None}
