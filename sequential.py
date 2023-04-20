#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
from networkx import Graph
from color import color_order


def seq_max_clique(g: Graph):
    """
    A python-friendly (naive) implementation of McCreesh and Prosser's sequential max clique algorithm
    as presented in 'doi:10.3390/a6040618'. This is a dynamic branch and bound algorithm that uses a
    greedy coloring heuristic to reduce the search space. NOTE: Bitset encodings of graph and vertices
    are omitted in this implementation.
    :param g: (Graph) a networkx graph
    :return: (set) the set of vertices that belong to the maximum clique of graph 'g'
    """
    def expand(g: Graph, c: set, p: set, c_max: set):
        """
        The recursive part of the algorithm
        :param g: (Graph) a networkx graph
        :param c: (set) the candidate set of vertices
        :param p: (set) the set of unprocessed vertices
        :param c_max: (set) the current best candidate max clique
        :return: (set) the maximum clique of graph 'g'
        """
        color, order = color_order(g, p)
        # print(color, order)
        for i in range(len(p) - 1, -1, -1):
            # print(f"|c={c}| + color[i]={color[i]} > |c_max={c_max}|")
            if len(c) + color[i] > len(c_max):
                v = order[i]
                # print("v=", v)
                c = c.union({v})
                q = p.intersection(set(g.neighbors(v)))

                if len(q) == 0:
                    if len(c) > len(c_max):
                        # print(f"{c_max} unseated by {c}")
                        c_max = c
                else:
                    # c_max = max(c_max, expand(g, c, q, c_max), key=lambda x: len(x))
                    c_max = expand(g, c, q, c_max)
                c = c - {v}
                p = p - {v}

        return c_max

    return expand(g, set(), set(g.nodes), set())


def test():
    # TODO: implement testing of seq_max_clique
    pass


if __name__ == "__main__":
    test()
