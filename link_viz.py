import itertools
import os

# --- Adjustable parameters ---

# Vertex styling
T_DOT_COLOR = "blue"
V_MINUS_T_DOT_COLOR = "black"
DOT_THICKNESS = 4.0
ADD_VERTEX_LABELS = True

# Link edge styling (Common Link Graph Edges Y)
LINK_EDGE_COLORS = ["magenta", "teal", "blue", "cyan", "violet", "teal", "red"]
LINK_EDGE_THICKNESS = "very thick"  # Make link edges stand out

# Contributing Hyperedge styling (Edges X u Y, |X|=1, Y is a link edge)
CONTRIBUTING_HYPEREDGE_BRIGHTNESS_FACTOR = 50  # TikZ factor (e.g., 70 = color!70!black)
CONTRIBUTING_HYPEREDGE_LINE_THICKNESS = 1.0
CONTRIBUTING_HYPEREDGE_ROOT_THICKNESS = 2.5
CONTRIBUTING_HYPEREDGE_STYLE = "solid"  # Style for lines from root

# Non-Contributing Hyperedge styling (Involving T, |H n T| != k-j)
# Specifically for |H n T| > k-j as requested (dimmer, dotted)
OTHER_T_HYPEREDGE_COLOR = "gray"
OTHER_T_HYPEREDGE_BRIGHTNESS_FACTOR = 50  # Dimmer gray: gray!40!black
OTHER_T_HYPEREDGE_LINE_THICKNESS = 1.5
OTHER_T_HYPEREDGE_ROOT_THICKNESS = 2.5
OTHER_T_HYPEREDGE_STYLE = "solid"  # Dotted style for these

# "Almost" Link Edge styling (Y connected to *some* but not *all* X in T)
ALMOST_LINK_EDGE_COLOR = "gray"
ALMOST_LINK_EDGE_THICKNESS = "thin"
ALMOST_LINK_EDGE_STYLE = "dashed"

# General Hyperedge Settings
DRAW_ORIGINAL_HYPEREDGES = True  # Master switch

# Box styling
T_BOX_BG_COLOR = "blue!10"
V_MINUS_T_BOX_BG_COLOR = "gray!10"
BOX_MARGIN = 0.7
DRAW_BOXES = True

# --- Utility Functions ---
# No changes needed for dim_rgb, but we'll use TikZ dimming instead for simplicity

# --- Define the graph G = (V, E) and set T ---

vertices = {
    'A': (0, 2), 'B': (0, 7),
    'X': (8, 9), 'Y': (10, 6),
    'Z': (8, 0), 'W': (10, 3)  # Changed T to W for clarity
}

T = ['A', 'B']
V_minus_T = [v for v in vertices if v not in T]

# Define the hyperedges E of the 3-uniform graph G
# Using frozenset for easier comparison
hyperedges_G_list = [('A', 'X', 'Y'),  # Hyperedge 1
                     ('A', 'Y', 'T'),  # Hyperedge 2
                     ('B', 'X', 'Y'),  # Hyperedge 3
                     ('B', 'Y', 'W'),  # Hyperedge 4
                     ('A', 'Z', 'W'),  # Hyperedge 5
                     ('B', 'Z', 'W'),  # Hyperedge 6
                     ('A', 'B', 'X'),  # Hyperedge 7
                     ('A', 'Y', 'W'),
                     ('B', 'Y', 'Z'),
                     ]
hyperedges_G_set = {frozenset(h) for h in hyperedges_G_list}
# Add original list indices for reference
hyperedges_G_indexed = {frozenset(h): idx for idx, h in enumerate(hyperedges_G_list)}

k = 3
j = 2
required_X_size = k - j  # Should be 1 in this example

# --- Calculate Link Edges, Contributing Hyperedges, and Almost Links ---

link_edges_data = {}  # Stores { frozenset(Y): {"color": color, "contributors": [hedge_id1, hedge_id2]} }
almost_link_edges = []  # Stores frozenset(Y) for almost links
potential_Y_sets = list(itertools.combinations(V_minus_T, j))
T_combinations = list(itertools.combinations(T, required_X_size))
num_required_X = len(T_combinations)

link_color_index = 0

for Y_tuple in potential_Y_sets:
    Y = frozenset(Y_tuple)
    contributing_hyperedges_ids = []
    found_X_count = 0

    for X_tuple in T_combinations:
        X = frozenset(X_tuple)
        hyperedge_candidate = X.union(Y)
        if hyperedge_candidate in hyperedges_G_set:
            found_X_count += 1
            contributing_hyperedges_ids.append(hyperedges_G_indexed[hyperedge_candidate])

    if found_X_count == num_required_X:
        # This is a confirmed link edge Y
        color = LINK_EDGE_COLORS[link_color_index % len(LINK_EDGE_COLORS)]
        link_edges_data[Y] = {
            "color": color,
            "contributors": contributing_hyperedges_ids,
            "nodes": Y_tuple  # Keep tuple for drawing order
        }
        link_color_index += 1
    elif 0 < found_X_count < num_required_X:
        # This is an "almost" link edge Y
        almost_link_edges.append(Y_tuple)

# --- Prepare data for drawing original hyperedges ---
hyperedge_drawing_data = []
if DRAW_ORIGINAL_HYPEREDGES:
    for idx, hedge_nodes_tuple in enumerate(hyperedges_G_list):
        hedge_nodes = frozenset(hedge_nodes_tuple)
        v_labels = list(hedge_nodes_tuple)  # Keep original order for consistency if needed
        coords = [vertices[v] for v in v_labels if v in vertices]
        if len(coords) != k:
            print(f"Warning: Skipping hyperedge {hedge_nodes_tuple} due to missing vertex coordinates.")
            continue

        root_x = sum(c[0] for c in coords) / k
        root_y = sum(c[1] for c in coords) / k

        # Determine category and style
        intersect_T = hedge_nodes.intersection(T)
        intersect_T_size = len(intersect_T)
        Y_part = hedge_nodes.difference(T)

        style_info = {}
        is_contributor = False

        if intersect_T_size == required_X_size:
            # Potential contributor? Check if Y_part is a confirmed link edge
            if Y_part in link_edges_data and idx in link_edges_data[Y_part]["contributors"]:
                # Yes, it's a contributor
                link_color = link_edges_data[Y_part]["color"]
                style_info = {
                    "category": "contributor",
                    "color": f"{link_color}!{CONTRIBUTING_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                    "line_thickness": CONTRIBUTING_HYPEREDGE_LINE_THICKNESS,
                    "root_thickness": CONTRIBUTING_HYPEREDGE_ROOT_THICKNESS,
                    "line_style": CONTRIBUTING_HYPEREDGE_STYLE
                }
                is_contributor = True

        if not is_contributor:
            # Check if it's the other type requested (|H n T| > k-j)
            if intersect_T_size > required_X_size:
                style_info = {
                    "category": "other_T",
                    "color": f"{OTHER_T_HYPEREDGE_COLOR}!{OTHER_T_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                    "line_thickness": OTHER_T_HYPEREDGE_LINE_THICKNESS,
                    "root_thickness": OTHER_T_HYPEREDGE_ROOT_THICKNESS,
                    "line_style": OTHER_T_HYPEREDGE_STYLE
                }
            else:
                style_info = {
                    "category": "other_generic",  # Or could reuse "other_T" if style is identical
                    "color": f"{OTHER_T_HYPEREDGE_COLOR}!{OTHER_T_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                    "line_thickness": OTHER_T_HYPEREDGE_LINE_THICKNESS,
                    "root_thickness": OTHER_T_HYPEREDGE_ROOT_THICKNESS,
                    "line_style": OTHER_T_HYPEREDGE_STYLE  # Using dotted as requested for non-contributing involving T
                }

        hyperedge_drawing_data.append({
            "id": idx,
            "nodes": v_labels,  # Use original tuple order
            "root": (root_x, root_y),
            "style": style_info
        })

# --- Prepare TikZ code lines ---
lines = [r"% TikZ code generated by Python script for Common Link Graph visualization",
         r"\begin{tikzpicture}[scale=0.8]", r"% Vertex coordinates"]

# Define needed colors explicitly if not standard TikZ names (optional here as we use named colors + dimming)
# Example: \definecolor{brightpink}{rgb}{1.0, 0.0, 0.5}

# -- 2. Define Coordinates for Vertices AND Hyperedge Roots --
for label, (x, y) in vertices.items():
    lines.append(r"\coordinate ({}) at ({:.2f}, {:.2f});".format(label, x, y))

if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Hyperedge root coordinates")
    for data in hyperedge_drawing_data:
        rx, ry = data['root']
        lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(data['id'], rx, ry))


# Function to compute bounding box (needed for boxes)
def bounding_box(points_coords, margin=0.5):
    if not points_coords:
        return 0, 0, 0, 0
    x_vals, y_vals = zip(*points_coords)
    return min(x_vals) - margin, max(x_vals) + margin, min(y_vals) - margin, max(y_vals) + margin


# -- 3. Draw Boxes (Optional) --
if DRAW_BOXES:
    lines.append(r"% Draw background boxes for T and V \ T")
    t_points_coords = [vertices[v] for v in T if v in vertices]
    if t_points_coords:
        x_min, x_max, y_min, y_max = bounding_box(t_points_coords, BOX_MARGIN)
        lines.append(
            r"\draw[fill={}, rounded corners, line width=0.5pt, draw=gray!50] "
            r"({:.2f}, {:.2f}) rectangle ({:.2f}, {:.2f});".format(
                T_BOX_BG_COLOR, x_min, y_min, x_max, y_max))
        lines.append(r"\node at ({:.2f}, {:.2f}) "
                     r"[anchor=south east, inner sep=1pt, text=gray] {{$T$}};".format(x_max, y_max))

    v_minus_t_coords = [vertices[v] for v in V_minus_T if v in vertices]
    if v_minus_t_coords:
        x_min, x_max, y_min, y_max = bounding_box(v_minus_t_coords, BOX_MARGIN)
        lines.append(r"\draw[fill={}, rounded corners,"
                     r" line width=0.5pt, draw=gray!50] ({:.2f}, {:.2f}) rectangle ({"
                     r":.2f}, {:.2f});".format(V_MINUS_T_BOX_BG_COLOR, x_min, y_min, x_max, y_max))
        lines.append(
            r"\node at ({:.2f}, {:.2f}) [anchor=south east, inner sep=1pt, text=gray] {{$V \setminus T$}};".format(
                x_max, y_max))  # Adjusted position

# -- 4. Draw Original Hyperedges --
if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Draw original hyperedges (styled by category)")
    for data in hyperedge_drawing_data:
        style = data['style']
        edge_id = data['id']
        root_coord = f"R{edge_id}"
        line_options = f"line width={style['line_thickness']:.1f}pt, color={style['color']}, {style['line_style']}"

        # Draw the tree edges from root to nodes
        for node_label in data['nodes']:
            lines.append(r"\draw[{}] ({}) -- ({});".format(line_options, root_coord, node_label))

        # Draw the hyperedge root dot
        lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(style['color'], root_coord, style['root_thickness']))

# -- 5. Draw "Almost" Link Edges --
if almost_link_edges:
    lines.append(r"% Draw 'almost' link edges (faintly, dotted)")
    almost_style = f"color={ALMOST_LINK_EDGE_COLOR}, {ALMOST_LINK_EDGE_THICKNESS}, {ALMOST_LINK_EDGE_STYLE}"
    for u, v in almost_link_edges:  # Assuming j=2
        if u in vertices and v in vertices:
            lines.append(r"\draw[{}] ({}) -- ({});".format(almost_style, u, v))
        else:
            print(f"Warning: Could not draw almost link edge between {u} and {v} - missing vertex.")

# -- 6. Draw Confirmed Link Edges --
if link_edges_data:
    lines.append(r"% Edges of the common {}-link graph of T (brightly colored)".format(j))
    for Y_fset, data in link_edges_data.items():
        u, v = data['nodes']  # Assumes j=2
        color = data['color']
        style = f"{LINK_EDGE_THICKNESS}, color={color}"
        if u in vertices and v in vertices:
            lines.append(r"\draw[{}] ({}) -- ({});".format(style, u, v))
        else:
            print(f"Warning: Could not draw link edge between {u} and {v} - missing vertex.")

# -- 7. Draw Vertices (Foreground) --
lines.append(r"% Draw vertices (foreground layer)")
# Vertices in T
for v_label in T:
    if v_label in vertices:
        lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(T_DOT_COLOR, v_label, DOT_THICKNESS))
        if ADD_VERTEX_LABELS:
            lines.append(r"\node[above right=1pt, color={}] at ({}) {{${}$}};".format(T_DOT_COLOR, v_label, v_label))
# Vertices in V \ T
for v_label in V_minus_T:
    if v_label in vertices:
        lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(V_MINUS_T_DOT_COLOR, v_label, DOT_THICKNESS))
        if ADD_VERTEX_LABELS:
            lines.append(
                r"\node[above right=1pt, color={}] at ({}) {{${}$}};".format(V_MINUS_T_DOT_COLOR, v_label, v_label))

lines.append(r"\end{tikzpicture}")

# --- Write TikZ code to a file ---
filename = "common_link.tex"
output_dir = "src/figures"  # Define output directory (optional)

# Ensure the output directory exists
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
else:
    full_path = filename

# Write the TikZ code to the file
try:
    with open(full_path, "w") as f:
        f.write("\n".join(lines))
    print(f"\nDetailed TikZ code for the common link graph has been written to '{full_path}'")
    print(f" - T: {T}")
    print(f" - Confirmed {j}-link edges found: {len(link_edges_data)}")
    for Y_fset, data in link_edges_data.items():
        print(f"   - {set(Y_fset)}: color={data['color']}")
    print(f" - 'Almost' {j}-link edges found: {len(almost_link_edges)}")
    for Y_tuple in almost_link_edges:
        print(f"   - {set(Y_tuple)}")
    print(f" - Original hyperedges styled by contribution:")
    print(f"   - Contributing: Dimmed version of link color, style '{CONTRIBUTING_HYPEREDGE_STYLE}'")
    print(f"   - Involving |T|>1: Color '{OTHER_T_HYPEREDGE_COLOR}' (dimmed), style '{OTHER_T_HYPEREDGE_STYLE}'")
    print(f"   - Others involving T: Styled similarly to |T|>1 case.")
except IOError as e:
    print(f"Error writing file '{full_path}': {e}")
