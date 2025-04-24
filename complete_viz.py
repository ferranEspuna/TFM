import itertools
import numpy as np
from typing import Tuple, Dict, List

# --- Adjustable parameters ---
LINE_THICKNESS = 1.5  # Thickness of hyperedge lines
DOT_THICKNESS = 4.0  # Thickness of the main vertex dots
ROOT_THICKNESS = 2.5  # Thickness of hyperedge root dots
VERTEX_COLOR = "black" # Color for all vertices

# --- Define your list of TikZ color names for hyperedges ---
# Customize with any valid TikZ color names/specifications.
# There are 4 hyperedges in K_4^(3).
tikz_edge_colors = ["magenta!70!white", "teal!70!white", "blue!70!white", "orange!70!white",] # Example list

# Check if the list is empty to avoid errors
if not tikz_edge_colors:
    raise ValueError("The tikz_edge_colors list cannot be empty.")
num_colors = len(tikz_edge_colors)

# --- Define the 4 vertices and their coordinates ---
# Example: corners of a square
vertices: Dict[str, Tuple[float, float]] = {
    'V1': (0, 5),
    'V2': (5, 5),
    'V3': (5, 0),
    'V4': (0, 0)
}
vertex_names = list(vertices.keys())

# Coefficients for calculating the root point (can be adjusted)
coefs_x = [1, 1, 1, -0.5]
coefs_y = [1, 1, 1, -0.5]

# --- Prepare TikZ code lines ---
lines = []

# Preamble and package imports
lines.append(r"% TikZ code for K_4^(3) using predefined edge colors")
lines.append(r"\begin{tikzpicture}[scale=1]")

# Define coordinates for the 4 vertices
for name, (x, y) in vertices.items():
    lines.append(r"\coordinate ({}) at ({}, {});".format(name, x, y))

# Calculate the overall center of the 4 vertices
all_coords = list(vertices.values())
center_all = (np.mean([p[0] for p in all_coords]), np.mean([p[1] for p in all_coords]))

# --- Draw hyperedges (trees) ---
# Iterate through all combinations of 3 vertices
hyperedges = list(itertools.combinations(vertex_names, 3))
total_hyperedges = len(hyperedges) # Should be 4

for edge_index, edge_nodes in enumerate(hyperedges):
    node1_name, node2_name, node3_name = edge_nodes
    node1_coord = vertices[node1_name]
    node2_coord = vertices[node2_name]
    node3_coord = vertices[node3_name]

    # Calculate the root point for this hyperedge
    root_x = 0
    points_x = [node1_coord[0], node2_coord[0], node3_coord[0], center_all[0]]
    valid_coefs_x = coefs_x[:len(points_x)]
    for coef, x in zip(valid_coefs_x, points_x):
        root_x += coef * x
    if sum(valid_coefs_x) != 0:
      root_x /= sum(valid_coefs_x)
    else: # Fallback
      root_x = (node1_coord[0] + node2_coord[0] + node3_coord[0])/3

    root_y = 0
    points_y = [node1_coord[1], node2_coord[1], node3_coord[1], center_all[1]]
    valid_coefs_y = coefs_y[:len(points_y)]
    for coef, y in zip(valid_coefs_y, points_y):
        root_y += coef * y
    if sum(valid_coefs_y) != 0:
      root_y /= sum(valid_coefs_y)
    else: # Fallback
      root_y = (node1_coord[1] + node2_coord[1] + node3_coord[1])/3

    # --- Select color name by cycling through the list ---
    current_color_name = tikz_edge_colors[edge_index % num_colors]

    # Create a coordinate for the hyperedge's root
    lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(edge_index, root_x, root_y))

    # --- Draw the tree edges using the TikZ color name ---
    lines.append(r"\draw[line width={}pt, color={}] (R{}) -- ({});".format(
        LINE_THICKNESS, current_color_name, edge_index, node1_name
    ))
    lines.append(r"\draw[line width={}pt, color={}] (R{}) -- ({});".format(
        LINE_THICKNESS, current_color_name, edge_index, node2_name
    ))
    lines.append(r"\draw[line width={}pt, color={}] (R{}) -- ({});".format(
        LINE_THICKNESS, current_color_name, edge_index, node3_name
    ))

    # --- Draw the hyperedge root dot using the TikZ color name ---
    lines.append(r"\fill[color={}] (R{}) circle ({}pt);".format(
        current_color_name, edge_index, ROOT_THICKNESS
    ))
    # Note: We no longer define edgecolor{edge_index}, so we use current_color_name


# --- Draw the main vertices on top ---
for name in vertex_names:
    lines.append(r"\fill[{}] ({}) circle ({}pt);".format(VERTEX_COLOR, name, DOT_THICKNESS))

lines.append(r"\end{tikzpicture}")

# --- Write TikZ code to a file ---
filename = "src/figures/k3_4.tex" # Updated filename
with open(filename, "w") as f:
    f.write("\n".join(lines))

print(f"TikZ code for K_4^(3) with predefined edge colors has been written to '{filename}'")