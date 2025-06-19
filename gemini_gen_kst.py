import itertools
import pathlib

# --- Parameters ---
SCALE = 0.8
U_PARTITION_LABEL = r"$U = V_1 \times V_2$"
W_PARTITION_LABEL = r"$W = V_3$"
H_VERT_COLOR = "black"
H_DOT_THICKNESS = 4.0
H_ROOT_THICKNESS = 2.0
H_LINE_THICKNESS = 1.0
HP_VERT_COLOR = "black"
HP_DOT_THICKNESS = 2.5
HP_LINE_THICKNESS = 0.5
HP_BASE_COLOR = "black!30"
SET_T_COLOR = "orange"
LINK_GRAPH_COLOR = "teal"
FINAL_K_COLOR = "brown!60!red"

# --- Graph Definition ---
# H coordinates (Left Graph)
v_coords = {
    'A1': (-3, 5), 'A2': (0, 7), 'A3': (3, 9),
    'B1': (-3, 0), 'B2': (0, -2), 'B3': (3, -4),
    'C1': (8, 0.85), 'C2': (8, 5), 'C3': (9, 3.1),
}
V1, V2, V3 = ['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3']

k222_edges = [p for p in itertools.product(['A1','A2'], ['B1','B2'], ['C1','C2'])]
distractor_edges = [
    ('A3', 'B3', 'C3'), ('A2', 'B3', 'C1'),
    ('A3', 'B1', 'C2'), ('A3', 'B2', 'C3'), ('A3', 'B1', 'C1'),
]

hyperedges_H = k222_edges + distractor_edges
hyperedge_fs_to_tuple_map = {frozenset(h_tuple): h_tuple for h_tuple in hyperedges_H}


def calc_root_coords(hyperedge):
    a, b, c = (v_coords[vtx] for vtx in hyperedge)
    ab_x_factor, c_x_factor = 0.4, 0.2
    ab_y_factor, c_y_factor = 0.37, 0.26
    x = (ab_x_factor * a[0] + ab_x_factor * b[0] + c_x_factor * c[0])
    y = (ab_y_factor * a[1] + ab_y_factor * b[1] + c_y_factor * c[1])
    return x, y


hyperedge_roots = {h: calc_root_coords(h) for h in hyperedges_H}

# H' definitions (nodes for the dual graph)
U_nodes = [f"{v1}{v2}" for v1 in V1 for v2 in V2]
U_labels = {f"{v1}{v2}": f"$({v1[0]}_{v1[1]},{v2[0]}_{v2[1]})$" for v1 in V1 for v2 in V2}
W_nodes = V3

# H' Coordinates (Right Graph, side-by-side with H)
u_coords_hp = {f"{V1[i]}{V2[j]}": (15, 9 - (i * 3 + j) * 1.2) for i in range(3) for j in range(3)}
w_coords_hp = {V3[i]: (21, 6 - i * 2) for i in range(3)}

# Adjacency list for H'
adj_Hp = {u: {w: 0 for w in W_nodes} for u in U_nodes}
for u_node in U_nodes:
    v1, v2 = u_node[:2], u_node[2:]
    for w_node in W_nodes:
        potential_hyperedge_fs = frozenset([v1, v2, w_node])
        if potential_hyperedge_fs in hyperedge_fs_to_tuple_map:
            adj_Hp[u_node][w_node] = 1

# --- TikZ Generation ---
lines = [
    r"% TikZ code for side-by-side dual proof sketch (v12 - naming clash fixed).",
    f"\\begin{{tikzpicture}}[scale={SCALE}, every node/.style={{transform shape, scale={SCALE}}}]",
]

# --- Graph H Drawing (Left) ---
lines.append(r"\begin{scope}")
lines.append(r"\node at (4.5, 8.5) {\Large$H$};")
for v, pos in v_coords.items(): lines.append(f"\\coordinate ({v}) at {pos};")

lines.append(r"\uncover<1->{")
for i, h in enumerate(hyperedges_H):
    lines.append(f"\\coordinate (R{i}) at {hyperedge_roots[h]};")
    lines.append(f"\\fill[gray!40] (R{i}) circle ({H_ROOT_THICKNESS}pt);")
    for v in h: lines.append(f"\\draw[gray!40, line width={H_LINE_THICKNESS}pt] (R{i}) -- ({v});")
for v in v_coords: lines.append(f"\\fill[{H_VERT_COLOR}] ({v}) circle ({H_DOT_THICKNESS}pt) node[above=2pt, font=\\small] {{${v[0]}_{v[1]}$}};")
lines.append(r"}")

lines.append(r"\uncover<2->{")
for v in ['C1', 'C2']: lines.append(f"\\fill[{SET_T_COLOR}] ({v}) circle ({H_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")

lines.append(r"\uncover<3->{")
link_graph_contributors = []
s_T_nodes_for_H = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
for u_node in s_T_nodes_for_H:
    v1, v2 = u_node[:2], u_node[2:]
    fs_c1 = frozenset([v1, v2, 'C1'])
    if fs_c1 in hyperedge_fs_to_tuple_map:
        link_graph_contributors.append(hyperedge_fs_to_tuple_map[fs_c1])
    fs_c2 = frozenset([v1, v2, 'C2'])
    if fs_c2 in hyperedge_fs_to_tuple_map:
        link_graph_contributors.append(hyperedge_fs_to_tuple_map[fs_c2])

for h in link_graph_contributors:
    if h in hyperedges_H:
        r_idx = hyperedges_H.index(h)
        lines.append(f"\\fill[{LINK_GRAPH_COLOR}] (R{r_idx}) circle ({H_ROOT_THICKNESS}pt);")
        for v in h: lines.append(f"\\draw[{LINK_GRAPH_COLOR}, line width={H_LINE_THICKNESS}pt] (R{r_idx}) -- ({v});")
for v in ['A1','A2','B1','B2']: lines.append(f"\\fill[{LINK_GRAPH_COLOR}] ({v}) circle ({H_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")

lines.append(r"\uncover<5->{")
k222_nodes_H = ['A1','A2','B1','B2','C1','C2']
for h in k222_edges:
    if h in hyperedges_H:
        r_idx = hyperedges_H.index(h)
        lines.append(f"\\fill[{FINAL_K_COLOR}] (R{r_idx}) circle ({H_ROOT_THICKNESS+0.5}pt);")
        for v in h: lines.append(f"\\draw[{FINAL_K_COLOR}, line width={H_LINE_THICKNESS+0.5}pt] (R{r_idx}) -- ({v});")
for v in k222_nodes_H: lines.append(f"\\fill[{FINAL_K_COLOR}] ({v}) circle ({H_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")
lines.append(r"\end{scope}")

# --- Graph H' Drawing (Right) ---
lines.append(r"\begin{scope}")
lines.append(r"\node at (18, 10.5) {\Large$H'$};")
# Define coordinates for U and W nodes in H'
for v, pos in u_coords_hp.items(): lines.append(f"\\coordinate ({v}) at {pos};")
# Use a unique suffix "HP" for the coordinates of the W partition to avoid clashes
for v, pos in w_coords_hp.items(): lines.append(f"\\coordinate ({v}HP) at {pos};") # CHANGED

lines.append(r"\uncover<1->{")
lines.append(f"\\node[anchor=south] at (15, 10) {{{U_PARTITION_LABEL}}};")
lines.append(f"\\node[anchor=south] at (21, 8) {{{W_PARTITION_LABEL}}};")
# Draw edges in H' (initially grey)
for u in U_nodes:
    for w in W_nodes:
        if adj_Hp[u][w]: lines.append(f"\\draw[line width={HP_LINE_THICKNESS}pt, {HP_BASE_COLOR}] ({u}) -- ({w}HP);") # CHANGED
# Draw U nodes with labels
for u, label in U_labels.items(): lines.append(f"\\fill[{HP_VERT_COLOR}] ({u}) circle ({HP_DOT_THICKNESS}pt) node[anchor=east, font=\\tiny] {{{label}}};")
# Draw W nodes with labels
for w in W_nodes: lines.append(f"\\fill[{HP_VERT_COLOR}] ({w}HP) circle ({HP_DOT_THICKNESS}pt) node[anchor=west, font=\\small] {{${w[0]}_{w[1]}$}};") # CHANGED
lines.append(r"}")

lines.append(r"\uncover<2->{")
# Highlight set T (C1, C2)
options_T = f"draw, thick, {SET_T_COLOR}, rounded corners, fit=(C1HP)(C2HP), inner sep=5pt, label distance=2pt, label={{90:$T$}}" # CHANGED
lines.append(f"\\node[{options_T}] {{}};")
for v in ['C1', 'C2']: lines.append(f"\\fill[{SET_T_COLOR}] ({v}HP) circle ({HP_DOT_THICKNESS+0.5}pt);") # CHANGED
lines.append(r"}")

lines.append(r"\uncover<3->{")
# Highlight nodes in S_T and edges from S_T to T
s_T_nodes = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
for u in s_T_nodes:
    lines.append(f"\\fill[{LINK_GRAPH_COLOR}] ({u}) circle ({HP_DOT_THICKNESS+0.5}pt);")
    for w in ['C1', 'C2']: lines.append(f"\\draw[line width={HP_LINE_THICKNESS+0.8}pt, {LINK_GRAPH_COLOR}] ({u}) -- ({w}HP);") # CHANGED
lines.append(r"}")

lines.append(r"\uncover<4->{")
# Draw a box around the link graph edges in H'
label_link = r"{[label distance=2pt]90:Edges of $\link{H}{T}{2}$}"
options_linkbox = f"draw, thick, {LINK_GRAPH_COLOR}, rounded corners, fit=(A1B1)(A2B2), inner sep=5pt, label={label_link}"
lines.append(f"\\node[{options_linkbox}] (linkbox) {{}};")
lines.append(r"}")

lines.append(r"\uncover<5->{")
# Highlight the final K(2,2,2) structure in H'
for u in s_T_nodes:
    lines.append(f"\\fill[{FINAL_K_COLOR}] ({u}) circle ({HP_DOT_THICKNESS+0.5}pt);")
    for w in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS+1}pt, {FINAL_K_COLOR}] ({u}) -- ({w}HP);") # CHANGED
for w in ['C1', 'C2']: lines.append(f"\\fill[{FINAL_K_COLOR}] ({w}HP) circle ({HP_DOT_THICKNESS+0.5}pt);") # CHANGED
# Add label for the found K(2,2,2)
label_final = f"{{[color={FINAL_K_COLOR}]-90:$K(2,2,2)$ found!}}"
options_final = f"draw, very thick, {FINAL_K_COLOR}, rounded corners, fit=(A1B1)(A2B2)(C1HP)(C2HP), inner sep=8pt, label distance=-2pt, label={label_final}" # CHANGED
lines.append(f"\\node[{options_final}] {{}};")
lines.append(r"}")
lines.append(r"\end{scope}")
lines.append(r"\end{tikzpicture}")

# --- Write to file ---
output_filename = "src/figures/erdos64_dual_sketch.tex"
try:
    with open(output_filename, "w") as f:
        f.write("\n".join(lines))
    print(f"Success: Final complete TikZ code (v22) has been written to '{output_filename}'")
except Exception as e:
    print(f"Error: Could not write to file. {e}")
