import tqdm
from typing import Tuple, List
from itertools import combinations
from functools import cache
from scipy.special import binom
from random_permutation import RandomPermutation


class Hypergraph:
    def __init__(self, n, k, N):
        self.N = N
        self.n = n
        self.k = k

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        raise NotImplementedError

    def neighbours(self, node: int):

        others = list(set(range(self.N)) - {node})
        for other_set in tqdm.tqdm(combinations(others, self.k - 1), total=binom(self.N - 1, self.k - 1), position=1):
        # for other_set in combinations(others, self.k - 1):

            edge = (node, *other_set)
            if self.is_edge(edge):
                yield tuple(other_set)

    @cache
    def degree(self, node: int):
        return sum(1 for _ in self.neighbours(node))

    def num_edges(self):
        return sum(1 for e in combinations(range(self.N), self.k) if self.is_edge(e))


class RandomOracleGraph(Hypergraph):

    def __init__(self, k, p, N, seed=1234):
        super().__init__(N, k, N)
        self.p = p
        self.seed = seed

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        if len(edge) != self.k:
            return False

        vtxs_in_order = sorted(edge)
        h = hash(tuple(vtxs_in_order + [self.seed])) % 1e8
        return h < self.p * 1e8

    @cache
    def num_edges(self):
        # return sum(self.degree(node) for node in tqdm.tqdm(range(self.N), position=1)) // self.k
        return sum(self.degree(node) for node in (range(self.n))) // self.k

    @cache
    def expected_num_edges(self):
        return self.p * binom(self.n, self.k)


class StupidHypergraph(Hypergraph):
    def __init__(self, k, mod, N):
        super().__init__(N, k, N)
        self.mod = mod

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        return sum(edge) % self.mod == 0

    def num_edges(self):
        return binom(self.N, self.k) // self.mod



class RandomPermutationHypergraph(Hypergraph):

    def __init__(self, n, k, m, N):
        super().__init__(n, k, N)
        self.m = m
        self.perm = RandomPermutation(binom(n, k), num_ciphers=1)
        self.end = n
        self.start = 0

    def get_edge_index(self, edge):
        comb = sorted(edge)

        idx = 0
        comb = [self.start - 1] + list(comb)

        for pos in range(1, self.k + 1):
            displacement = comb[pos] - comb[pos - 1] - 1
            for j in range(1, displacement + 1):
                idx += int(binom(self.end - (comb[pos - 1] + j + 1), self.k - pos))

        return idx

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        if len(edge) != self.k:
            return False
        permuted_idx = self.perm[self.get_edge_index(edge)]
        return permuted_idx < self.m

    def num_edges(self):
        return self.m


class LinkGraph(Hypergraph):
    def __init__(self, h: Hypergraph, s: List[int]):
        super().__init__(h.n - len(s), h.k - 1, h.N)
        self.h = h
        self.s = s

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        assert len(edge) == self.k

        if any(v in self.s for v in edge):
            return False

        assert len(edge) == self.k, "The edge must have k vertices"

        return all(self.h.is_edge((*edge, v)) for v in self.s)


if __name__ == "__main__":
    G = RandomOracleGraph(10, 3, 0.5)
    print(G.num_edges())
    print(G.expected_num_edges())

    H = RandomPermutationHypergraph(10, 3, 60)
    print(H.num_edges())

    real_n_edges = 0
    for i, e in enumerate(combinations(range(10), 3)):
        if H.is_edge(e):
            real_n_edges += 1
        assert i == H.get_edge_index(e)

    assert real_n_edges == H.num_edges()
