import colorsys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colormaps

# --- Adjustable parameters ---
LINE_THICKNESS = 1.5  # Thickness of hyperedge lines
DOT_THICKNESS = 4.0  # Thickness of the main dots
ROOT_THICKNESS = 2.5  # Thickness of hyperedge root dots

DOT_COLORS = {
    "A": "black",  # Color of group A dots
    "B": "black",  # Color of group B dots
    "C": "black"  # Color of group C dots
}

BOX_BG_COLOR = "gray!20"  # Background color for group boxes

from typing import Tuple


def dim_rgb(color: Tuple[float, float, float], target_brightness: float) -> Tuple[float, float, float]:
    """
    Dim an RGB color (with values in range [0,1]) to a specified brightness level.

    Parameters:
        color (Tuple[float, float, float]): The original RGB color (values 0-1).
        target_brightness (float): The desired brightness level (0-1).

    Returns:
        Tuple[float, float, float]: The dimmed RGB color.
    """
    if not (0 <= target_brightness <= 1):
        raise ValueError("Brightness factor must be between 0 and 1.")

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(*color)

    # Adjust lightness to match target brightness
    new_rgb = colorsys.hls_to_rgb(h, min(l, target_brightness), s)

    return new_rgb


# --- Define your groups (adjust coordinates as needed) ---
group_A = [(2, 0), (0, 2)]
group_B = [(8, 0), (10, 2)]
group_C = [(2, 6), (8, 6)]

coefs_x = [1, 1, 1.25, -1]
# coefs_y = [1, 1, 1, -1]
coefs_y = [1, 1, 1.25, -1]

# Combine all points to compute the overall center
all_points = group_A + group_B + group_C
center_all = (np.mean([p[0] for p in all_points]), np.mean([p[1] for p in all_points]))

# --- Prepare TikZ code lines ---
lines = []

# Preamble and package imports
lines.append(r"\begin{tikzpicture}[scale=1]")


# Function to compute bounding box
def bounding_box(points, margin=0.5):
    x_vals, y_vals = zip(*points)
    return (
        min(x_vals) - margin, max(x_vals) + margin,  # X range
        min(y_vals) - margin, max(y_vals) + margin  # Y range
    )


for label, group, group_name in zip(["A", "B", "C"], [group_A, group_B, group_C], [r"$V_1$", r"$V_2$", r"$V_3$"]):
    x_min, x_max, y_min, y_max = bounding_box(group)
    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2  # Compute the center of the box
    lines.append(
        r"\draw[fill={}, rounded corners] ({}, {}) rectangle ({}, {});".format(BOX_BG_COLOR, x_min, y_min, x_max, y_max)
    )
    lines.append(r"\node at ({}, {}) [align=center] {{{}}};".format(center_x, center_y, group_name))

# Define coordinates for points in each group
for idx, (x, y) in enumerate(group_A, start=1):
    lines.append(r"\coordinate (A{}) at ({}, {});".format(idx, x, y))
for idx, (x, y) in enumerate(group_B, start=1):
    lines.append(r"\coordinate (B{}) at ({}, {});".format(idx, x, y))
for idx, (x, y) in enumerate(group_C, start=1):
    lines.append(r"\coordinate (C{}) at ({}, {});".format(idx, x, y))

# --- Draw hyperedges (trees) first so they appear behind the dots ---
total_hyperedges = len(group_A) * len(group_B) * len(group_C)
edge_index = 0
for i, a in enumerate(group_A):
    for j, b in enumerate(group_B):
        for k, c in enumerate(group_C):

            root_x = 0
            for coef, x in zip(coefs_x, [a[0], b[0], c[0], center_all[0]]):
                root_x += coef * x
            root_x /= sum(coefs_x)

            root_y = 0
            for coef, y in zip(coefs_y, [a[1], b[1], c[1], center_all[1]]):
                root_y += coef * y
            root_y /= sum(coefs_y)

            # Compute a color from the viridis colormap
            f = (edge_index) / (total_hyperedges)  # f in [0,1)
            # candidates = ['viridis', 'plasma', 'magma', Set2', 'prism']
            rgba = colormaps['prism'](f)
            r_val, g_val, b_val = rgba[:3]  # ignore alpha
            # Dim the color to a specified brightness level
            r_val, g_val, b_val = dim_rgb((r_val, g_val, b_val), 0.45)
            print(r_val, g_val, b_val)

            """c = plt.get_cmap('Dark2_r').colors[edge_index]
            r_val, g_val, b_val = c"""

            # Define a unique color using the rgb model
            lines.append(
                r"\definecolor{{edgecolor{}}}{{rgb}}{{{:.3f}, {:.3f}, {:.3f}}}".format(edge_index, r_val, g_val, b_val))

            # Create a coordinate for the hyperedge's root
            lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(edge_index, root_x, root_y))

            # Draw the tree edges with adjustable thickness
            lines.append(r"\draw[line width={}pt, color=edgecolor{}] (R{}) -- (A{});".format(LINE_THICKNESS, edge_index,
                                                                                             edge_index, i + 1))
            lines.append(r"\draw[line width={}pt, color=edgecolor{}] (R{}) -- (B{});".format(LINE_THICKNESS, edge_index,
                                                                                             edge_index, j + 1))
            lines.append(r"\draw[line width={}pt, color=edgecolor{}] (R{}) -- (C{});".format(LINE_THICKNESS, edge_index,
                                                                                             edge_index, k + 1))

            # Draw the hyperedge root dot
            lines.append(
                r"\fill[color=edgecolor{}] (R{}) circle ({}pt);".format(edge_index, edge_index, ROOT_THICKNESS))

            edge_index += 1

# --- Now draw the vertices (points) so they appear on top of the hyperedges ---
for idx in range(1, len(group_A) + 1):
    lines.append(r"\fill[{}] (A{}) circle ({}pt);".format(DOT_COLORS["A"], idx, DOT_THICKNESS))
for idx in range(1, len(group_B) + 1):
    lines.append(r"\fill[{}] (B{}) circle ({}pt);".format(DOT_COLORS["B"], idx, DOT_THICKNESS))
for idx in range(1, len(group_C) + 1):
    lines.append(r"\fill[{}] (C{}) circle ({}pt);".format(DOT_COLORS["C"], idx, DOT_THICKNESS))

lines.append(r"\end{tikzpicture}")

filename = "src/figures/222.tex"

# --- Write TikZ code to a file ---
with open(filename, "w") as f:
    f.write("\n".join(lines))

print(f"TikZ code has been written to '{filename}'")
