import tqdm
from typing import Tuple
from itertools import combinations
from functools import cache
from scipy.special import binom
from random_permutation import RandomPermutation


class RandomHypergraph:

    def __init__(self, n, k):
        self.n = n
        self.k = k

    def is_edge(self, edge: Tuple[int, ...]) -> bool:
        raise NotImplementedError

    def neighbours(self, node: int):

        others = list(set(range(self.n)) - {node})
        for other_set in combinations(others, self.k - 1):
            edge = (node, *other_set)
            if self.is_edge(edge):
                yield (i for i in edge if i != node)

    @cache
    def degree(self, node: int):
        return sum(1 for _ in self.neighbours(node))

    def num_edges(self):
        raise NotImplementedError


class RandomOracleGraph(RandomHypergraph):

    def __init__(self, n, k, p, seed=1234):
        super().__init__(n, k)
        self.p = p
        self.seed = seed

    def is_edge(self, edge: Tuple[int, ...]) -> bool:

        vtxs_in_order = sorted(edge)
        assert len(vtxs_in_order) == self.k, "The edge must have k vertices"
        for i in range(len(vtxs_in_order) - 1):
            assert vtxs_in_order[i] != vtxs_in_order[i + 1]

        h = hash(tuple(vtxs_in_order + [self.seed])) % 1e8
        return h < self.p * 1e8

    @cache
    def num_edges(self):
        return sum(self.degree(node) for node in tqdm.tqdm(range(self.n))) // self.k

    @cache
    def expected_num_edges(self):
        return self.p * binom(self.n, self.k)


class RandomPermutationHypergraph(RandomHypergraph):

    def __init__(self, n, k, m):
        super().__init__(n, k)
        self.m = m
        self.perm = RandomPermutation(binom(n, k),num_ciphers=1)
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
        permuted_idx = self.perm[self.get_edge_index(edge)]
        return permuted_idx < self.m

    def num_edges(self):
        return self.m


if __name__ == "__main__":
    G = RandomOracleGraph(10, 3, 0.5)
    print(G.num_edges())
    print(G.expected_num_edges())

    H = RandomPermutationHypergraph(10, 3, 60)
    print(H.num_edges())

    real_n_edges = 0
    for i, edge in enumerate(combinations(range(10), 3)):
        if H.is_edge(edge):
            real_n_edges += 1
        assert i == H.get_edge_index(edge)

    assert real_n_edges == H.num_edges()
