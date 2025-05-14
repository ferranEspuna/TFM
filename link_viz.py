import itertools
import os
import math  # For ceiling function

# --- Adjustable parameters ---

# Vertex styling
T_DOT_COLOR = "black"
V_MINUS_T_DOT_COLOR = "black"
DOT_THICKNESS = 4.0
ADD_VERTEX_LABELS = True

# Link edge styling (Common Link Graph Edges Y - TRUE links)
LINK_EDGE_COLORS = ["magenta", "teal", "blue", "orange",]
LINK_EDGE_THICKNESS = "very thick"
LINK_EDGE_STYLE = "solid"  # True link edges are solid

# Contributing Hyperedge styling (Edges X u Y, where Y is a TRUE link edge)
CONTRIBUTING_HYPEREDGE_BRIGHTNESS_FACTOR = 60  # TikZ factor (e.g., 70 = color!70!white)
CONTRIBUTING_HYPEREDGE_LINE_THICKNESS = 1.0
CONTRIBUTING_HYPEREDGE_ROOT_THICKNESS = 2.5
CONTRIBUTING_HYPEREDGE_STYLE = "solid"  # Contributors to TRUE links are solid

# "Almost" Link Edge styling (Y connected to *some* but not *all* X in T)
# Uses the LINK_EDGE_COLORS pool after the true links
ALMOST_LINK_EDGE_THICKNESS = "very thick"
ALMOST_LINK_EDGE_STYLE = "dashed"  # Almost link edges are dashed

# Contributing Hyperedge styling (Edges X u Y, where Y is an ALMOST link edge)
ALMOST_CONTRIB_HYPEREDGE_BRIGHTNESS_FACTOR = 60  # Slightly more faded
ALMOST_CONTRIB_HYPEREDGE_LINE_THICKNESS = 1.0
ALMOST_CONTRIB_HYPEREDGE_ROOT_THICKNESS = 2.5
ALMOST_CONTRIB_HYPEREDGE_STYLE = "solid"  # Contributors to ALMOST links are dashed

# Invalid T-Intersection Hyperedge styling (|H n T| > k-j)
INVALID_T_INTERSECT_HYPEREDGE_COLOR = "gray"
INVALID_T_INTERSECT_HYPEREDGE_BRIGHTNESS_FACTOR = 80  # Dim gray
INVALID_T_INTERSECT_HYPEREDGE_LINE_THICKNESS = 1.0
INVALID_T_INTERSECT_HYPEREDGE_ROOT_THICKNESS = 2.5
INVALID_T_INTERSECT_HYPEREDGE_STYLE = "solid"  # Dashed style for these

# Other/Generic Hyperedge styling (Not contributing, |H n T| <= k-j)
OTHER_GENERIC_HYPEREDGE_COLOR = "gray"
OTHER_GENERIC_HYPEREDGE_BRIGHTNESS_FACTOR = 80  # Even dimmer gray
OTHER_GENERIC_HYPEREDGE_LINE_THICKNESS = 0.8  # Thinner
OTHER_GENERIC_HYPEREDGE_ROOT_THICKNESS = 2.0
OTHER_GENERIC_HYPEREDGE_STYLE = "solid"  # Solid for these? Or dashed? Let's keep solid for now.

# General Hyperedge Settings
DRAW_ORIGINAL_HYPEREDGES = True  # Master switch

# Box styling
T_BOX_BG_COLOR = "gray!20"
V_MINUS_T_BOX_BG_COLOR = "gray!20"
BOX_MARGIN = 0.8
DRAW_BOXES = True

# *** NEW: Overall Frame Styling ***
ADD_OVERALL_FRAME = True  # Master switch to add the frame
FRAME_MARGIN = 1.0  # Margin around the picture contents (in TikZ units)
FRAME_COLOR = "black!80"  # Color of the frame
FRAME_THICKNESS = "thin"  # TikZ style: thin, thick, line width=1pt, etc.
FRAME_LABEL = "G"  # The label text (use $G$ for math italics)
# Position relative to bounding box: south, north, north west, etc.
FRAME_LABEL_POSITION = "north"
# TikZ node options for the label (positioning, font, etc.)
FRAME_LABEL_OPTIONS = "anchor=north, yshift=-5pt, font=\\Large"

# --- Define the graph G = (V, E) and set T ---

vertices = {
    'A': (0, 1.6), 'B': (0, 5.6), 'C': (1.2, 3.6),
    'X': (9, 7.2), 'Y': (11, 4.8),
    'Z': (9, 0.0), 'W': (11, 2.4)
}

vertex_label_position = {
    'A': 'left',
    'B': 'left',
    'C': 'above',
    'X': 'right',
    'Y': 'right',
    'Z': 'right',
    'W': 'right'
}

T = ['A', 'B', 'C']
V_minus_T = [v for v in vertices if v not in T]

# Define the hyperedges E of the 3-uniform graph G
hyperedges_G_list = [('A', 'X', 'Y'),
                     ('B', 'X', 'Y'),
                     ('B', 'Y', 'W'),
                     ('A', 'Z', 'W'),
                     ('B', 'Z', 'W'),
                     ('A', 'B', 'X'),
                     ('A', 'Y', 'W'),
                     ('B', 'Y', 'Z'),
                     ('A', 'B', 'C'),
                     ('C', 'X', 'Y'),
                     ('C', 'Z', 'W'),
                     ('X', 'Z', 'W'),
                     ]

hyperedges_G_set = {frozenset(h) for h in hyperedges_G_list}
hyperedges_G_indexed = {frozenset(h): idx for idx, h in enumerate(hyperedges_G_list)}

k = 3
j = 2
required_X_size = k - j  # Should be 1

# --- Calculate Link Edges, Almost Links, and Categorize Hyperedges ---

link_edges_data = {}  # Stores { frozenset(Y): {"color": color, "contributors": [hedge_id1,...], "nodes": tuple(Y)} }
almost_link_edges_data = {}  # Stores { frozenset(Y): {"color": color, "contributors": [hedge_id1,...], "nodes": tuple(Y)} }

potential_Y_sets = list(itertools.combinations(V_minus_T, j))
T_combinations = list(itertools.combinations(T, required_X_size))
num_required_X = len(T_combinations)

link_color_index = 0
almost_link_color_start_index = 0  # We'll determine this after finding true links

# Find True Link Edges first
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
            "nodes": Y_tuple
        }
        link_color_index += 1

# Now find Almost Link Edges (and assign colors from the remaining pool)
almost_link_color_start_index = link_color_index
almost_link_color_index = almost_link_color_start_index

for Y_tuple in potential_Y_sets:
    Y = frozenset(Y_tuple)
    if Y in link_edges_data:  # Skip if it's already a true link
        continue

    contributing_hyperedges_ids = []
    found_X_count = 0
    for X_tuple in T_combinations:
        X = frozenset(X_tuple)
        hyperedge_candidate = X.union(Y)
        if hyperedge_candidate in hyperedges_G_set:
            found_X_count += 1
            contributing_hyperedges_ids.append(hyperedges_G_indexed[hyperedge_candidate])

    if 0 < found_X_count < num_required_X:
        # This is an "almost" link edge Y
        color = LINK_EDGE_COLORS[almost_link_color_index % len(LINK_EDGE_COLORS)]
        almost_link_edges_data[Y] = {
            "color": color,
            "contributors": contributing_hyperedges_ids,
            "nodes": Y_tuple
        }
        almost_link_color_index += 1

# --- Prepare data for drawing original hyperedges ---
hyperedge_drawing_data = []
if DRAW_ORIGINAL_HYPEREDGES:
    for idx, hedge_nodes_tuple in enumerate(hyperedges_G_list):
        hedge_nodes = frozenset(hedge_nodes_tuple)
        v_labels = list(hedge_nodes_tuple)
        coords = [vertices[v] for v in v_labels if v in vertices]
        if len(coords) != k:
            print(f"Warning: Skipping hyperedge {hedge_nodes_tuple} due to missing vertex coords.")
            continue

        root_x = sum(c[0] for c in coords) / k
        root_y = sum(c[1] for c in coords) / k

        # Determine category and style
        intersect_T = hedge_nodes.intersection(T)
        intersect_T_size = len(intersect_T)
        Y_part = hedge_nodes.difference(T)  # Potential Y component

        style_info = {}
        category = "other_generic"  # Default category

        # Priority 1: True Contributors
        is_contributor = False
        if intersect_T_size == required_X_size and Y_part in link_edges_data:
            if idx in link_edges_data[Y_part]["contributors"]:
                link_color = link_edges_data[Y_part]["color"]
                style_info = {
                    "color": f"{link_color}!{CONTRIBUTING_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                    "line_thickness": CONTRIBUTING_HYPEREDGE_LINE_THICKNESS,
                    "root_thickness": CONTRIBUTING_HYPEREDGE_ROOT_THICKNESS,
                    "line_style": CONTRIBUTING_HYPEREDGE_STYLE
                }
                category = "true_contributor"
                is_contributor = True

        # Priority 2: Almost Contributors
        if not is_contributor and intersect_T_size == required_X_size and Y_part in almost_link_edges_data:
            if idx in almost_link_edges_data[Y_part]["contributors"]:
                almost_link_color = almost_link_edges_data[Y_part]["color"]
                style_info = {
                    "color": f"{almost_link_color}!{ALMOST_CONTRIB_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                    "line_thickness": ALMOST_CONTRIB_HYPEREDGE_LINE_THICKNESS,
                    "root_thickness": ALMOST_CONTRIB_HYPEREDGE_ROOT_THICKNESS,
                    "line_style": ALMOST_CONTRIB_HYPEREDGE_STYLE  # Dashed
                }
                category = "almost_contributor"
                is_contributor = True  # Mark as 'processed'

        # Priority 3: Invalid T Intersection (|H n T| > k-j)
        if not is_contributor and intersect_T_size != required_X_size:
            style_info = {
                "color": f"{INVALID_T_INTERSECT_HYPEREDGE_COLOR}!{INVALID_T_INTERSECT_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                "line_thickness": INVALID_T_INTERSECT_HYPEREDGE_LINE_THICKNESS,
                "root_thickness": INVALID_T_INTERSECT_HYPEREDGE_ROOT_THICKNESS,
                "line_style": INVALID_T_INTERSECT_HYPEREDGE_STYLE  # Dashed
            }
            category = "invalid_T_intersect"
            is_contributor = True  # Mark as 'processed'

        # Priority 4: Other/Generic (Default if not caught above)
        if not is_contributor:
            style_info = {
                "color": f"{OTHER_GENERIC_HYPEREDGE_COLOR}!{OTHER_GENERIC_HYPEREDGE_BRIGHTNESS_FACTOR}!white",
                "line_thickness": OTHER_GENERIC_HYPEREDGE_LINE_THICKNESS,
                "root_thickness": OTHER_GENERIC_HYPEREDGE_ROOT_THICKNESS,
                "line_style": OTHER_GENERIC_HYPEREDGE_STYLE  # Solid gray
            }
            # Category remains "other_generic"

        hyperedge_drawing_data.append({
            "id": idx,
            "nodes": v_labels,
            "root": (root_x, root_y),
            "style": style_info,
            "category": category  # Store category for sorting draw order
        })

# --- Prepare TikZ code lines ---
lines = [r"% TikZ code generated by Python script for Common Link Graph visualization",
         r"\begin{tikzpicture}[scale=0.8]", r"% Vertex coordinates"]

# Define needed colors explicitly if not standard TikZ names (optional)

# -- Define Coordinates for Vertices AND Hyperedge Roots --
for label, (x, y) in vertices.items():
    lines.append(r"\coordinate ({}) at ({:.2f}, {:.2f});".format(label, x, y))

if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Hyperedge root coordinates")
    for data in hyperedge_drawing_data:
        rx, ry = data['root']
        lines.append(r"\coordinate (R{}) at ({:.3f}, {:.3f});".format(data['id'], rx, ry))


# Function to compute bounding box
def bounding_box(points_coords, margin=0.5):
    # (same as before)
    if not points_coords:
        return 0, 0, 0, 0
    x_vals, y_vals = zip(*points_coords)
    return min(x_vals) - margin, max(x_vals) + margin, min(y_vals) - margin, max(y_vals) + margin


# --- Drawing Order ---

# -- 1. Draw Boxes (Background) --
if DRAW_BOXES:
    lines.append(r"% Draw background boxes for T and V \ T")
    # (same as before)
    t_points_coords = [vertices[v] for v in T if v in vertices]
    if t_points_coords:
        x_min, x_max, y_min, y_max = bounding_box(t_points_coords, BOX_MARGIN)
        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2
        lines.append(
            r"\draw[fill={}, rounded corners, line width=0.5pt, draw=gray!50] "
            r"({:.2f}, {:.2f}) rectangle ({:.2f}, {:.2f});".format(
                T_BOX_BG_COLOR, x_min, y_min, x_max, y_max))
        lines.append(r"\node at ({:.2f}, {:.2f}) "
                     r"[anchor=south, inner sep=1pt, text=gray] {{$T$}};".format(x_mid, y_max))

    v_minus_t_coords = [vertices[v] for v in V_minus_T if v in vertices]
    if v_minus_t_coords:
        x_min, x_max, y_min, y_max = bounding_box(v_minus_t_coords, BOX_MARGIN)
        x_mid = (x_min + x_max) / 2
        y_mid = (y_min + y_max) / 2
        lines.append(r"\draw[fill={}, rounded corners,"
                     r" line width=0.5pt, draw=gray!50] ({:.2f}, {:.2f}) rectangle ({"
                     r":.2f}, {:.2f});".format(V_MINUS_T_BOX_BG_COLOR, x_min, y_min, x_max, y_max))
        lines.append(
            r"\node at ({:.2f}, {:.2f}) [anchor=south, inner sep=1pt, text=gray] {{$\link{{G}}{{T}}{{2}}$}};".format(
                x_mid, y_max))


# Utility function to draw a hyperedge based on its data
def draw_hyperedge(data):
    draw_lines = []
    style = data['style']
    edge_id = data['id']
    root_coord = f"R{edge_id}"
    line_options = f"line width={style['line_thickness']:.1f}pt, color={style['color']}, {style['line_style']}"
    # Draw the tree edges from root to nodes
    for node_label in data['nodes']:
        draw_lines.append(r"\draw[{}] ({}) -- ({});".format(line_options, root_coord, node_label))
    # Draw the hyperedge root dot
    draw_lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(style['color'], root_coord, style['root_thickness']))
    return draw_lines


# -- 2. Draw Invalid T-Intersection Hyperedges (Dashed Gray - Background) --
if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Draw hyperedges with |H n T| > k-j (dashed gray, background)")
    for data in hyperedge_drawing_data:
        if data['category'] == "invalid_T_intersect":
            lines.extend(draw_hyperedge(data))

# -- 3. Draw Hyperedges Contributing to Almost Links (Dashed Colored) --
if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Draw hyperedges contributing to 'almost' links (dashed colored)")
    for data in hyperedge_drawing_data:
        if data['category'] == "almost_contributor":
            lines.extend(draw_hyperedge(data))

# -- 4. Draw "Almost" Link Edges (Dashed Colored) --
if almost_link_edges_data:
    lines.append(r"% Draw 'almost' link edges (dashed colored)")
    for Y_fset, data in almost_link_edges_data.items():
        u, v = data['nodes']  # Assumes j=2
        color = data['color']
        style = f"color={color}, {ALMOST_LINK_EDGE_THICKNESS}, {ALMOST_LINK_EDGE_STYLE}"
        if u in vertices and v in vertices:
            lines.append(r"\draw[{}] ({}) -- ({});".format(style, u, v))
        else:
            print(f"Warning: Could not draw almost link edge {data['nodes']} - missing vertex.")

# -- 5. Draw Hyperedges Contributing to TRUE Links (Solid Colored) --
if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Draw hyperedges contributing to TRUE links (solid colored)")
    for data in hyperedge_drawing_data:
        if data['category'] == "true_contributor":
            lines.extend(draw_hyperedge(data))

# -- 6. Draw Confirmed TRUE Link Edges (Solid Colored) --
if link_edges_data:
    lines.append(r"% Draw TRUE common {}-link graph edges (solid colored)".format(j))
    for Y_fset, data in link_edges_data.items():
        u, v = data['nodes']  # Assumes j=2
        color = data['color']
        style = f"color={color}, {LINK_EDGE_THICKNESS}, {LINK_EDGE_STYLE}"
        if u in vertices and v in vertices:
            lines.append(r"\draw[{}] ({}) -- ({});".format(style, u, v))
        else:
            print(f"Warning: Could not draw link edge {data['nodes']} - missing vertex.")

# -- 7. Draw Other/Generic Hyperedges (Solid Gray - Default) --
if DRAW_ORIGINAL_HYPEREDGES:
    lines.append(r"% Draw other/generic hyperedges (solid gray)")
    for data in hyperedge_drawing_data:
        if data['category'] == "other_generic":
            lines.extend(draw_hyperedge(data))

# -- 8. Draw Vertices (Foreground) --
lines.append(r"% Draw vertices (foreground layer)")
# Vertices in T
for v_label in T:

    if v_label in vertices:
        lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(T_DOT_COLOR, v_label, DOT_THICKNESS))
        if ADD_VERTEX_LABELS:
            lines.append(
                r"\node[{}=1pt, color={}] at ({}) {{${}$}};".format(vertex_label_position[v_label], T_DOT_COLOR,
                                                                    v_label, v_label))
# Vertices in V \ T
for v_label in V_minus_T:
    if v_label in vertices:
        lines.append(r"\fill[{}] ({}) circle ({:.1f}pt);".format(V_MINUS_T_DOT_COLOR, v_label, DOT_THICKNESS))
        if ADD_VERTEX_LABELS:
            lines.append(
                r"\node[{}=1pt, color={}] at ({}) {{${}$}};".format(vertex_label_position[v_label], V_MINUS_T_DOT_COLOR,
                                                                    v_label, v_label))

# ... (End of vertex drawing loops) ...



# This should be the VERY LAST line added to the list before writing the file
lines.append(r"\end{tikzpicture}")

# --- Write TikZ code to a file ---
filename = "common_link.tex"  # Changed filename
output_dir = "src/figures"

if output_dir:
    os.makedirs(output_dir, exist_ok=True)
    full_path = os.path.join(output_dir, filename)
else:
    full_path = filename

try:
    with open(full_path, "w") as f:
        f.write("\n".join(lines))

    # --- Summary Output ---
    print(f"\nDetailed TikZ code for the common link graph has been written to '{full_path}'")
    print(f" - T: {T}")
    print(f" - k={k}, j={j}, required |H n T| = {required_X_size}")

    print(f"\n - Confirmed {j}-link edges found: {len(link_edges_data)}")
    for Y_fset, data in link_edges_data.items():
        print(
            f"   - {set(data['nodes'])}: color={data['color']}, style='{LINK_EDGE_STYLE}', contributors={data['contributors']}")

    print(f"\n - 'Almost' {j}-link edges found: {len(almost_link_edges_data)}")
    for Y_fset, data in almost_link_edges_data.items():
        print(
            f"   - {set(data['nodes'])}: color={data['color']}, style='{ALMOST_LINK_EDGE_STYLE}', contributors={data['contributors']}")

    print("\n - Original hyperedges styled by category:")
    categories_summary = {}
    for data in hyperedge_drawing_data:
        cat = data['category']
        style_desc = f"color={data['style']['color']}, style='{data['style']['line_style']}'"
        if cat not in categories_summary:
            categories_summary[cat] = {"count": 0, "example_style": style_desc}
        categories_summary[cat]["count"] += 1

    print(
        f"   - true_contributor ({categories_summary.get('true_contributor', {}).get('count', 0)}): Contributors to TRUE links. Style: {categories_summary.get('true_contributor', {}).get('example_style', 'N/A')}")
    print(
        f"   - almost_contributor ({categories_summary.get('almost_contributor', {}).get('count', 0)}): Contributors to ALMOST links. Style: {categories_summary.get('almost_contributor', {}).get('example_style', 'N/A')}")
    print(
        f"   - invalid_T_intersect ({categories_summary.get('invalid_T_intersect', {}).get('count', 0)}): |H n T| > {required_X_size}. Style: {categories_summary.get('invalid_T_intersect', {}).get('example_style', 'N/A')}")
    print(
        f"   - other_generic ({categories_summary.get('other_generic', {}).get('count', 0)}): Other hyperedges. Style: {categories_summary.get('other_generic', {}).get('example_style', 'N/A')}")

except IOError as e:
    print(f"Error writing file '{full_path}': {e}")
