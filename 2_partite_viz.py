import numpy as np
from typing import Tuple, Dict, List

# --- Adjustable parameters ---
LINE_THICKNESS = 1.5  # Thickness of edge lines
DOT_THICKNESS = 4.0  # Thickness of the main vertex dots

DOT_COLORS = {
    "A": "black",  # Color of group A dots
    "B": "black",  # Color of group B dots
    "C": "black"  # Color of group C dots
}

BOX_BG_COLOR = "gray!20"  # Background color for group boxes

# --- Define your groups (Partitions V1, V2, V3 each size 2) ---
# Coordinates can be adjusted for better layout
group_A = [(2, 0), (0, 2)] # V1
group_B = [(8, 0), (10, 2)] # V2
group_C = [(2, 6), (8, 6)] # V3

# --- Prepare TikZ code lines ---
lines = []

# Preamble and package imports
lines.append(r"% TikZ code for K^(2)(2, 2, 2) using predefined edge colors")
lines.append(r"\begin{tikzpicture}[scale=0.8]")

# Define the margin value for bounding boxes
BOX_MARGIN = 0.7

# Function to compute bounding box
def bounding_box(points, margin=BOX_MARGIN):
    if not points:
        return (0, 0, 0, 0)
    x_vals, y_vals = zip(*points)
    return (
        min(x_vals) - margin, max(x_vals) + margin,  # X range
        min(y_vals) - margin, max(y_vals) + margin  # Y range
    )

# Draw background boxes and labels
for label, group, group_name in zip(["A", "B", "C"], [group_A, group_B, group_C], [r"$V_1$", r"$V_2$", r"$V_3$"]):
    x_min, x_max, y_min, y_max = bounding_box(group, margin=BOX_MARGIN)
    center_x, center_y = (x_min + x_max) / 2, (y_min + y_max) / 2
    # Draw box slightly behind text using TikZ layers
    lines.append(r"\begin{pgfonlayer}{background}")
    lines.append(
        r"  \draw[fill={}, rounded corners] ({:.2f}, {:.2f}) rectangle ({:.2f}, {:.2f});".format(BOX_BG_COLOR, x_min, y_min, x_max, y_max)
    )
    lines.append(r"\end{pgfonlayer}")
    # Position node in the center of the box
    lines.append(r"\node at ({:.2f}, {:.2f}) [align=center] {{{}}};".format(center_x, center_y, group_name))

# Define coordinates for points in each group
for idx, (x, y) in enumerate(group_A, start=1):
    lines.append(r"\coordinate (A{}) at ({}, {});".format(idx, x, y))
for idx, (x, y) in enumerate(group_B, start=1):
    lines.append(r"\coordinate (B{}) at ({}, {});".format(idx, x, y))
for idx, (x, y) in enumerate(group_C, start=1):
    lines.append(r"\coordinate (C{}) at ({}, {});".format(idx, x, y))



# Edges between A and B (4 edges)
for i in range(len(group_A)):
    for j in range(len(group_B)):
        current_color_name = 'magenta!70!white'  # Fixed color for edges between A and B
        lines.append(r"\draw[line width={}pt, color={}] (A{}) -- (B{});".format(
            LINE_THICKNESS, current_color_name, i + 1, j + 1
        ))

# Edges between A and C (4 edges)
for i in range(len(group_A)):
    for k in range(len(group_C)):
        current_color_name = 'teal!70!white'  # Fixed color for edges between A and C
        lines.append(r"\draw[line width={}pt, color={}] (A{}) -- (C{});".format(
            LINE_THICKNESS, current_color_name, i + 1, k + 1
        ))

# Edges between B and C (4 edges)
for j in range(len(group_B)):
    for k in range(len(group_C)):
        current_color_name = 'orange!70!white'  # Fixed color for edges between B and C
        lines.append(r"\draw[line width={}pt, color={}] (B{}) -- (C{});".format(
            LINE_THICKNESS, current_color_name, j + 1, k + 1
        ))

# --- Draw the vertices (points) on top ---
lines.append(r"\begin{pgfonlayer}{main}") # Default layer is main
for idx in range(1, len(group_A) + 1):
    lines.append(r"  \fill[{}] (A{}) circle ({}pt);".format(DOT_COLORS["A"], idx, DOT_THICKNESS))
for idx in range(1, len(group_B) + 1):
    lines.append(r"  \fill[{}] (B{}) circle ({}pt);".format(DOT_COLORS["B"], idx, DOT_THICKNESS))
for idx in range(1, len(group_C) + 1):
    lines.append(r"  \fill[{}] (C{}) circle ({}pt);".format(DOT_COLORS["C"], idx, DOT_THICKNESS))
lines.append(r"\end{pgfonlayer}")

# Declare layers (should be done early)
lines.insert(1, r"\pgfdeclarelayer{background}")
lines.insert(2, r"\pgfdeclarelayer{main}")
lines.insert(3, r"\pgfsetlayers{background,main}") # Set drawing order

lines.append(r"\end{tikzpicture}")

# --- Write TikZ code to a file ---
filename = "src/figures/k2_222.tex" # Updated filename
with open(filename, "w") as f:
    f.write("\n".join(lines))

print(f"TikZ code for K^(2)(2, 2, 2) with predefined edge colors has been written to '{filename}'")