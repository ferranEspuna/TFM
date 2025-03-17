import numpy as np
import matplotlib.pyplot as plt

from matplotlib import colormaps

cm = list(colormaps)

# Canvas boundaries and padding
x_min, x_max = 0, 10
y_min, y_max = 0, 10
padding = 0


group_A = [(2, 0), (0, 2)]
group_B = [(8, 0), (10, 2)]
group_C = [(2, 8), (8, 8)]

nA, nB, nC = len(group_A), len(group_B), len(group_C)

center_of_all = np.mean([group_A + group_B + group_C], axis=1)[0]

for map in list(plt.colormaps):

    # Create the figure
    plt.figure(figsize=(8, 8))

    plt.title(f"Colormap: {map}")

    # Plot vertices for each group
    for x, y in group_A:
        plt.scatter(x, y, color='blue', s=100, zorder=5, label="Group A" if (x, y) == group_A[0] else "")
    for x, y in group_B:
        plt.scatter(x, y, color='red', s=100, zorder=5, label="Group B" if (x, y) == group_B[0] else "")
    for x, y in group_C:
        plt.scatter(x, y, color='green', s=100, zorder=5, label="Group C" if (x, y) == group_C[0] else "")

    # Total number of hyperedges (each hyperedge is a tree connecting one vertex from each group)
    total_hyperedges = nA * nB * nC

    # Draw hyperedges as trees with unique colors (using a gradient from the viridis colormap)
    edge_index = 0
    for a in group_A:
        for b in group_B:
            for c in group_C:
                # Compute the centroid (the tree's root)
                root_x = (a[0] + b[0] + c[0] -1*center_of_all[0]) / 2
                root_y = (a[1] + b[1] + c[1] -1*center_of_all[1]) / 2

                # Choose a color from a gradient based on the hyperedge index
                color = plt.colormaps[map](edge_index / total_hyperedges)

                # Draw tree edges: from the root to each of the three vertices
                plt.plot([root_x, a[0]], [root_y, a[1]], color=color, lw=2, zorder=3)
                plt.plot([root_x, b[0]], [root_y, b[1]], color=color, lw=2, zorder=3)
                plt.plot([root_x, c[0]], [root_y, c[1]], color=color, lw=2, zorder=3)

                # Optionally, mark the root with a smaller dot
                plt.scatter(root_x, root_y, color=color, s=50, zorder=4)

                edge_index += 1

    plt.legend()
    plt.axis("equal")
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.show()
