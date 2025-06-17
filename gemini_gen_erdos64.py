import os
import itertools

# --- Parameters ---
SCALE = 0.8 # Reverted to a larger scale for legibility
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
    'A1': (0, 6), 'A2': (2, 7.5), 'A3': (4, 6),
    'B1': (0, 0), 'B2': (2, -1.5), 'B3': (4, 0),
    'C1': (7, 3), 'C2': (9, 4.5), 'C3': (9, 1.5),
}
V1, V2, V3 = ['A1', 'A2', 'A3'], ['B1', 'B2', 'B3'], ['C1', 'C2', 'C3']
k222_edges = [frozenset(p) for p in itertools.product(['A1','A2'], ['B1','B2'], ['C1','C2'])]
distractor_edges = [
    frozenset(['A3', 'B3', 'C3']), frozenset(['A1', 'B3', 'C1']),
    frozenset(['A3', 'B1', 'C2']), frozenset(['A2', 'B2', 'C3'])
]
hyperedges_H = k222_edges + distractor_edges
hyperedge_roots = {h: tuple(sum(v_coords[v][i] for v in h) / 3 for i in [0, 1]) for h in hyperedges_H}

# H' definitions
U_nodes = [f"{v1}{v2}" for v1 in V1 for v2 in V2]
U_labels = {f"{v1}{v2}": f"$({v1[0]}_{v1[1]},{v2[0]}_{v2[1]})$" for v1 in V1 for v2 in V2}
W_nodes = V3

# H' Coordinates (Right Graph, side-by-side with H)
u_coords_hp = {f"{V1[i]}{V2[j]}": (15, 9 - (i * 3 + j) * 1.2) for i in range(3) for j in range(3)}
w_coords_hp = {V3[i]: (21, 6 - i * 2) for i in range(3)}

adj_Hp = {u: {w: 0 for w in W_nodes} for u in U_nodes}
for u_node in U_nodes:
    v1, v2 = u_node[:2], u_node[2:]
    for w_node in W_nodes:
        if frozenset([v1, v2, w_node]) in hyperedges_H:
            adj_Hp[u_node][w_node] = 1

# --- TikZ Generation ---
lines = [
    r"% TikZ code for side-by-side dual proof sketch (v11 - layout final).",
    f"\\begin{{tikzpicture}}[scale={SCALE}, every node/.style={{transform shape, scale={SCALE}}}]",
]

# --- Graph H Drawing (Left) ---
lines.append(r"\begin{scope}")
lines.append(r"\node at (4.5, 8.5) {\Large$H$};")
for v, pos in v_coords.items(): lines.append(f"\\coordinate ({v}) at {pos};")
lines.append(r"\uncover<1->{")
for i, h in enumerate(hyperedges_H):
    lines.append(f"\\coordinate (R{i}) at {hyperedge_roots[h]};")
    lines.append(f"\\fill[gray!20] (R{i}) circle ({H_ROOT_THICKNESS}pt);")
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
    link_graph_contributors.append(frozenset([v1, v2, 'C1']))
    link_graph_contributors.append(frozenset([v1, v2, 'C2']))
for h in link_graph_contributors:
    if h in hyperedges_H:
        r_idx = hyperedges_H.index(h)
        lines.append(f"\\fill[{LINK_GRAPH_COLOR}!50] (R{r_idx}) circle ({H_ROOT_THICKNESS}pt);")
        for v in h: lines.append(f"\\draw[{LINK_GRAPH_COLOR}, line width={H_LINE_THICKNESS}pt] (R{r_idx}) -- ({v});")
for v in ['A1','A2','B1','B2']: lines.append(f"\\fill[{LINK_GRAPH_COLOR}] ({v}) circle ({H_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")
lines.append(r"\uncover<5->{")
k222_nodes_H = ['A1','A2','B1','B2','C1','C2']
for h in k222_edges:
    r_idx = hyperedges_H.index(h)
    lines.append(f"\\fill[{FINAL_K_COLOR}!70] (R{r_idx}) circle ({H_ROOT_THICKNESS+0.5}pt);")
    for v in h: lines.append(f"\\draw[{FINAL_K_COLOR}, line width={H_LINE_THICKNESS+0.5}pt] (R{r_idx}) -- ({v});")
for v in k222_nodes_H: lines.append(f"\\fill[{FINAL_K_COLOR}] ({v}) circle ({H_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")
lines.append(r"\end{scope}")

# --- Graph H' Drawing (Right) ---
lines.append(r"\begin{scope}")
lines.append(r"\node at (18, 10.5) {\Large$H'$};")
for v, pos in u_coords_hp.items(): lines.append(f"\\coordinate ({v}) at {pos};")
for v, pos in w_coords_hp.items(): lines.append(f"\\coordinate ({v}) at {pos};")
lines.append(r"\uncover<1->{")
lines.append(f"\\node[anchor=south] at (15, 10) {{{U_PARTITION_LABEL}}};")
lines.append(f"\\node[anchor=south] at (21, 8) {{{W_PARTITION_LABEL}}};")
for u in U_nodes:
    for w in W_nodes:
        if adj_Hp[u][w]: lines.append(f"\\draw[line width={HP_LINE_THICKNESS}pt, {HP_BASE_COLOR}] ({u}) -- ({w});")
for u, label in U_labels.items(): lines.append(f"\\fill[{HP_VERT_COLOR}] ({u}) circle ({HP_DOT_THICKNESS}pt) node[anchor=east, font=\\tiny] {{{label}}};")
for w in W_nodes: lines.append(f"\\fill[{HP_VERT_COLOR}] ({w}) circle ({HP_DOT_THICKNESS}pt) node[anchor=west, font=\\small] {{${w[0]}_{w[1]}$}};")
lines.append(r"}")
lines.append(r"\uncover<2->{")
options_T = f"draw, thick, {SET_T_COLOR}, rounded corners, fit=(C1)(C2), inner sep=5pt, label distance=2pt, label={{90:$T$}}"
lines.append(f"\\node[{options_T}] {{}};")
for v in ['C1', 'C2']: lines.append(f"\\fill[{SET_T_COLOR}] ({v}) circle ({HP_DOT_THICKNESS+0.5}pt);")
lines.append(r"}")
lines.append(r"\uncover<3->{")
s_T_nodes = [u for u in U_nodes if adj_Hp[u]['C1'] and adj_Hp[u]['C2']]
for u in s_T_nodes:
    lines.append(f"\\fill[{LINK_GRAPH_COLOR}] ({u}) circle ({HP_DOT_THICKNESS+0.5}pt);")
    for w in ['C1', 'C2']: lines.append(f"\\draw[line width={HP_LINE_THICKNESS+0.8}pt, {LINK_GRAPH_COLOR}] ({u}) -- ({w});")
lines.append(r"}")
lines.append(r"\uncover<4->{")
label_link = r"{[label distance=2pt]90:Edges of $\link{H}{T}{2}$}"
options_linkbox = f"draw, thick, {LINK_GRAPH_COLOR}, rounded corners, fit=(A1B1)(A2B2), inner sep=5pt, label={label_link}"
lines.append(f"\\node[{options_linkbox}] (linkbox) {{}};")
lines.append(r"}")
lines.append(r"\uncover<5->{")
for u in s_T_nodes:
    lines.append(f"\\fill[{FINAL_K_COLOR}] ({u}) circle ({HP_DOT_THICKNESS+0.5}pt);")
    for w in ['C1', 'C2']:
        lines.append(f"\\draw[line width={HP_LINE_THICKNESS+1}pt, {FINAL_K_COLOR}] ({u}) -- ({w});")
for w in ['C1', 'C2']: lines.append(f"\\fill[{FINAL_K_COLOR}] ({w}) circle ({HP_DOT_THICKNESS+0.5}pt);")
# This line includes your bug fix for the extra '$'
label_final = f"{{[color={FINAL_K_COLOR}]-90:$K(2,2,2)$ found!}}"
options_final = f"draw, very thick, {FINAL_K_COLOR}, rounded corners, fit=(A1B1)(A2B2)(C1)(C2), inner sep=8pt, label distance=-2pt, label={label_final}"
lines.append(f"\\node[{options_final}] {{}};")
lines.append(r"}")
lines.append(r"\end{scope}")
lines.append(r"\end{tikzpicture}")

# --- Write to file ---
output_filename = "src/figures/erdos64_dual_sketch.tex"
with open(output_filename, "w") as f:
    f.write("\n".join(lines))
print(f"Success: Side-by-side dual-graph TikZ code written to '{output_filename}'")