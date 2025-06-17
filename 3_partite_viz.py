
import numpy as np
from typing import Tuple, List, Dict

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

# --- Define your list of TikZ color names for hyperedges ---
# Customize with any valid TikZ color names/specifications.
# The script will cycle through these colors for the 8 hyperedges in K(2,2,2).
# base_colors = ['blue', 'red', 'orange', 'teal', 'magenta', 'violet', 'brown', 'cyan']
base_colors = ['blue']
tikz_edge_colors = [f'{color}!70!white' if color != 'yellow' else color for color in base_colors]
# Check if the list is empty to avoid errors
if not tikz_edge_colors:
    raise ValueError("The tikz_edge_colors list cannot be empty.")
num_colors = len(tikz_edge_colors)


# --- Define your groups (adjust coordinates as needed) ---
group_A = [(2, 0), (0, 2)] # V1
group_B = [(8, 0), (10, 2)] # V2
group_C = [(2, 6), (8, 6)] # V3

# Coefficients for calculating the root point (can be adjusted)
coefs_x = [1, 1, 1.25, -1]
coefs_y = [1, 1, 1.25, -1]


# Combine all points to compute the overall center
all_points = group_A + group_B + group_C
center_all = (np.mean([p[0] for p in all_points]), np.mean([p[1] for p in all_points]))

# --- Prepare TikZ code lines ---
lines = []

# Preamble and package imports
lines.append(r"% TikZ code for K^(3)(2, 2, 2) using predefined edge colors")
lines.append(r"\begin{tikzpicture}[scale=1]")


# Function to compute bounding box
def bounding_box(points, margin=0.5):
    if not points:
        return (0,0,0,0)
    x_vals, y_vals = zip(*points)
    return (
        min(x_vals) - margin, max(x_vals) + margin,  # X range
        min(y_vals) - margin, max(y_vals) + margin  # Y range
    )

# Draw background boxes for groups
for label, group, group_name in zip(["A", "B", "C"], [group_A, group_B, group_C], [r"$V_1$", r"$V_2$", r"$V_3$"]):
    x_min, x_max, y_min, y_max = bounding_box(group)
    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2 # Compute the center of the box
    lines.append(
        r"\draw[fill={}, rounded corners] ({:.2f}, {:.2f}) rectangle ({:.2f}, {:.2f});".format(BOX_BG_COLOR, x_min, y_min, x_max, y_max)
    )
    lines.append(r"\node at ({:.2f}, {:.2f}) [align=center] {{{}}};".format(center_x, center_y, group_name))

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
for i, a_coord in enumerate(group_A):
    for j, b_coord in enumerate(group_B):
        for k, c_coord in enumerate(group_C):

            # Calculate root point
            root_x = 0
            points_x = [a_coord[0], b_coord[0], c_coord[0], center_all[0]]
            valid_coefs_x = coefs_x[:len(points_x)]
            for coef, x in zip(valid_coefs_x, points_x):
                root_x += coef * x
            if sum(valid_coefs_x) != 0:
                root_x /= sum(valid_coefs_x)
            else: # Fallback
                 root_x = (a_coord[0] + b_coord[0] + c_coord[0])/3

            root_y = 0
            points_y = [a_coord[1], b_coord[1], c_coord[1], center_all[1]]
            valid_coefs_y = coefs_y[:len(points_y)]
            for coef, y in zip(valid_coefs_y, points_y):
                root_y += coef * y
            if sum(valid_coefs_y) != 0:
                root_y /= sum(valid_coefs_y)
            else: # Fallback
                root_y = (a_coord[1] + b_coord[1] + c_coord[1])/3

            # --- Select color name by cycling through the list ---
            current_color_name = tikz_edge_colors[edge_index % num_colors]

            # Create a coordinate for the hyperedge's root
            lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(edge_index, root_x, root_y))

            # --- Draw the tree edges using the TikZ color name ---
            lines.append(r"\draw[line width={}pt, color={}] (R{}) -- (A{});".format(
                LINE_THICKNESS, current_color_name, edge_index, i + 1
            ))
            lines.append(r"\draw[line width={}pt, color={}] (R{}) -- (B{});".format(
                LINE_THICKNESS, current_color_name, edge_index, j + 1
            ))
            lines.append(r"\draw[line width={}pt, color={}] (R{}) -- (C{});".format(
                LINE_THICKNESS, current_color_name, edge_index, k + 1
            ))

            # --- Draw the hyperedge root dot using the TikZ color name ---
            lines.append(r"\fill[color={}] (R{}) circle ({}pt);".format(
                current_color_name, edge_index, ROOT_THICKNESS
            ))

            edge_index += 1

# --- Now draw the vertices (points) so they appear on top of the hyperedges ---
for idx in range(1, len(group_A) + 1):
    lines.append(r"\fill[{}] (A{}) circle ({}pt);".format(DOT_COLORS["A"], idx, DOT_THICKNESS))
for idx in range(1, len(group_B) + 1):
    lines.append(r"\fill[{}] (B{}) circle ({}pt);".format(DOT_COLORS["B"], idx, DOT_THICKNESS))
for idx in range(1, len(group_C) + 1):
    lines.append(r"\fill[{}] (C{}) circle ({}pt);".format(DOT_COLORS["C"], idx, DOT_THICKNESS))

lines.append(r"\end{tikzpicture}")

# --- Write TikZ code to a file ---
filename = "src/figures/k3_222.tex" # Changed filename
with open(filename, "w") as f:
    f.write("\n".join(lines))

print(f"TikZ code for K^(3)(2, 2, 2) with predefined edge colors has been written to '{filename}'")