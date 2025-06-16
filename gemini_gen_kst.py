# generate_kst_proof_sketch.py (v22 - Granular highlighting)
import itertools
import pathlib

# --- Adjacency matrix ---
adj_matrix = [
    [1, 1, 1, 1],  # U_1
    [1, 1, 1, 0],  # U_2
    [1, 0, 0, 1],  # U_3
    [0, 1, 0, 1],  # U_4
    [0, 0, 1, 1]   # U_5
]
U_SIZE, W_SIZE = len(adj_matrix), len(adj_matrix[0])

# --- Main Parameters for Customization ---
GRAPH_VERTICAL_SCALE, GRAPH_HORIZONTAL_SCALE, SCALE = 1.0, 4.5, 0.8
HIGHLIGHTED_LINE_COLOR, STARS_HIGHLIGHT_COLOR, CALLOUT_COLOR = "brown!40!red", "teal", "yellow"
BOX_BG_COLOR = f"{HIGHLIGHTED_LINE_COLOR}!20"
TOP_BOX_Y_POS, BOTTOM_BOX_Y_POS = 5.0, -1.5

# --- Automatically Derived Parameters ---
BOX_CENTER_X = GRAPH_HORIZONTAL_SCALE / 2.0
BOX_WIDTH = GRAPH_HORIZONTAL_SCALE + 2.0

# --- Drawing parameters ---
LINE_THICKNESS, DOT_THICKNESS = 0.7, 2.8
output_filename = "src/figures/kst_proof_sketch.tex"

# --- TikZ Code Generation ---
lines = []
lines.append(r"% TikZ code for KST proof sketch, v22 (granular highlights)")
lines.append(f"\\begin{{tikzpicture}}[scale={SCALE}, every node/.style={{transform shape, scale={SCALE}}}]")
lines.append(r"\pgfdeclarelayer{background}\pgfdeclarelayer{main}\pgfsetlayers{background,main}")

# Define Vertex Coordinates
u_y_coords = [4 - i * GRAPH_VERTICAL_SCALE for i in range(U_SIZE)]
for i in range(U_SIZE): lines.append(f"\\coordinate (U{i}) at (0, {u_y_coords[i]});")
w_y_coords = [3.5 - i * GRAPH_VERTICAL_SCALE for i in range(W_SIZE)]
for i in range(W_SIZE): lines.append(f"\\coordinate (W{i}) at ({GRAPH_HORIZONTAL_SCALE}, {w_y_coords[i]});")

lines.append(r"\begin{pgfonlayer}{main}")

# --- STAGE 1 (Slide 1->...): Base Graph and Top Box ---
lines.append(r"\uncover<1->{")
lines.append(f"  \\node[draw, thick, fill={CALLOUT_COLOR}!20, rounded corners, align=center, text width={BOX_WIDTH}cm] at ({BOX_CENTER_X}, {TOP_BOX_Y_POS}) "
             r"{This graph has the maximum number of edges ($|E|=13$) to be $K_{3,2}$-free.};")
for i in range(U_SIZE):
    for j in range(W_SIZE):
        if adj_matrix[i][j] == 1: lines.append(f"  \\draw[line width={LINE_THICKNESS}pt, black!25] (U{i}) -- (W{j});")
for i in range(U_SIZE): lines.append(f"  \\fill[black] (U{i}) circle ({DOT_THICKNESS}pt) node[anchor=east] {{$U_{{{i + 1}}}$}};")
for i in range(W_SIZE): lines.append(f"  \\fill[black] (W{i}) circle ({DOT_THICKNESS}pt) node[anchor=west] {{$W_{{{i + 1}}}$}};")
lines.append(r"}")

# --- STAGE 2 (Slide 2 ONLY): The "Add Edge" animation ---
lines.append(r"\only<2>{")
# ... (This section is kept from the previous version) ...
target_w, target_u = [1, 2], [0, 1, 3]; critical_u, critical_w = 3, 2
for j in target_w: lines.append(f"  \\fill[{HIGHLIGHTED_LINE_COLOR}] (W{j}) circle ({DOT_THICKNESS + 0.5}pt);")
for i in target_u: lines.append(f"  \\fill[{HIGHLIGHTED_LINE_COLOR}] (U{i}) circle ({DOT_THICKNESS + 0.5}pt);")
lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}, dashed, -] (U{critical_u}) -- (W{critical_w}) node[midway, below, sloped, font=\scriptsize] {{Add edge}};")
for i in target_u:
    for j in target_w:
        if adj_matrix[i][j] == 1: lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}] (U{i}) -- (W{j});")
lines.append(f"  \\node[draw, thick, fill={BOX_BG_COLOR}, rounded corners, align=center, text width={BOX_WIDTH-0.5}cm, overlay] at ({BOX_CENTER_X}, {BOTTOM_BOX_Y_POS}) "
             r"{{For example, adding the edge $\{U_4, W_3\}$ creates a $K_{3,2}$ on vertices "
             r"$\{U_1, U_2, U_4\}$ and $\{W_2, W_3\}$.}};")
lines.append(r"}")


# --- STAGE 3 (Slides 3-8): The "Counting Stars" animation ---
# Box for this stage
lines.append(r"\uncover<3-8>{")
lines.append(f"  \\node[draw, thick, fill={STARS_HIGHLIGHT_COLOR}!20, rounded corners, align=center, text width={BOX_WIDTH-0.5}cm, overlay] at ({BOX_CENTER_X}, {BOTTOM_BOX_Y_POS}) "
             r"{{For $x=U_1$, we count its $\binom{4}{2}=6$ stars.}};")
lines.append(r"}")
# Animation loop for this stage
star_center_u_idx = 0; neighbors_of_u1 = [j for j, edge in enumerate(adj_matrix[star_center_u_idx]) if edge == 1]
neighbor_pairs = list(itertools.combinations(neighbors_of_u1, 2))
for i, pair in enumerate(neighbor_pairs):
    slide_num = i + 3
    lines.append(f"\\only<{slide_num}>{{")
    lines.append(f"  \\fill[{STARS_HIGHLIGHT_COLOR}] (U{star_center_u_idx}) circle ({DOT_THICKNESS + 0.5}pt);")
    w_idx_1, w_idx_2 = pair
    lines.append(f"  \\fill[{STARS_HIGHLIGHT_COLOR}] (W{w_idx_1}) circle ({DOT_THICKNESS + 0.5}pt);")
    lines.append(f"  \\fill[{STARS_HIGHLIGHT_COLOR}] (W{w_idx_2}) circle ({DOT_THICKNESS + 0.5}pt);")
    lines.append(f"  \\draw[line width={LINE_THICKNESS * 1.5}pt, {STARS_HIGHLIGHT_COLOR}] (U{star_center_u_idx}) -- (W{w_idx_1});")
    lines.append(f"  \\draw[line width={LINE_THICKNESS * 1.5}pt, {STARS_HIGHLIGHT_COLOR}] (U{star_center_u_idx}) -- (W{w_idx_2});")
    lines.append(r"}")

# stage 4 averaging
lines.append(r"\uncover<9>{")
lines.append(
    f"  \\node[draw, thick, fill={STARS_HIGHLIGHT_COLOR}!20, rounded corners, align=center, text width={BOX_WIDTH - 0.5}cm, overlay] at ({BOX_CENTER_X}, {BOTTOM_BOX_Y_POS}) "
    r"{{In the example, there are at least $5\binom{13/5}{2} = 10.4$ stars (there are actually 12)}};")
lines.append(r"}")

# --- STAGE 4 (Slides 10-12): The "Bounding" animation ---
# Box for this stage
lines.append(r"\uncover<10-12>{")
lines.append(f"  \\node[draw, thick, fill={HIGHLIGHTED_LINE_COLOR}!20, rounded corners, align=center, text width={BOX_WIDTH-0.5}cm, overlay] at ({BOX_CENTER_X}, {BOTTOM_BOX_Y_POS}) "
             r"{{Each set $T \subset W$ (in this case, $T = \{W_1, W_2\})$ is in at most $s-1 = 3 - 1 = 2$ stars. In total, at most $2 \binom{4}{2}=12$ stars.}};")
lines.append(r"}")
# Define vertices for this stage
bounding_T_indices = [1, 2]; bounding_S_indices = [0, 1]

# --- NEW HIGHLIGHTING LOGIC ---
# Highlight vertices of the first star (U1, W2, W3) from slide 11 onwards
lines.append(r"\uncover<11-12>{")
lines.append(f"  \\fill[{HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[0]}) circle ({DOT_THICKNESS + 0.5}pt);")
for j in bounding_T_indices:
    lines.append(f"  \\fill[{HIGHLIGHTED_LINE_COLOR}] (W{j}) circle ({DOT_THICKNESS + 0.5}pt);")
lines.append(r"}")
# Highlight center of second star (U2) from slide 12 onwards
lines.append(r"\uncover<12>{")
lines.append(f"  \\fill[{HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[1]}) circle ({DOT_THICKNESS + 0.5}pt);")
lines.append(r"}")

# Show the first star's edges on slide 11
lines.append(r"\only<11>{")
lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[0]}) -- (W{bounding_T_indices[0]});")
lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[0]}) -- (W{bounding_T_indices[1]});")
lines.append(r"}")
# Show the second star's edges on slide 12
lines.append(r"\only<12>{")
lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[1]}) -- (W{bounding_T_indices[0]});")
lines.append(f"  \\draw[line width={LINE_THICKNESS*1.5}pt, {HIGHLIGHTED_LINE_COLOR}] (U{bounding_S_indices[1]}) -- (W{bounding_T_indices[1]});")
lines.append(r"}")

lines.append(r"\uncover<13>{")
lines.append(f"  \\node[draw, thick, fill={CALLOUT_COLOR}!20, rounded corners, align=center, text width={BOX_WIDTH-0.5}cm, overlay] at ({BOX_CENTER_X}, {BOTTOM_BOX_Y_POS}) "
             r"{{In the example, we conclude that $10.4 \leq 12$, which is true. For bigger values of $z$ this would fail, leading to contradiction and therefore upper bounding $z$. In fact, z=14 already fails! }};")
lines.append(r"}")



lines.append(r"\end{pgfonlayer}\end{tikzpicture}")

# --- Write TikZ code to file ---
output_path = pathlib.Path(output_filename)
output_path.parent.mkdir(parents=True, exist_ok=True)
try:
    with open(output_path, "w") as f: f.write("\n".join(lines))
    print(f"Success: Final complete TikZ code (v22) has been written to '{output_filename}'")
except Exception as e:
    print(f"Error: Could not write to file. {e}")