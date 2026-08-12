from __future__ import annotations

import math


def _area_to_radius(area_mm2):
    try:
        a = float(area_mm2)
    except Exception:
        return None
    return math.sqrt(a / math.pi) if a > 0 else None


def _circle_intersections(x0, y0, r0, x1, y1, r1):
    """Return the (up to 2) intersection points of two circles."""
    dx = x1 - x0
    dy = y1 - y0
    d = math.hypot(dx, dy)
    if d == 0 or d > (r0 + r1) or d < abs(r0 - r1):
        return []
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h_sq = r0 * r0 - a * a
    if h_sq < 0:
        return []
    h = math.sqrt(h_sq)
    xm = x0 + a * dx / d
    ym = y0 + a * dy / d
    rx = -dy * (h / d)
    ry = dx * (h / d)
    return [(xm + rx, ym + ry), (xm - rx, ym - ry)]


def _pack_circles_in_circle(n, r, R):
    """Pack n equal circles of radius r inside radius R using tangent candidates."""
    if not n or not r or not R or r <= 0 or R <= 0:
        return []
    if r > R:
        return []
    if n == 1:
        return [(0.0, 0.0)]

    placed = []
    spacing_options = [0.2, 0.0]
    angles = [i * (math.pi / 18.0) for i in range(36)]

    def fits(x, y, rr, spacing):
        if math.hypot(x, y) + rr > R:
            return False
        for ox, oy in placed:
            dx = x - ox
            dy = y - oy
            if (dx * dx + dy * dy) < (2 * rr + spacing) ** 2:
                return False
        return True

    placed.append((0.0, 0.0))
    while len(placed) < n:
        placed_flag = False
        for spacing in spacing_options:
            best = None
            best_score = None
            candidates = []

            for (ox, oy) in placed:
                base_dist = 2 * r + spacing
                for a in angles:
                    candidates.append((ox + base_dist * math.cos(a), oy + base_dist * math.sin(a)))

            for i in range(len(placed)):
                for j in range(i + 1, len(placed)):
                    (x1, y1) = placed[i]
                    (x2, y2) = placed[j]
                    d1 = 2 * r + spacing
                    d2 = 2 * r + spacing
                    candidates.extend(_circle_intersections(x1, y1, d1, x2, y2, d2))

            for (x, y) in candidates:
                if not fits(x, y, r, spacing):
                    continue
                score = x * x + y * y
                if best_score is None or score < best_score:
                    best_score = score
                    best = (x, y)

            if best is None:
                for ring in range(1, 12):
                    ring_r = ring * (r * 1.1)
                    if ring_r + r > R:
                        break
                    for a in angles:
                        x = ring_r * math.cos(a)
                        y = ring_r * math.sin(a)
                        if fits(x, y, r, spacing):
                            score = x * x + y * y
                            if best_score is None or score < best_score:
                                best_score = score
                                best = (x, y)
                    if best is not None:
                        break

            if best is not None:
                placed.append(best)
                placed_flag = True
                break

        if not placed_flag:
            break

    return placed


def _place_cables(cables, conduit_radius, angle_offset=0.0, angle_count=36, seed_mode="center"):
    """Greedy circle packing using tangent candidates (deterministic)."""
    placed = []
    unplaced = 0
    spacing_options = [0.5, 0.2, 0.0]  # progressively relax spacing if needed

    def fits(x, y, r, spacing):
        if (x * x + y * y) ** 0.5 + r > conduit_radius:
            return False
        for other in placed:
            dx = x - other["x"]
            dy = y - other["y"]
            min_sep = r + other["r"] + spacing
            if (dx * dx + dy * dy) < (min_sep * min_sep):
                return False
        return True


    # Place larger cables first to improve packing
    cables_sorted = sorted(cables, key=lambda c: (c.get("r") or 0.0), reverse=True)
    angles = [angle_offset + i * (math.pi / max(1.0, angle_count / 2.0)) for i in range(angle_count)]

    for cable in cables_sorted:
        r = cable.get("r")
        if r is None or r <= 0:
            unplaced += 1
            continue
        if r > conduit_radius:
            unplaced += 1
            continue
        if not placed:
            if seed_mode == "boundary":
                seed_r = max(0.0, conduit_radius - r)
                cable["x"], cable["y"] = seed_r * math.cos(angle_offset), seed_r * math.sin(angle_offset)
            else:
                cable["x"], cable["y"] = 0.0, 0.0
            placed.append(cable)
            continue

        placed_flag = False

        for spacing in spacing_options:
            best = None
            best_score = None
            current_max = 0.0
            for o in placed:
                current_max = max(current_max, math.hypot(o["x"], o["y"]) + o["r"])
            candidates = []

            # Tangent to one circle (angle sweep)
            for other in placed:
                base_dist = other["r"] + r + spacing
                for a in angles:
                    candidates.append(
                        (other["x"] + base_dist * math.cos(a), other["y"] + base_dist * math.sin(a))
                    )

            # Tangent to two circles (circle intersections)
            for i in range(len(placed)):
                for j in range(i + 1, len(placed)):
                    o1 = placed[i]
                    o2 = placed[j]
                    d1 = o1["r"] + r + spacing
                    d2 = o2["r"] + r + spacing
                    candidates.extend(
                        _circle_intersections(o1["x"], o1["y"], d1, o2["x"], o2["y"], d2)
                    )

            # Boundary candidates (tangent to conduit wall)
            boundary_r = conduit_radius - r
            if boundary_r > 0:
                for a in angles:
                    candidates.append((boundary_r * math.cos(a), boundary_r * math.sin(a)))

            # Rank candidates by distance to center
            for (x, y) in candidates:
                if not fits(x, y, r, spacing):
                    continue
                extent = math.hypot(x, y) + r
                max_extent = max(current_max, extent)
                score = (max_extent, extent, (x * x + y * y))
                if best_score is None or score < best_score:
                    best_score = score
                    best = (x, y)

            # Fallback: a few concentric rings
            if best is None:
                for ring in range(1, 16):
                    ring_r = ring * (r * 1.1)
                    if ring_r + r > conduit_radius:
                        break
                    for a in angles:
                        x = ring_r * math.cos(a)
                        y = ring_r * math.sin(a)
                        if fits(x, y, r, spacing):
                            extent = math.hypot(x, y) + r
                            max_extent = max(current_max, extent)
                            score = (max_extent, extent, (x * x + y * y))
                            if best_score is None or score < best_score:
                                best_score = score
                                best = (x, y)
                    if best is not None:
                        break

            if best is not None:
                cable["x"], cable["y"] = best[0], best[1]
                placed.append(cable)
                placed_flag = True
                break

        if not placed_flag:
            unplaced += 1

    return placed, unplaced


def _place_cables_allow_overlap(cables, conduit_radius):
    """Fallback placement that allows overlap (keeps all circles inside the conduit)."""
    placed = []
    for i, cable in enumerate(cables):
        r = cable.get("r")
        if r is None or r <= 0 or r > conduit_radius:
            continue
        if i == 0:
            cable["x"], cable["y"] = 0.0, 0.0
            placed.append(cable)
            continue
        # place along expanding spiral without collision checks
        angle = i * 0.7
        dist = min(conduit_radius - r, (0.7 * r) * math.sqrt(i))
        x = dist * math.cos(angle)
        y = dist * math.sin(angle)
        cable["x"], cable["y"] = x, y
        placed.append(cable)
    return placed
