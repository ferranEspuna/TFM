from typing import List, Set
import hypergraphx.generation as generation
import random
from math import log, floor, ceil, e
import heapq
from scipy.special import binom
from itertools import combinations

from tqdm import tqdm

from random_graph import RandomHypergraph, RandomPermutationHypergraph

random.seed(1234)


def calc_r(q, d):
    return ceil(2 * q / d)


def calc_s(q, k, d, n):
    return floor((d ** q) * (n ** (k - 1)))


# get the set R of r nodes with more edges
def get_R(g: RandomHypergraph, r: int, k: int, d: float) -> List[int]:
    assert 0 <= r <= g.n, "r must be between 1 and the number of nodes"

    min_total_deg = d * r * g.n ** (k - 1)
    total_deg = 0

    if r == 0:
        return []

    min_heap = []
    for node in tqdm(range(g.n)):

        deg = g.degree(node)

        if len(min_heap) < r:
            heapq.heappush(min_heap, (deg, node))
            total_deg += deg

        elif deg > min_heap[0][0]:
            total_deg -= min_heap[0][0]
            total_deg += deg
            heapq.heapreplace(min_heap, (deg, node))

        if total_deg >= min_total_deg:
            break

    else:
        assert False, "The algorithm did NOT work! Something went wrong"

    return [node for _, node in min_heap]


def get_2_partite(g: RandomHypergraph):

    assert g.k == 2, "The algorithm only works for 2-partite graphs"
    n: int = g.n
    m: int = g.num_edges()

    d: float = m / n ** 2
    pre_q = log(n / 2) / log(2 * e / d)
    print(pre_q)
    q: int = floor(pre_q)
    assert q >= 2, "g is not dense enought to apply the algorithm"

    r: int = calc_r(q, d)
    assert r <= n, "r must be less than the number of nodes. Something went wrong"
    assert q <= r, "q must be less than r. Something went wrong"

    s: int = calc_s(q, 2, d, n)
    assert s <= binom(n - r, 1)

    R: List[int] = get_R(g, r, 2, d)
    R_set: Set[int] = set(R)

    # iterate over q-subsets of R
    for Q in combinations(R, q):

        S = set(range(g.n)) - R_set

        for q_node in Q:
            S &= set(i for i, in g.neighbours(q_node))

        if len(S) >= q:
            return list(Q), list(S)[:q]

    assert False, "The algorithm did NOT work! Something went wrong"


N = 5000
p = 0.9

G = RandomPermutationHypergraph(N, 2, int(p * binom(N, 2)))
print(G.num_edges())
print('generated')
print(get_2_partite(G))
