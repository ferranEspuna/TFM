import itertools

# --- Parameters ---
SCALE = 0.8
U_PARTITION_LABEL = r"$U = V_1 \times V_2$"
W_PARTITION_LABEL = r"$W = V_3$"
H_VERT_COLOR = "black"
H_DOT_THICKNESS = 4.0
H_ROOT_THICKNESS = 2.0
H_LINE_THICKNESS = 1.0
HP_VERT_COLOR = "black"
HP_DOT_THICKNESS = 4.0
HP_LINE_THICKNESS = 0.5
HP_BASE_COLOR = "black!30"

# --- Animation Colors ---
LINK_C1_COLOR = "blue"
LINK_C2_COLOR = "orange"
LINK_C3_COLOR = "green!50!black"
COMMON_LINK_COLOR = "teal"
FOUND_K22_COLOR = "purple"
FINAL_K222_COLOR = "brown!60!red"

# --- Graph Definition ---
v_coords = {
    'A1': (-4.5, 6), 'A2': (-1.5, 8), 'A3': (1.5, 10),
    'B1': (-4.5, 1), 'B2': (-1.5, -1), 'B3': (1.5, -3.2),
    'C1': (6.5, 1.85), 'C2': (6.5, 6), 'C3': (7.5, 4.1),
}
V1_nodes, V2_nodes, V3_nodes = ['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3']

k222_edges = [p for p in itertools.product(['A1', 'A2'], ['B1', 'B2'], ['C1', 'C2'])]
distractor_edges = [
    ('A3', 'B3', 'C3'), ('A2', 'B3', 'C1'),
    ('A3', 'B1', 'C2'), ('A3', 'B2', 'C3'),
    ('A1', 'B3', 'C2'), ('A3', 'B2', 'C1'),
    ('A3', 'B1', 'C1')
]
hyperedges_H = list(dict.fromkeys(k222_edges + distractor_edges))
hyperedge_fs_to_tuple_map = {frozenset(h_tuple): h_tuple for h_tuple in hyperedges_H}


def calc_root_coords(hyperedge):
    a, b, c = (v_coords[vtx] for vtx in hyperedge)
    x = (0.4 * a[0] + 0.4 * b[0] + (1 - 0.8) * c[0])
    y = (0.37 * a[1] + 0.37 * b[1] + (1 - 0.74) * c[1])
    return x, y


hyperedge_roots = {h: calc_root_coords(h) for h in hyperedges_H}

# H' definitions
U_nodes = [f"{v1}{v2}" for v1 in V1_nodes for v2 in V2_nodes]
U_labels = {f"{v1}{v2}": f"$({v1[0]}_{v1[1]},{v2[0]}_{v2[1]})$" for v1 in V1_nodes for v2 in V2_nodes}
W_nodes = V3_nodes

u_coords_hp = {f"{V1_nodes[i]}{V2_nodes[j]}": (13, 9.5 - (i * 3 + j) * 1.5) for i in range(3) for j in range(3)}
w_coords_hp = {V3_nodes[i]: (19, 7 - i * 3) for i in range(3)}


adj_Hp = {u: {w: 0 for w in W_nodes} for u in U_nodes}
for u_node in U_nodes:
    v1, v2 = u_node[:2], u_node[2:]
    for w_node in W_nodes:
        if frozenset([v1, v2, w_node]) in hyperedge_fs_to_tuple_map:
            adj_Hp[u_node][w_node] = 1

def get_2d_link_edges(w_node):
    edges = set()
    for h_edge in hyperedges_H:
        if w_node in h_edge:
            v_parts = [v for v in h_edge if v.startswith('A') or v.startswith('B')]
            if len(v_parts) == 2:
                v1, v2 = v_parts
                if v1.startswith('B'): v1, v2 = v2, v1
                edges.add((v1, v2))
    return list(edges)

# --- TikZ Generation ---
lines = [
    r"% TikZ code for side-by-side dual proof sketch (v8 - simplified).",
    f"\\begin{{tikzpicture}}[scale={SCALE}, every node/.style={{transform shape, scale={SCALE}}}]",
]

# --- BASE GRAPHS (Slide 1->) ---
lines.append(r"% === BASE GRAPHS (H and H') ===")
lines.append(r"\uncover<1->{")
lines.append(r"\begin{scope}")
lines.append(r"\node at (-6, 3.5) {\huge$H$};")
for v, pos in v_coords.items(): lines.append(f"\\coordinate ({v}) at {pos};")

for i, h in enumerate(hyperedges_H):
    lines.append(f"\\coordinate (R{i}) at {hyperedge_roots[h]};")
    lines.append(f"\\fill[gray!40] (R{i}) circle ({H_ROOT_THICKNESS}pt);")
    for v in h: lines.append(f"\\draw[gray!40, line width={H_LINE_THICKNESS}pt] (R{i}) -- ({v});")

for v in v_coords:
    label_pos = "right=2pt" if v.startswith('B') else "above=2pt"
    lines.append(
        f"\\fill[{H_VERT_COLOR}] ({v}) circle ({H_DOT_THICKNESS}pt) node[{label_pos}, font=\\Large] {{${v[0]}_{v[1]}$}};"
    )

lines.append(r"\end{scope}")


lines.append(r"\begin{scope}")
lines.append(r"\node at (21.5, 4) {\huge$H'$};")
for v, pos in u_coords_hp.items(): lines.append(f"\\coordinate ({v}) at {pos};")
for v, pos in w_coords_hp.items(): lines.append(f"\\coordinate ({v}HP) at {pos};")
lines.append(f"\\node[anchor=south] at (13, 10) {{ \\huge {U_PARTITION_LABEL} }}; ")
lines.append(f"\\node[anchor=south] at (19, 8.5) {{ \\huge {W_PARTITION_LABEL}}};")
for u in U_nodes:
    for w in W_nodes:
        if adj_Hp[u][w]: lines.append(f"\\draw[line width={HP_LINE_THICKNESS}pt, {HP_BASE_COLOR}] ({u}) -- ({w}HP);")

for u, label in U_labels.items():
    lines.append(
        f"\\fill[{HP_VERT_COLOR}] ({u}) circle ({HP_DOT_THICKNESS}pt) node[anchor=east, font=\\Large, xshift=-4pt] {{{label}}};"
    )

# MODIFICATION: Shift W-labels to the right to avoid overlap
for w in W_nodes:
    lines.append(
        f"\\fill[{HP_VERT_COLOR}] ({w}HP) circle ({HP_DOT_THICKNESS}pt) node[anchor=west, font=\\Large, xshift=4pt] {{${w[0]}_{w[1]}$}};"
    )
lines.append(r"\end{scope}")
lines.append(r"}")

# --- ANIMATION SEQUENCE ---
slide_counter = 2
link_colors = [LINK_C1_COLOR, LINK_C2_COLOR, LINK_C3_COLOR]
v3_targets = ['C1', 'C2', 'C3']

info_box_coords = "at (0, -2)"

for i, w_target in enumerate(v3_targets):
    color = link_colors[i]
    lines.append(f"\n% --- Link for {w_target} (Slide {slide_counter}) ---")
    lines.append(f"\\only<{slide_counter}>{{")
    for h_idx, h_edge in enumerate(hyperedges_H):
        if w_target in h_edge:
            lines.append(f"\\fill[{color}] (R{h_idx}) circle ({H_ROOT_THICKNESS}pt);")
            for v in h_edge: lines.append(
                f"\\draw[{color}, line width={H_LINE_THICKNESS + 0.5}pt] (R{h_idx}) -- ({v});")
    lines.append(f"\\fill[{color}] ({w_target}) circle ({H_DOT_THICKNESS + 0.5}pt);")
    lines.append(r"\begin{scope}")
    lines.append(f"\\fill[{color}] ({w_target}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for u_node in U_nodes:
        if adj_Hp[u_node][w_target]:
            lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {color}] ({u_node}) -- ({w_target}HP);")
            lines.append(f"\\fill[{color}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    lines.append(r"\end{scope}")
    lines.append(f"}}")
    slide_counter += 1
    lines.append(f"\n% --- 2D Graph for L({w_target}) (Slide {slide_counter}) ---")
    lines.append(f"\\only<{slide_counter}>{{")
    link_2d_edges = get_2d_link_edges(w_target)
    link_2d_verts = set(itertools.chain(*link_2d_edges))
    for v_start, v_end in link_2d_edges:
        lines.append(f"\\draw[line width=1.5pt, {color}, bend left=20] ({v_start}) to ({v_end});")
    for v in link_2d_verts:
        lines.append(f"\\fill[{color}] ({v}) circle ({H_DOT_THICKNESS + 0.5}pt);")
    lines.append(r"\begin{scope}")
    lines.append(f"\\node[draw, thick, fill={color}!20, rounded corners] {info_box_coords} {{2-graph $L_H({w_target})$}};")
    lines.append(r"\end{scope}")
    lines.append(r"\begin{scope}")
    lines.append(f"\\fill[{color}] ({w_target}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for u_node in U_nodes:
        if adj_Hp[u_node][w_target]:
            lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {color}] ({u_node}) -- ({w_target}HP);")
            lines.append(f"\\fill[{color}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    lines.append(r"\end{scope}")
    lines.append(f"}}")
    slide_counter += 1

lines.append(f"\n% --- Common Link for T={{C1, C2}} (Slide {slide_counter}) ---")
lines.append(f"\\only<{slide_counter}>{{")
s_T_nodes = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
for h_idx, h_edge in enumerate(hyperedges_H):
    v1_v2_part_list = [v for v in h_edge if not v.startswith('C')]
    if len(v1_v2_part_list) == 2:
     v1_v2_part = tuple(sorted(v1_v2_part_list))
     u_node_equiv = f"{v1_v2_part[0]}{v1_v2_part[1]}"
     if u_node_equiv in s_T_nodes and ('C1' in h_edge or 'C2' in h_edge):
         lines.append(f"\\fill[{COMMON_LINK_COLOR}] (R{h_idx}) circle ({H_ROOT_THICKNESS}pt);")
         for v in h_edge: lines.append(
             f"\\draw[{COMMON_LINK_COLOR}, line width={H_LINE_THICKNESS + 0.5}pt] (R{h_idx}) -- ({v});")
for v in ['C1', 'C2']: lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v}) circle ({H_DOT_THICKNESS + 0.5}pt);")
for u_node in s_T_nodes:
    v1, v2 = u_node[:2], u_node[2:]
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v1}) circle ({H_DOT_THICKNESS + 0.5}pt);")
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v2}) circle ({H_DOT_THICKNESS + 0.5}pt);")
lines.append(r"\begin{scope}")
for u_node in s_T_nodes:
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for w_node in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {COMMON_LINK_COLOR}] ({u_node}) -- ({w_node}HP);")
for v in ['C1', 'C2']: lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
lines.append(r"\end{scope}")
lines.append(f"}}")
slide_counter += 1
lines.append(f"\n% --- 2D Graph for L(T) (Slide {slide_counter}) ---")
lines.append(f"\\only<{slide_counter}>{{")
link_c1_2d = get_2d_link_edges('C1')
link_c2_2d = get_2d_link_edges('C2')
common_2d_edges = list(set(link_c1_2d) & set(link_c2_2d))
common_2d_verts = set(itertools.chain(*common_2d_edges))
for v_start, v_end in common_2d_edges:
    lines.append(f"\\draw[line width=1.5pt, {COMMON_LINK_COLOR}, bend left=20] ({v_start}) to ({v_end});")
for v in common_2d_verts:
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v}) circle ({H_DOT_THICKNESS + 0.5}pt);")
lines.append(f"\\node[draw, thick, fill={COMMON_LINK_COLOR}!20, rounded corners] {info_box_coords} {{2-graph $L_H(T)$}};")
lines.append(r"\begin{scope}")
s_T_nodes = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
for u_node in s_T_nodes:
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for w_node in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {COMMON_LINK_COLOR}] ({u_node}) -- ({w_node}HP);")
for v in ['C1', 'C2']: lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({v}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
lines.append(r"\end{scope}")
lines.append(f"}}")
slide_counter += 1
lines.append(f"\n% --- Found K(2,2) in L(T) (Slide {slide_counter}) ---")
lines.append(f"\\only<{slide_counter}>{{")
k22_edges = [p for p in itertools.product(['A1', 'A2'], ['B1', 'B2'])]
k22_verts = ['A1', 'A2', 'B1', 'B2']
for v_start, v_end in common_2d_edges:
    lines.append(f"\\draw[line width=1.5pt, {COMMON_LINK_COLOR}!40, bend left=20] ({v_start}) to ({v_end});")
for v_start, v_end in k22_edges:
    lines.append(f"\\draw[line width=2pt, {FOUND_K22_COLOR}, bend left=20] ({v_start}) to ({v_end});")
for v in k22_verts:
    lines.append(f"\\fill[{FOUND_K22_COLOR}] ({v}) circle ({H_DOT_THICKNESS + 0.5}pt);")
lines.append(
    f"\\node[draw, thick, fill={FOUND_K22_COLOR}!20, rounded corners] {info_box_coords} {{$K(2,2) \\subset L_H(T)$}};")
lines.append(r"\begin{scope}")
s_T_nodes = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
k22_unodes = ['A1B1', 'A1B2', 'A2B1', 'A2B2']
extra_link_unodes = [u for u in s_T_nodes if u not in k22_unodes]
for u_node in extra_link_unodes:
    lines.append(f"\\fill[{COMMON_LINK_COLOR}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for w_node in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {COMMON_LINK_COLOR}] ({u_node}) -- ({w_node}HP);")
for u_node in k22_unodes:
    lines.append(f"\\fill[{FOUND_K22_COLOR}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for w_node in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {FOUND_K22_COLOR}] ({u_node}) -- ({w_node}HP);")
for v in ['C1', 'C2']:
    lines.append(f"\\fill[{FOUND_K22_COLOR}] ({v}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
lines.append(r"\end{scope}")
lines.append(f"}}")
slide_counter += 1
lines.append(f"\n% --- FINAL K(2,2,2) in H (Slide {slide_counter}) ---")
lines.append(f"\\only<{slide_counter}>{{")
k222_nodes_H = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
for h_edge in hyperedges_H:
    if all(v in k222_nodes_H for v in h_edge) and frozenset(h_edge) in hyperedge_fs_to_tuple_map and len(h_edge)==3:
        r_idx = hyperedges_H.index(h_edge)
        lines.append(f"\\fill[{FINAL_K222_COLOR}] (R{r_idx}) circle ({H_ROOT_THICKNESS + 0.5}pt);")
        for v in h_edge: lines.append(
            f"\\draw[{FINAL_K222_COLOR}, line width={H_LINE_THICKNESS + 0.8}pt] (R{r_idx}) -- ({v});")
for v in k222_nodes_H: lines.append(f"\\fill[{FINAL_K222_COLOR}] ({v}) circle ({H_DOT_THICKNESS + 0.5}pt);")
lines.append(
    f"\\node[draw, thick, fill={FINAL_K222_COLOR}!20, rounded corners, align=center] {info_box_coords} {{$K(2,2,2)$ found in $H$}};")
lines.append(r"\begin{scope}")
k22_unodes = ['A1B1', 'A1B2', 'A2B1', 'A2B2']
for u_node in k22_unodes:
    lines.append(f"\\fill[{FINAL_K222_COLOR}] ({u_node}) circle ({HP_DOT_THICKNESS + 0.5}pt);")
    for w_node in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS + 0.8}pt, {FINAL_K222_COLOR}] ({u_node}) -- ({w_node}HP);")
for v in ['C1', 'C2']: lines.append(f"\\fill[{FINAL_K222_COLOR}] ({v}HP) circle ({HP_DOT_THICKNESS + 0.5}pt);")
lines.append(r"\end{scope}")
lines.append(f"}}")

lines.append(r"\end{tikzpicture}")

# --- Write to file ---
output_filename = "src/figures/erdos64_dual_sketch.tex"
try:
    with open(output_filename, "w") as f:
        f.write("\n".join(lines))
    print(f"Success: New animated TikZ code with H' shifted left written to '{output_filename}'")
    print(f"The animation will have {slide_counter} steps.")
except Exception as e:
    print(f"Error: Could not write to file. {e}")