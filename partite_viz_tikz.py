import numpy as np
import matplotlib.cm as cm

# --- Define your groups (adjust coordinates as needed) ---
group_A = [(2, 0), (0, 2)]
group_B = [(8, 0), (10, 2)]
group_C = [(2, 8), (8, 8)]

# Combine all points to compute the overall center
all_points = group_A + group_B + group_C
center_all = (np.mean([p[0] for p in all_points]), np.mean([p[1] for p in all_points]))

# --- Prepare TikZ code lines ---
lines = []

# Preamble and package imports
lines.append(r"\documentclass[tikz]{standalone}")
lines.append(r"\usepackage{xcolor}")
lines.append(r"\begin{document}")
lines.append(r"\begin{tikzpicture}[scale=1]")

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
            # Compute the tree's root as in your original code
            root_x = (a[0] + b[0] + c[0] - center_all[0]) / 2
            root_y = (a[1] + b[1] + c[1] - center_all[1]) / 2

            # Compute a color from the viridis colormap
            f = edge_index / total_hyperedges  # f in [0,1)
            rgba = cm.viridis(f)
            r_val, g_val, b_val = rgba[:3]  # ignore alpha

            # Define a unique color using the rgb model
            lines.append(
                r"\definecolor{{edgecolor{}}}{{rgb}}{{{:.3f}, {:.3f}, {:.3f}}}".format(edge_index, r_val, g_val, b_val))

            # Create a coordinate for the hyperedge's root
            lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(edge_index, root_x, root_y))

            # Draw the tree edges (with a thinner line width)
            lines.append(
                r"\draw[line width=0.5pt, color=edgecolor{}] (R{}) -- (A{});".format(edge_index, edge_index, i + 1))
            lines.append(
                r"\draw[line width=0.5pt, color=edgecolor{}] (R{}) -- (B{});".format(edge_index, edge_index, j + 1))
            lines.append(
                r"\draw[line width=0.5pt, color=edgecolor{}] (R{}) -- (C{});".format(edge_index, edge_index, k + 1))

            # Optionally, mark the root with a small dot
            lines.append(r"\fill[color=edgecolor{}] (R{}) circle (1.5pt);".format(edge_index, edge_index))

            edge_index += 1

# --- Now draw the vertices (points) so they appear on top of the hyperedges ---
for idx in range(1, len(group_A) + 1):
    lines.append(r"\fill[blue] (A{}) circle (2pt);".format(idx))
for idx in range(1, len(group_B) + 1):
    lines.append(r"\fill[red] (B{}) circle (2pt);".format(idx))
for idx in range(1, len(group_C) + 1):
    lines.append(r"\fill[green] (C{}) circle (2pt);".format(idx))

lines.append(r"\end{tikzpicture}")
lines.append(r"\end{document}")

filename = "src/figures/222.tex"

# --- Write TikZ code to a file ---
with open(filename, "w") as f:
    f.write("\n".join(lines))

print(f"TikZ code has been written to '{filename}'")
