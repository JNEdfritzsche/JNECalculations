from __future__ import annotations

import math

from calc_common.packing import (
    _area_to_radius,
    _pack_circles_in_circle,
    _place_cables,
    _place_cables_allow_overlap,
)

CF_PALETTE = ["#5B8FF9", "#61DDAA", "#F6BD16", "#E8684A", "#9270CA", "#6DC8EC", "#FF9D4D"]


def _build_cable_group_swatch_svg(area_per_cable, n_cond, area_per_conductor, group_idx):
    """Render a small SVG swatch showing this cable group's color and conductor layout."""
    r_cable = _area_to_radius(area_per_cable)
    if r_cable is None or r_cable <= 0:
        return None

    r_cond = _area_to_radius(area_per_conductor) if area_per_conductor else None

    canvas = 90
    margin = 6
    scale = (canvas - 2 * margin) / (2 * r_cable)
    cx = canvas / 2
    cy = canvas / 2

    def to_px(val_mm):
        return val_mm * scale

    color = CF_PALETTE[group_idx % len(CF_PALETTE)]

    svg_parts = []
    svg_parts.append(
        f'<svg width="{canvas}" height="{canvas}" viewBox="0 0 {canvas} {canvas}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{to_px(r_cable):.2f}" '
        f'stroke="#333" stroke-width="1" fill="{color}" fill-opacity="0.55"/>'
    )

    if n_cond:
        inner_margin = 0.6
        R_inner = r_cable - inner_margin
        if R_inner > 0:
            if r_cond is None or r_cond <= 0:
                r_cond_use = R_inner / max(1.6 * math.sqrt(int(n_cond)), 1.6)
            else:
                r_cond_use = min(r_cond, R_inner)

            conductor_positions = []
            for _ in range(15):
                conductor_positions = _pack_circles_in_circle(int(n_cond), r_cond_use, R_inner)
                if len(conductor_positions) >= int(n_cond):
                    break
                r_cond_use *= 0.9

            for (dx, dy) in conductor_positions[: int(n_cond)]:
                svg_parts.append(
                    f'<circle cx="{cx + to_px(dx):.2f}" cy="{cy + to_px(dy):.2f}" '
                    f'r="{to_px(r_cond_use):.2f}" stroke="#111" stroke-width="0.6" '
                    f'fill="#000000"/>'
                )

    svg_parts.append("</svg>")
    return "".join(svg_parts)


def _build_conduit_svg(conduit_radius, cables, overpacked=False):
    canvas = 360
    margin = 12
    scale = (canvas - 2 * margin) / (2 * conduit_radius) if conduit_radius else 1.0
    cx = canvas / 2
    cy = canvas / 2

    def to_px(val_mm):
        return val_mm * scale

    svg_parts = []
    svg_parts.append(
        f'<svg width="{canvas}" height="{canvas}" viewBox="0 0 {canvas} {canvas}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    )
    svg_parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{to_px(conduit_radius):.2f}" '
        f'stroke="#222" stroke-width="2" fill="#f8f8f8"/>'
    )

    for cable in cables:
        x = cable.get("x")
        y = cable.get("y")
        r = cable.get("r")
        if x is None or y is None or r is None:
            continue
        color = CF_PALETTE[cable.get("group_idx", 0) % len(CF_PALETTE)]
        svg_parts.append(
            f'<circle cx="{cx + to_px(x):.2f}" cy="{cy + to_px(y):.2f}" r="{to_px(r):.2f}" '
            f'stroke="#333" stroke-width="1" fill="{color}" fill-opacity="0.55"/>'
        )

        n_cond = cable.get("n_cond")
        r_cond = cable.get("r_cond")
        if n_cond:
            margin = 0.6
            R_inner = r - margin
            if R_inner > 0:
                if r_cond is None or r_cond <= 0:
                    r_cond_use = R_inner / max(1.6 * math.sqrt(int(n_cond)), 1.6)
                else:
                    r_cond_use = min(r_cond, R_inner)

                # Shrink conductors if they don't fit
                conductor_positions = []
                for _ in range(15):
                    conductor_positions = _pack_circles_in_circle(int(n_cond), r_cond_use, R_inner)
                    if len(conductor_positions) >= int(n_cond):
                        break
                    r_cond_use *= 0.9

                for (dx, dy) in conductor_positions[: int(n_cond)]:
                    svg_parts.append(
                        f'<circle cx="{cx + to_px(x + dx):.2f}" cy="{cy + to_px(y + dy):.2f}" '
                        f'r="{to_px(r_cond_use):.2f}" stroke="#111" stroke-width="0.6" '
                        f'fill="#000000"/>'
                    )

    if overpacked:
        # Diagonal red hatch clipped to conduit circle
        svg_parts.append(
            f'<defs><clipPath id="conduitClip"><circle cx="{cx}" cy="{cy}" '
            f'r="{to_px(conduit_radius):.2f}"/></clipPath></defs>'
        )
        svg_parts.append(f'<g clip-path="url(#conduitClip)" opacity="0.35">')
        step = 14
        for x in range(-canvas, canvas * 2, step):
            x1 = x
            y1 = -canvas
            x2 = x + canvas
            y2 = canvas
            svg_parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="#cc0000" stroke-width="6"/>'
            )
        svg_parts.append("</g>")

    svg_parts.append("</svg>")
    return "".join(svg_parts)


def cable_instances(result):
    instances = []
    for group_idx, group in enumerate(result.get("groups") or []):
        area_per_cable = group.get("area_each_mm2")
        n_cond = int(group.get("conductors_per_cable") or 1)
        area_per_conductor = area_per_cable / n_cond if (area_per_cable and n_cond) else None

        r_cable = _area_to_radius(area_per_cable) if area_per_cable else None
        r_cond = _area_to_radius(area_per_conductor) if area_per_conductor else None

        for _ in range(int(group.get("qty") or 0)):
            instances.append({"r": r_cable, "n_cond": n_cond, "r_cond": r_cond, "group_idx": group_idx})
    return instances


def build_cross_section_svg(result):
    conduit_radius = _area_to_radius(result.get("internal_area_mm2"))
    if not conduit_radius:
        return None

    cables = cable_instances(result)
    if not cables:
        return None

    placed, unplaced = _place_cables(cables, conduit_radius)

    if unplaced > 0:
        best_placed, best_unplaced, best_extent = placed, unplaced, None
        for mode in ("center", "boundary"):
            for offset in (0.0, math.pi / 36.0, math.pi / 18.0, math.pi / 12.0, math.pi / 9.0):
                p2, u2 = _place_cables(cables, conduit_radius, angle_offset=offset,
                                       angle_count=48, seed_mode=mode)
                if u2 == 0:
                    extent = max((math.hypot(c["x"], c["y"]) + c["r"] for c in p2), default=0.0)
                    if best_extent is None or extent < best_extent:
                        best_extent, best_placed, best_unplaced = extent, p2, u2
                elif u2 < best_unplaced:
                    best_unplaced, best_placed = u2, p2
        placed, unplaced = best_placed, best_unplaced

    allowed = result.get("allowed_area_mm2")
    total = result.get("total_cable_area_mm2")
    overpacked = allowed is not None and total is not None and total > allowed + 1e-9

    if unplaced > 0 and overpacked:
        placed = _place_cables_allow_overlap(cables, conduit_radius)

    return _build_conduit_svg(conduit_radius, placed, overpacked=overpacked)


def group_swatch_svg(group, group_idx):
    area_per_cable = group.get("area_each_mm2")
    n_cond = int(group.get("conductors_per_cable") or 1)
    area_per_conductor = area_per_cable / n_cond if (area_per_cable and n_cond) else None
    return _build_cable_group_swatch_svg(area_per_cable, n_cond, area_per_conductor, group_idx)
