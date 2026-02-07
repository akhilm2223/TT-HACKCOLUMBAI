"""
Court / Table Lines Detection
=============================
Detects table tennis table corners using multiple strategies.

Key insights from Paris 2024 video analysis:
  - Pink LED barriers in background create 1024+ px/row bands spanning 82% of frame
  - Actual table borders create ~300 px/row bands spanning ~35% of frame
  - At low thresholds, table top+bottom borders merge (connected by side-border pixels)
  - Scattered noise pixels stretch x-extent to frame edges

Strategy order:
  1. Pink/white peak-based + profile scan (most reliable)
  2. Rectangle detector
  3. K-means + Hough
  4. Direct Canny + Hough
  5. Surface color contour (last resort)
"""
import cv2
import numpy as np

# ============================================================
# GEOMETRY HELPERS
# ============================================================

def _line_intersection(p1, p2, p3, p4):
    """Intersection of line(p1->p2) and line(p3->p4). Returns (x,y) or None."""
    d1 = np.array([p2[0] - p1[0], p2[1] - p1[1]], dtype=np.float64)
    d2 = np.array([p4[0] - p3[0], p4[1] - p3[1]], dtype=np.float64)
    cross = d1[0] * d2[1] - d1[1] * d2[0]
    if abs(cross) < 1e-8:
        return None
    x = np.array([p3[0] - p1[0], p3[1] - p1[1]], dtype=np.float64)
    t = (x[0] * d2[1] - x[1] * d2[0]) / cross
    return (float(p1[0] + d1[0] * t), float(p1[1] + d1[1] * t))


def _angle_deg(dx, dy):
    return np.degrees(np.arctan2(abs(dy), abs(dx)))


def _seg_length(seg):
    return np.sqrt((seg[2] - seg[0]) ** 2 + (seg[3] - seg[1]) ** 2)


def _order_corners(pts):
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).flatten()
    tl = pts[np.argmin(s)]
    br = pts[np.argmax(s)]
    tr = pts[np.argmin(d)]
    bl = pts[np.argmax(d)]
    return np.array([tl, tr, br, bl], dtype=np.float32)


def _valid_table(corners, frame_h=0, frame_w=0, min_area=2000, aspect_range=(1.4, 5.0)):
    if corners is None or len(corners) != 4:
        return False
    area = cv2.contourArea(corners.reshape(-1, 1, 2).astype(np.float32))
    if area < min_area:
        return False
    w1 = np.linalg.norm(corners[1] - corners[0])
    w2 = np.linalg.norm(corners[2] - corners[3])
    h1 = np.linalg.norm(corners[3] - corners[0])
    h2 = np.linalg.norm(corners[2] - corners[1])
    tw = (w1 + w2) / 2
    th = (h1 + h2) / 2
    if tw < 40 or th < 20:
        return False
    aspect = tw / (th + 1e-6)
    if not (aspect_range[0] <= aspect <= aspect_range[1]):
        return False
    if frame_w > 0 and tw > frame_w * 0.50:
        return False
    if frame_h > 0 and th > frame_h * 0.40:
        return False
    return True


# ============================================================
# STRATEGY 0: Find table surface first, then find the 5 lines
# (4 edges + net) on it. Surface constrains where to look.
# ============================================================

def _find_surface_roi(frame):
    """
    Quickly find the approximate bounding box of the table playing surface
    using color segmentation. Returns (y_top, y_bot, x_left, x_right) or None.
    """
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Table surface: dark blue / dark green / teal
    blue = cv2.inRange(hsv, (90, 30, 20), (130, 255, 200))
    green = cv2.inRange(hsv, (35, 30, 20), (90, 255, 200))
    teal = cv2.inRange(hsv, (80, 20, 15), (135, 255, 220))
    mask = blue | green | teal

    # Center zone only
    zone = np.zeros_like(mask)
    y1z, y2z = int(h * 0.10), int(h * 0.85)
    x1z, x2z = int(w * 0.05), int(w * 0.95)
    zone[y1z:y2z, x1z:x2z] = 255
    mask = mask & zone

    # Close small gaps
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k5, iterations=3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k5, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Find largest roughly-centered contour
    best = None
    best_area = h * w * 0.015  # min 1.5% of frame
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < best_area:
            continue
        M = cv2.moments(cnt)
        if M['m00'] == 0:
            continue
        cx = M['m10'] / M['m00']
        cy = M['m01'] / M['m00']
        if w * 0.15 < cx < w * 0.85 and h * 0.15 < cy < h * 0.80:
            if area > best_area:
                best_area = area
                best = cnt

    if best is None:
        return None

    x, y, bw, bh = cv2.boundingRect(best)
    return (y, y + bh, x, x + bw)


def _strategy_find_table_lines(frame):
    """
    Two-phase approach:
      Phase 1: Find approximate table surface using color -> defines search region
      Phase 2: Find the actual white edge lines & net ONLY near that surface
    """
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- Phase 1: Find approximate table surface region ---
    roi = _find_surface_roi(frame)
    if roi is None:
        return None, None

    sy_top, sy_bot, sx_left, sx_right = roi
    surf_w = sx_right - sx_left
    surf_h = sy_bot - sy_top
    print(f"    Surface ROI: x=[{sx_left},{sx_right}] y=[{sy_top},{sy_bot}]"
          f" ({surf_w}x{surf_h})")

    if surf_w < 40 or surf_h < 15:
        return None, None

    # --- Phase 2: Search for edge lines ONLY near the surface border ---
    # Add a small margin around the surface (lines are AT the edges)
    margin_x = int(surf_w * 0.15)
    margin_y = int(surf_h * 0.25)
    search_y1 = max(0, sy_top - margin_y)
    search_y2 = min(h, sy_bot + margin_y)
    search_x1 = max(0, sx_left - margin_x)
    search_x2 = min(w, sx_right + margin_x)

    # Build edge mask restricted to the search zone
    zone = np.zeros((h, w), dtype=np.uint8)
    zone[search_y1:search_y2, search_x1:search_x2] = 255

    # White lines on table (high brightness, low saturation)
    white = cv2.inRange(hsv, (0, 0, 150), (180, 80, 255))
    # Light grey (net, edge markings)
    light = cv2.inRange(hsv, (0, 0, 110), (180, 50, 210))

    line_mask = (white | light) & zone

    # Light cleanup
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    line_mask = cv2.morphologyEx(line_mask, cv2.MORPH_CLOSE, k3, iterations=1)

    # Canny edges from grayscale (catches contrast boundaries at table edges)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blurred, 50, 150) & zone

    # Combined edges
    combined_edges = cv2.Canny(line_mask, 30, 100) | canny

    # --- Find line segments with Hough ---
    min_len = max(25, min(surf_w, surf_h) // 5)
    max_gap = max(15, min(surf_w, surf_h) // 8)

    all_segs = []
    for thresh in [40, 25, 15]:
        segs = cv2.HoughLinesP(combined_edges, 1, np.pi / 180, thresh,
                               minLineLength=min_len, maxLineGap=max_gap)
        if segs is not None:
            all_segs.extend(segs.reshape(-1, 4).tolist())
        if len(all_segs) >= 10:
            break

    if len(all_segs) < 4:
        print("    Not enough line segments found")
        return None, None

    # --- Classify into horizontal and near-vertical (allow perspective slant) ---
    horizontals = []  # (y_mid, length, seg)
    verticals = []    # (x_mid, length, seg)

    for seg in all_segs:
        x1, y1, x2, y2 = seg
        angle = _angle_deg(float(x2 - x1), float(y2 - y1))
        length = _seg_length(seg)
        y_mid = (y1 + y2) / 2.0
        x_mid = (x1 + x2) / 2.0

        if angle < 25:  # horizontal
            horizontals.append((y_mid, length, seg))
        elif angle > 55:  # vertical / near-vertical
            verticals.append((x_mid, length, seg))

    if len(horizontals) < 2:
        print("    Not enough horizontal lines")
        return None, None

    # --- Group by position (cluster nearby segments) ---
    merge_dist_y = max(10, surf_h * 0.10)
    merge_dist_x = max(10, surf_w * 0.08)

    h_groups = _group_lines(horizontals, merge_dist_y)
    v_groups = _group_lines(verticals, merge_dist_x)

    # --- Determine the 4 edge lines ---
    # For horizontal: find the top edge and bottom edge of the SURFACE
    # The top-h line should be near sy_top, bottom-h near sy_bot
    h_groups.sort(key=lambda g: g[0])
    v_groups.sort(key=lambda g: g[0])

    # Find the horizontal line closest to the surface top edge
    top_line = None
    top_dist = float('inf')
    for grp in h_groups:
        d = abs(grp[0] - sy_top)
        if d < top_dist and grp[0] < sy_top + surf_h * 0.35:
            top_dist = d
            top_line = grp

    # Find the horizontal line closest to the surface bottom edge
    bot_line = None
    bot_dist = float('inf')
    for grp in h_groups:
        if grp is top_line:
            continue
        d = abs(grp[0] - sy_bot)
        if d < bot_dist and grp[0] > sy_top + surf_h * 0.5:
            bot_dist = d
            bot_line = grp

    if top_line is None or bot_line is None:
        print("    Could not find top/bottom edge lines")
        return None, None

    # Find left and right vertical lines closest to surface edges
    left_line = None
    left_dist = float('inf')
    for grp in v_groups:
        d = abs(grp[0] - sx_left)
        if d < left_dist and grp[0] < sx_left + surf_w * 0.35:
            left_dist = d
            left_line = grp

    right_line = None
    right_dist = float('inf')
    for grp in v_groups:
        if grp is left_line:
            continue
        d = abs(grp[0] - sx_right)
        if d < right_dist and grp[0] > sx_left + surf_w * 0.5:
            right_dist = d
            right_line = grp

    # --- Build corners ---
    top_y = top_line[0]
    bot_y = bot_line[0]

    if left_line is not None and right_line is not None:
        left_x = left_line[0]
        right_x = right_line[0]
    else:
        # Fall back to surface edges if vertical lines not found
        left_x = float(sx_left)
        right_x = float(sx_right)
        print("    Using surface edges for left/right (vertical lines weak)")

    # Try intersection-based corners for perspective accuracy
    top_seg = max(top_line[2], key=lambda s: _seg_length(s))
    bot_seg = max(bot_line[2], key=lambda s: _seg_length(s))

    if left_line is not None and right_line is not None:
        left_seg = max(left_line[2], key=lambda s: _seg_length(s))
        right_seg = max(right_line[2], key=lambda s: _seg_length(s))

        tl = _line_intersection(
            (top_seg[0], top_seg[1]), (top_seg[2], top_seg[3]),
            (left_seg[0], left_seg[1]), (left_seg[2], left_seg[3]))
        tr = _line_intersection(
            (top_seg[0], top_seg[1]), (top_seg[2], top_seg[3]),
            (right_seg[0], right_seg[1]), (right_seg[2], right_seg[3]))
        bl = _line_intersection(
            (bot_seg[0], bot_seg[1]), (bot_seg[2], bot_seg[3]),
            (left_seg[0], left_seg[1]), (left_seg[2], left_seg[3]))
        br = _line_intersection(
            (bot_seg[0], bot_seg[1]), (bot_seg[2], bot_seg[3]),
            (right_seg[0], right_seg[1]), (right_seg[2], right_seg[3]))

        if all(c is not None for c in [tl, tr, bl, br]):
            corners = np.array([tl, tr, br, bl], dtype=np.float32)
        else:
            corners = np.array([
                [left_x, top_y], [right_x, top_y],
                [right_x, bot_y], [left_x, bot_y]
            ], dtype=np.float32)
    else:
        corners = np.array([
            [left_x, top_y], [right_x, top_y],
            [right_x, bot_y], [left_x, bot_y]
        ], dtype=np.float32)

    if not _valid_table(corners, h, w, aspect_range=(1.3, 5.5)):
        print("    Lines found but rectangle invalid")
        return None, None

    # --- Find the net ---
    net_y = None
    for grp in h_groups:
        if grp is top_line or grp is bot_line:
            continue
        ny = grp[0]
        if top_y + (bot_y - top_y) * 0.2 < ny < bot_y - (bot_y - top_y) * 0.2:
            net_y = int(ny)
            break

    tw = np.linalg.norm(corners[1] - corners[0])
    th_t = np.linalg.norm(corners[3] - corners[0])
    msg = f"  [Strategy 0: surface+lines] Table {tw:.0f}x{th_t:.0f}"
    if net_y:
        msg += f", net at y={net_y}"
    print(msg)
    return corners, net_y


def _group_lines(items, merge_dist):
    """Group line segments by position (first element of tuple). Returns list of [avg_pos, total_length, [segs]]."""
    groups = []
    for pos, length, seg in items:
        merged = False
        for grp in groups:
            if abs(pos - grp[0]) < merge_dist:
                n = len(grp[2])
                grp[0] = (grp[0] * n + pos) / (n + 1)
                grp[1] += length
                grp[2].append(seg)
                merged = True
                break
        if not merged:
            groups.append([pos, length, [seg]])
    return groups


# ============================================================
# DENSE-BLOCK X-EXTENT FINDER
# ============================================================

def _find_dense_extent(col_counts, min_px=2, max_gap=30):
    """Find the longest contiguous block of occupied columns, ignoring scattered noise."""
    occupied = col_counts >= min_px
    runs = []
    run_start = None
    run_end = 0
    gap_count = 0
    for x in range(len(col_counts)):
        if occupied[x]:
            if run_start is None:
                run_start = x
            gap_count = 0
            run_end = x
        else:
            gap_count += 1
            if run_start is not None and gap_count > max_gap:
                runs.append((run_start, run_end))
                run_start = None
    if run_start is not None:
        runs.append((run_start, run_end))
    if not runs:
        return None, None
    longest = max(runs, key=lambda r: r[1] - r[0])
    return longest[0], longest[1]


# ============================================================
# PEAK-BASED BAND DETECTION
# ============================================================

def _add_band(mask, row_smooth, band_start, band_end, w, h_bands):
    peak_val = float(np.max(row_smooth[band_start:band_end + 1]))
    center = band_start + int(np.argmax(row_smooth[band_start:band_end + 1]))
    band_rows = mask[band_start:band_end + 1, :]
    band_col = np.sum(band_rows > 0, axis=0)
    band_thick = band_end - band_start + 1
    min_px = max(2, band_thick // 3)
    xl, xr = _find_dense_extent(band_col, min_px=min_px, max_gap=30)
    if xl is not None and xr is not None:
        h_bands.append({
            'center': center, 'peak': peak_val,
            'start': band_start, 'end': band_end,
            'xl': xl, 'xr': xr, 'xspan': xr - xl,
        })


def _find_h_bands(mask, row_smooth, above, w, h):
    h_bands = []
    in_band = False
    band_start = 0
    for y in range(h):
        if above[y] and not in_band:
            band_start = y
            in_band = True
        elif not above[y] and in_band:
            _add_band(mask, row_smooth, band_start, y - 1, w, h_bands)
            in_band = False
    if in_band:
        _add_band(mask, row_smooth, band_start, h - 1, w, h_bands)
    return h_bands


def _best_band_pair(h_bands, min_peak_sep, row_max, frame_h, frame_w):
    best = None
    best_score = -1
    for i in range(len(h_bands)):
        for j in range(i + 1, len(h_bands)):
            bi, bj = h_bands[i], h_bands[j]
            top_b = bi if bi['center'] < bj['center'] else bj
            bot_b = bj if bi['center'] < bj['center'] else bi
            top_y = top_b['center']
            bot_y = bot_b['center']
            if bot_y - top_y < min_peak_sep:
                continue
            left = min(top_b['xl'], bot_b['xl'])
            right = max(top_b['xr'], bot_b['xr'])
            tw = right - left
            th = bot_y - top_y
            if tw < 30 or th < 15:
                continue
            aspect = tw / (th + 1e-6)
            if not (1.4 <= aspect <= 5.0):
                continue
            if frame_w > 0 and tw > frame_w * 0.50:
                continue
            if frame_h > 0 and th > frame_h * 0.40:
                continue
            top_span = top_b['xspan']
            bot_span = bot_b['xspan']
            span_sim = min(top_span, bot_span) / (max(top_span, bot_span) + 1)
            overlap_left = max(top_b['xl'], bot_b['xl'])
            overlap_right = min(top_b['xr'], bot_b['xr'])
            if overlap_right > overlap_left:
                overlap = overlap_right - overlap_left
                overlap_ratio = overlap / (max(top_span, bot_span) + 1)
            else:
                overlap_ratio = 0
            cy = (top_y + bot_y) / 2
            pos_score = max(0, 1.0 - abs(cy - frame_h * 0.45) / (frame_h * 0.5))
            strength = (top_b['peak'] + bot_b['peak']) / (2 * row_max + 1)
            score = (span_sim * 0.35 + overlap_ratio * 0.25 +
                     pos_score * 0.20 + strength * 0.20)
            if score > best_score:
                best_score = score
                best = (top_y, bot_y, left, right)
    return best


def _peak_border_scan(mask, min_peak_height=80, min_peak_sep=20):
    """Find table borders via horizontal band detection + pair scoring."""
    h, w = mask.shape[:2]
    row_counts = np.sum(mask > 0, axis=1).astype(np.float64)
    kernel = np.ones(5) / 5.0
    row_smooth = np.convolve(row_counts, kernel, mode='same')
    row_max = np.max(row_smooth)
    if row_max < min_peak_height:
        return None
    # Multi-threshold: high thresholds split merged bands
    thresholds = sorted(set([
        row_max * 0.7, row_max * 0.5, row_max * 0.3,
        row_max * 0.2, float(min_peak_height),
    ]), reverse=True)
    for row_thresh in thresholds:
        if row_thresh < min_peak_height:
            continue
        above = row_smooth >= row_thresh
        h_bands = _find_h_bands(mask, row_smooth, above, w, h)
        if len(h_bands) < 2:
            continue
        result = _best_band_pair(h_bands, min_peak_sep, row_max, h, w)
        if result is not None:
            return result
    return None


# ============================================================
# HOUGH REFINEMENT
# ============================================================

def _refine_edge_hough(mask, pos, direction, margin, w, h):
    if direction == 'horizontal':
        y1b = max(0, pos - margin)
        y2b = min(h, pos + margin + 1)
        band = mask[y1b:y2b, :]
        if band.sum() == 0:
            return None
        min_len = max(15, w // 25)
        max_gap = max(20, w // 10)
        for thresh in (20, 12, 8):
            segs = cv2.HoughLinesP(band, 1, np.pi / 180, thresh,
                                   minLineLength=min_len, maxLineGap=max_gap)
            if segs is not None and len(segs) > 0:
                break
        if segs is None or len(segs) == 0:
            return None
        best = None
        best_len = 0
        for seg in segs.reshape(-1, 4):
            x1, y1s, x2, y2s = seg
            angle = _angle_deg(float(x2 - x1), float(y2s - y1s))
            length = _seg_length(seg)
            if angle < 25 and length > best_len:
                best_len = length
                best = ((float(x1), float(y1s + y1b)),
                        (float(x2), float(y2s + y1b)))
        return best
    else:
        x1b = max(0, pos - margin)
        x2b = min(w, pos + margin + 1)
        band = mask[:, x1b:x2b]
        if band.sum() == 0:
            return None
        min_len = max(15, h // 25)
        max_gap = max(20, h // 10)
        for thresh in (20, 12, 8):
            segs = cv2.HoughLinesP(band, 1, np.pi / 180, thresh,
                                   minLineLength=min_len, maxLineGap=max_gap)
            if segs is not None and len(segs) > 0:
                break
        if segs is None or len(segs) == 0:
            return None
        best = None
        best_len = 0
        for seg in segs.reshape(-1, 4):
            x1s, y1s, x2s, y2s = seg
            angle = _angle_deg(float(x2s - x1s), float(y2s - y1s))
            length = _seg_length(seg)
            if angle > 65 and length > best_len:
                best_len = length
                best = ((float(x1s + x1b), float(y1s)),
                        (float(x2s + x1b), float(y2s)))
        return best


def _try_hough_refine(mask, top, bot, left, right, h, w):
    margin = max(15, min(w, h) // 50)
    refine_pad = margin * 3
    mask_refine = mask.copy()
    rzone = np.zeros_like(mask_refine)
    ry1 = max(0, top - refine_pad)
    ry2 = min(h, bot + refine_pad)
    rx1 = max(0, left - refine_pad)
    rx2 = min(w, right + refine_pad)
    rzone[ry1:ry2, rx1:rx2] = 255
    mask_refine = mask_refine & rzone

    top_line = _refine_edge_hough(mask_refine, top, 'horizontal', margin, w, h)
    bot_line = _refine_edge_hough(mask_refine, bot, 'horizontal', margin, w, h)
    left_line = _refine_edge_hough(mask_refine, left, 'vertical', margin, w, h)
    right_line = _refine_edge_hough(mask_refine, right, 'vertical', margin, w, h)

    if all(l is not None for l in [top_line, bot_line, left_line, right_line]):
        tl = _line_intersection(top_line[0], top_line[1], left_line[0], left_line[1])
        tr = _line_intersection(top_line[0], top_line[1], right_line[0], right_line[1])
        bl = _line_intersection(bot_line[0], bot_line[1], left_line[0], left_line[1])
        br = _line_intersection(bot_line[0], bot_line[1], right_line[0], right_line[1])
        if all(c is not None for c in [tl, tr, bl, br]):
            return np.array([tl, tr, br, bl], dtype=np.float32)
    return None


# ============================================================
# MASKS
# ============================================================

def _build_pink_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pink = cv2.inRange(hsv, (130, 50, 30), (175, 255, 255))
    red = cv2.inRange(hsv, (0, 50, 30), (12, 255, 255))
    return pink | red


def _build_color_mask(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    pink = cv2.inRange(hsv, (130, 50, 30), (175, 255, 255))
    red = cv2.inRange(hsv, (0, 50, 30), (12, 255, 255))
    white = cv2.inRange(hsv, (0, 0, 180), (180, 50, 255))
    yellow = cv2.inRange(hsv, (15, 40, 150), (35, 255, 255))
    cyan = cv2.inRange(hsv, (80, 40, 150), (100, 255, 255))
    return pink | red | white | yellow | cyan


def _apply_zone(mask, h, w, y_frac, x_frac):
    y1 = int(h * y_frac[0])
    y2 = int(h * y_frac[1])
    x1 = int(w * x_frac[0])
    x2 = int(w * x_frac[1])
    zone = np.zeros_like(mask)
    zone[y1:y2, x1:x2] = 255
    return cv2.bitwise_and(mask, zone), (y1, y2, x1, x2)


def _profile_scan(mask, y1z, y2z, x1z, x2z, row_thresh_pct=0.08, col_thresh_pct=0.04):
    h_full, w_full = mask.shape[:2]
    row_counts = np.sum(mask > 0, axis=1)
    col_counts = np.sum(mask > 0, axis=0)
    zone_w = x2z - x1z
    zone_h = y2z - y1z
    min_row_px = max(5, zone_w * row_thresh_pct)
    min_col_px = max(3, zone_h * col_thresh_pct)

    top = bot = left = right = None
    for y in range(y1z, y2z):
        if row_counts[y] >= min_row_px:
            top = y; break
    for y in range(y2z - 1, y1z - 1, -1):
        if row_counts[y] >= min_row_px:
            bot = y; break
    for x in range(x1z, x2z):
        if col_counts[x] >= min_col_px:
            left = x; break
    for x in range(x2z - 1, x1z - 1, -1):
        if col_counts[x] >= min_col_px:
            right = x; break

    if any(v is None for v in [top, bot, left, right]):
        return None
    tw = right - left
    th = bot - top
    if tw < 40 or th < 20:
        return None
    aspect = tw / (th + 1e-6)
    if not (1.4 <= aspect <= 5.0):
        return None
    if w_full > 0 and tw > w_full * 0.50:
        return None
    if h_full > 0 and th > h_full * 0.40:
        return None
    return top, bot, left, right


# ============================================================
# STRATEGY 1: Peak + Profile + Hough (MOST RELIABLE)
# ============================================================

def _strategy_border_lines(frame):
    h, w = frame.shape[:2]
    k3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # Pass 1: Pink-only peak detection
    pink_mask = _build_pink_mask(frame)
    pink_clean = cv2.morphologyEx(pink_mask, cv2.MORPH_CLOSE, k3, iterations=1)

    edges_approx = _peak_border_scan(pink_clean, min_peak_height=80)
    if edges_approx is not None:
        top, bot, left, right = edges_approx
        corners = _try_hough_refine(pink_clean, top, bot, left, right, h, w)
        if corners is not None and _valid_table(corners, h, w):
            tw_c = np.linalg.norm(corners[1] - corners[0])
            th_c = np.linalg.norm(corners[3] - corners[0])
            print(f"  [Strategy 1: Pink peak+Hough] {tw_c:.0f}x{th_c:.0f}")
            return corners
        corners = np.array([[left, top], [right, top], [right, bot], [left, bot]], dtype=np.float32)
        if _valid_table(corners, h, w):
            print(f"  [Strategy 1: Pink peak scan] {right - left}x{bot - top}")
            return corners

    # Pass 2: All-color peak detection
    color_mask = _build_color_mask(frame)
    color_clean = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, k3, iterations=2)
    color_clean = cv2.morphologyEx(color_clean, cv2.MORPH_OPEN, k3, iterations=1)

    edges_approx = _peak_border_scan(color_clean, min_peak_height=60)
    if edges_approx is not None:
        top, bot, left, right = edges_approx
        corners = _try_hough_refine(color_clean, top, bot, left, right, h, w)
        if corners is not None and _valid_table(corners, h, w):
            tw_c = np.linalg.norm(corners[1] - corners[0])
            th_c = np.linalg.norm(corners[3] - corners[0])
            print(f"  [Strategy 1: Color peak+Hough] {tw_c:.0f}x{th_c:.0f}")
            return corners
        corners = np.array([[left, top], [right, top], [right, bot], [left, bot]], dtype=np.float32)
        if _valid_table(corners, h, w):
            print(f"  [Strategy 1: Color peak scan] {right - left}x{bot - top}")
            return corners

    # Pass 3: Zone profile scan (tight -> medium -> wide)
    zone_passes = [
        ((0.30, 0.62), (0.24, 0.68), 0.10, 0.04),
        ((0.25, 0.68), (0.18, 0.82), 0.06, 0.03),
        ((0.20, 0.75), (0.10, 0.90), 0.04, 0.02),
    ]
    edges_approx = None
    for (yf, xf, row_t, col_t) in zone_passes:
        mask_z, (y1, y2, x1, x2) = _apply_zone(color_clean, h, w, y_frac=yf, x_frac=xf)
        edges_approx = _profile_scan(mask_z, y1, y2, x1, x2,
                                      row_thresh_pct=row_t, col_thresh_pct=col_t)
        if edges_approx is not None:
            break

    if edges_approx is not None:
        top, bot, left, right = edges_approx
        corners = _try_hough_refine(color_clean, top, bot, left, right, h, w)
        if corners is not None and _valid_table(corners, h, w):
            tw_c = np.linalg.norm(corners[1] - corners[0])
            th_c = np.linalg.norm(corners[3] - corners[0])
            print(f"  [Strategy 1: Profile+Hough] {tw_c:.0f}x{th_c:.0f}")
            return corners
        corners = np.array([[left, top], [right, top], [right, bot], [left, bot]], dtype=np.float32)
        if _valid_table(corners, h, w):
            print(f"  [Strategy 1: Profile scan] {right - left}x{bot - top}")
            return corners

    # Pass 4: Hough-only fallback
    mask_hough, _ = _apply_zone(color_clean, h, w, y_frac=(0.20, 0.75), x_frac=(0.15, 0.85))
    min_dim = min(w, h)
    for thresh, minLen, maxGap in [(30, max(30, min_dim // 12), max(40, min_dim // 15)),
                                    (20, max(20, min_dim // 18), max(60, min_dim // 10)),
                                    (12, max(10, min_dim // 30), max(80, min_dim // 6))]:
        segs = cv2.HoughLinesP(mask_hough, 1, np.pi / 180, thresh,
                               minLineLength=minLen, maxLineGap=maxGap)
        if segs is not None and len(segs) >= 4:
            corners = _median_split_corners(segs.reshape(-1, 4), h, w)
            if corners is not None and _valid_table(corners, h, w):
                print(f"  [Strategy 1: Hough fallback]")
                return corners

    return None


def _median_split_corners(segs, h, w):
    horizontals = []
    verticals = []
    for seg in segs:
        x1, y1, x2, y2 = seg
        angle = _angle_deg(float(x2 - x1), float(y2 - y1))
        length = _seg_length(seg)
        if angle < 25:
            horizontals.append(((y1 + y2) / 2.0, length, seg))
        elif angle > 65:
            verticals.append(((x1 + x2) / 2.0, length, seg))
    if len(horizontals) < 2 or len(verticals) < 2:
        return None
    y_med = np.median([h_[0] for h_ in horizontals])
    x_med = np.median([v_[0] for v_ in verticals])
    top_segs = [(y, l, s) for y, l, s in horizontals if y < y_med]
    bot_segs = [(y, l, s) for y, l, s in horizontals if y >= y_med]
    left_segs = [(x, l, s) for x, l, s in verticals if x < x_med]
    right_segs = [(x, l, s) for x, l, s in verticals if x >= x_med]
    if not all([top_segs, bot_segs, left_segs, right_segs]):
        return None
    top_s = max(top_segs, key=lambda t: t[1])[2]
    bot_s = max(bot_segs, key=lambda t: t[1])[2]
    left_s = max(left_segs, key=lambda t: t[1])[2]
    right_s = max(right_segs, key=lambda t: t[1])[2]
    tl = _line_intersection((top_s[0], top_s[1]), (top_s[2], top_s[3]),
                            (left_s[0], left_s[1]), (left_s[2], left_s[3]))
    tr = _line_intersection((top_s[0], top_s[1]), (top_s[2], top_s[3]),
                            (right_s[0], right_s[1]), (right_s[2], right_s[3]))
    bl = _line_intersection((bot_s[0], bot_s[1]), (bot_s[2], bot_s[3]),
                            (left_s[0], left_s[1]), (left_s[2], left_s[3]))
    br = _line_intersection((bot_s[0], bot_s[1]), (bot_s[2], bot_s[3]),
                            (right_s[0], right_s[1]), (right_s[2], right_s[3]))
    if any(c is None for c in [tl, tr, bl, br]):
        return None
    return np.array([tl, tr, br, bl], dtype=np.float32)


# ============================================================
# STRATEGY 2: Rectangle detection
# ============================================================

def _strategy_rectangle(frame):
    h, w = frame.shape[:2]
    pyr = cv2.pyrDown(frame)
    timg = cv2.pyrUp(pyr, dstsize=(w, h))
    candidates = []
    for c in range(3):
        gray0 = timg[:, :, c]
        for lev in range(11):
            if lev == 0:
                gray = cv2.Canny(gray0, 0, 50, apertureSize=5)
                gray = cv2.dilate(gray, None)
            else:
                _, gray = cv2.threshold(gray0, int((lev + 1) * 255 / 11), 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(gray, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) != 4:
                    continue
                area = abs(cv2.contourArea(approx))
                if area < 2000 or area > h * w * 0.5:
                    continue
                if not cv2.isContourConvex(approx):
                    continue
                pts = approx.reshape(4, 2).astype(float)
                max_cosine = 0
                for j in range(2, 5):
                    v1 = pts[j % 4] - pts[(j - 1) % 4]
                    v2 = pts[(j - 2) % 4] - pts[(j - 1) % 4]
                    cosine = abs(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-10))
                    max_cosine = max(max_cosine, cosine)
                if max_cosine < 0.3:
                    corners = _order_corners(pts)
                    if _valid_table(corners, h, w):
                        candidates.append((area, corners))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    print(f"  [Strategy 2: Rectangle] Found {len(candidates)} candidates")
    return candidates[0][1]


# ============================================================
# STRATEGY 3: K-means + Hough
# ============================================================

def _kmeans_binarize(frame):
    h, w = frame.shape[:2]
    blurred = cv2.GaussianBlur(frame, (15, 15), 0)
    pixels = blurred.reshape(-1, 3).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, 4, None, criteria, 3, cv2.KMEANS_PP_CENTERS)
    line_idx = int(np.argmax(np.sum(centers, axis=1)))
    labels = labels.reshape(h, w)
    bin_img = np.uint8((labels == line_idx) * 255)
    kern_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    opened = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kern_open)
    lines_only = cv2.subtract(bin_img, opened)
    close_sz = min(101, max(21, w // 12))
    if close_sz % 2 == 0:
        close_sz += 1
    kern_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_sz, close_sz))
    return cv2.morphologyEx(lines_only, cv2.MORPH_CLOSE, kern_close)


def _hough_classify_intersect(edge_img, w, h):
    cx, cy = w / 2, h / 2
    for (thresh, minLen, maxGap) in [(50, max(80, w // 6), 100),
                                      (30, max(40, w // 10), 150),
                                      (20, 30, 200)]:
        segs = cv2.HoughLinesP(edge_img, 1, np.pi / 180, thresh,
                               minLineLength=minLen, maxLineGap=maxGap)
        if segs is not None and len(segs) >= 4:
            break
    if segs is None or len(segs) < 4:
        return None
    segs = segs.reshape(-1, 4)
    h_up, h_down, v_left, v_right = [], [], [], []
    for seg in segs:
        x1, y1, x2, y2 = seg
        angle = _angle_deg(float(x2 - x1), float(y2 - y1))
        if angle < 15:
            if y1 < cy and y2 < cy: h_up.append(seg)
            elif y1 > cy and y2 > cy: h_down.append(seg)
        elif angle > 75:
            if x1 < cx and x2 < cx: v_left.append(seg)
            elif x1 > cx and x2 > cx: v_right.append(seg)
    if not (h_up and h_down and v_left and v_right):
        h_up, h_down, v_left, v_right = [], [], [], []
        for seg in segs:
            x1, y1, x2, y2 = seg
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            angle = _angle_deg(float(x2 - x1), float(y2 - y1))
            if angle < 25:
                (h_up if my < cy else h_down).append(seg)
            elif angle > 65:
                (v_left if mx < cx else v_right).append(seg)
        if not (h_up and h_down and v_left and v_right):
            return None

    def intersect_all(horiz, vert):
        pts = []
        for hl in horiz:
            for vl in vert:
                p = _line_intersection((hl[0], hl[1]), (hl[2], hl[3]),
                                       (vl[0], vl[1]), (vl[2], vl[3]))
                if p and 0 <= p[0] <= w and 0 <= p[1] <= h:
                    pts.append(p)
        return pts

    center = np.array([cx, cy])
    def farthest(pts):
        if not pts: return None
        return max(pts, key=lambda p: np.linalg.norm(np.array(p) - center))

    tl = farthest(intersect_all(h_up, v_left))
    tr = farthest(intersect_all(h_up, v_right))
    br = farthest(intersect_all(h_down, v_right))
    bl = farthest(intersect_all(h_down, v_left))
    if any(c is None for c in [tl, tr, br, bl]):
        return None
    return np.array([tl, tr, br, bl], dtype=np.float32)


def _strategy_kmeans_hough(frame):
    h, w = frame.shape[:2]
    line_bin = _kmeans_binarize(frame)
    edges = cv2.Canny(line_bin, 50, 150)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges2 = cv2.Canny(gray, 50, 200, apertureSize=3)
    combined = cv2.bitwise_or(edges, edges2)
    corners = _hough_classify_intersect(combined, w, h)
    if corners is not None and _valid_table(corners, h, w):
        print("  [Strategy 3: K-means+Hough] Table found!")
        return corners
    corners = _hough_classify_intersect(line_bin, w, h)
    if corners is not None and _valid_table(corners, h, w):
        print("  [Strategy 3: K-means binary+Hough] Table found!")
        return corners
    return None


# ============================================================
# STRATEGY 4: Direct Canny + Hough
# ============================================================

def _strategy_direct_hough(frame):
    h, w = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    canny = cv2.Canny(gray, 50, 200, apertureSize=3)
    corners = _hough_classify_intersect(canny, w, h)
    if corners is not None and _valid_table(corners, h, w):
        print("  [Strategy 4: Direct Hough] Table found!")
        return corners
    return None


# ============================================================
# STRATEGY 5: Surface color (last resort)
# ============================================================

def _strategy_surface_color(frame):
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(hsv, (95, 60, 40), (125, 255, 200))
    green_mask = cv2.inRange(hsv, (40, 60, 40), (80, 255, 200))
    table_mask = blue_mask | green_mask
    zone = np.zeros_like(table_mask)
    y1z, y2z = int(h * 0.20), int(h * 0.70)
    x1z, x2z = int(w * 0.20), int(w * 0.80)
    zone[y1z:y2z, x1z:x2z] = 255
    table_mask = table_mask & zone
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    table_mask = cv2.morphologyEx(table_mask, cv2.MORPH_CLOSE, k, iterations=3)
    table_mask = cv2.morphologyEx(table_mask, cv2.MORPH_OPEN, k, iterations=2)
    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None
    for cnt in sorted(contours, key=cv2.contourArea, reverse=True)[:3]:
        area = cv2.contourArea(cnt)
        if area < h * w * 0.03:
            continue
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            corners = _order_corners(approx.reshape(-1, 2))
            if _valid_table(corners, h, w):
                print("  [Strategy 5: Surface color] Table found!")
                return corners
        rect = cv2.minAreaRect(cnt)
        box = cv2.boxPoints(rect)
        corners = _order_corners(box)
        if _valid_table(corners, h, w):
            print("  [Strategy 5: Surface color minAreaRect] Table found!")
            return corners
    return None


# ============================================================
# PUBLIC API
# ============================================================

def detect_table_corners(frame):
    """
    Returns (corners, net_y) or just corners for backward compat.
    corners: np.array (4,2) [TL, TR, BR, BL] or None.
    net_y: int y-coordinate of detected net, or None.
    """
    print("  Court detection: trying strategies...")

    # Strategy 0: Find 5 lines (4 edges + net) that form the table rectangle
    corners, net_y = _strategy_find_table_lines(frame)
    if corners is not None:
        return corners, net_y

    # Fallback strategies (return corners only, net_y=None)
    for strategy in [_strategy_border_lines, _strategy_rectangle,
                     _strategy_kmeans_hough, _strategy_direct_hough,
                     _strategy_surface_color]:
        corners = strategy(frame)
        if corners is not None:
            return corners, None

    print("  All strategies failed.")
    return None, None


def detect_table_corners_kmean_hough(frame, gray=None):
    corners, _ = detect_table_corners(frame)
    return corners


def draw_court_overlay(frame, corners, color=(0, 255, 0), thickness=2, net_y=None):
    """Draw table edges + net + center line. corners: (4,2) TL, TR, BR, BL."""
    if corners is None or len(corners) != 4:
        return frame
    pts = np.int32(corners)
    # 4 edges (green)
    for i in range(4):
        cv2.line(frame, tuple(pts[i]), tuple(pts[(i + 1) % 4]), color, thickness, cv2.LINE_AA)
    # Corner dots (red)
    for p in pts:
        cv2.circle(frame, tuple(p), 4, (0, 0, 255), -1, cv2.LINE_AA)

    # Net line
    if net_y is not None:
        # Use detected net y-position — interpolate left and right x at that y
        # Left edge: TL(0) to BL(3), Right edge: TR(1) to BR(2)
        def _interp_x(p_top, p_bot, y):
            if abs(p_bot[1] - p_top[1]) < 1:
                return int(p_top[0])
            t = (y - p_top[1]) / (p_bot[1] - p_top[1])
            t = max(0, min(1, t))
            return int(p_top[0] + t * (p_bot[0] - p_top[0]))

        net_xl = _interp_x(pts[0], pts[3], net_y)
        net_xr = _interp_x(pts[1], pts[2], net_y)
        cv2.line(frame, (net_xl, net_y), (net_xr, net_y), (255, 255, 255), 2, cv2.LINE_AA)
    else:
        # Fallback: net at midpoint of left and right edges
        mid_L = ((pts[0][0] + pts[3][0]) // 2, (pts[0][1] + pts[3][1]) // 2)
        mid_R = ((pts[1][0] + pts[2][0]) // 2, (pts[1][1] + pts[2][1]) // 2)
        cv2.line(frame, mid_L, mid_R, (255, 255, 255), 1, cv2.LINE_AA)

    # Center line (white, thin) — midpoints of top and bottom edges
    mid_T = ((pts[0][0] + pts[1][0]) // 2, (pts[0][1] + pts[1][1]) // 2)
    mid_B = ((pts[2][0] + pts[3][0]) // 2, (pts[2][1] + pts[3][1]) // 2)
    cv2.line(frame, mid_T, mid_B, (255, 255, 255), 1, cv2.LINE_AA)
    return frame
