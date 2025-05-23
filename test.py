from typing import List, Tuple
import random
from math import log, floor, ceil
import heapq
from scipy.special import binom
from itertools import combinations

from tqdm import tqdm

from random_graph import Hypergraph, RandomPermutationHypergraph, LinkGraph, RandomOracleGraph, StupidHypergraph

random.seed(1234)


def get_deg_sum_at_least(h: Hypergraph, n_vtxs: int, min_deg_sum: int) -> List[int]:
    min_heap = []
    total_deg = 0

    # for node in range(h.n):
    for node in tqdm(range(h.n), position=0):

        deg = h.degree(node)

        if len(min_heap) < n_vtxs:
            heapq.heappush(min_heap, (deg, node))
            total_deg += deg

        elif total_deg >= min_deg_sum:
            return [node for _, node in min_heap]

        elif deg > min_heap[0][0]:
            total_deg -= min_heap[0][0]
            total_deg += deg
            heapq.heapreplace(min_heap, (deg, node))
            print(f'{total_deg} > {min_deg_sum}')

        print(f"curr_len: {len(min_heap)} / {n_vtxs}, curr_deg: {total_deg} / {min_deg_sum}")

    assert False, f"The algorithm did NOT work! Something went wrong{h.k, h.n, h.N, n_vtxs, min_deg_sum}"


def get_partite(h: Hypergraph, min_m=None, t=None) -> Tuple[List, ...]:
    k = h.k

    if k == 1:
        ret = list(x for x in range(h.N) if h.is_edge((x,)))
        if t is not None:
            assert len(ret) >= t, f"t ({t}) must be less than the number of edges ({len(ret)})"
            return ret[:t],

    if t is None:
        if min_m is None:
            min_m = h.num_edges()

        min_d = min_m / h.n ** k
        print(f"min_d: {min_d}")
        assert min_m is not None, "Either t or min_m must be provided"
        raw_t = (log(h.n / 2 ** (k - 1)) / log(3 / min_d)) ** (1 / (k - 1))
        print('raw_t:', raw_t)
        t = floor(raw_t)

    assert t >= 2, "t must be at least 2"

    w = ceil(2 * t / min_d)
    W = get_deg_sum_at_least(h, w, w * k * min_d * h.n ** (k - 1))
    print(f"w: {w}, W: {W}")
    min_s = min_d ** t * h.n ** (k - 1)

    T = None
    h_prime = None

    for T in combinations(W, t):
        h_prime = LinkGraph(h, list(T))
        if h_prime.num_edges() >= min_s:
            print(f"T: {T}, min_s: {min_s}, num_edges: {h_prime.num_edges()}")
            break

    assert T is not None and h_prime is not None, "The algorithm did NOT work! Something went wrong"
    return list(T), *get_partite(h_prime, min_s, t=t)


N = 10000000
p = 0.9
K = 3
M = int((p - 0.001) * binom(N, K))
print(f"n: {N}, k: {K}, m: {M}")

# G = RandomOracleGraph(K, p, N)

G = StupidHypergraph(K, 2, N)
print('generated')
print(get_partite(G))
