#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""

from networkx import Graph
from color import color_order
import utils


def seq_max_clique(g: Graph):
    """
    A python-friendly (naive) implementation of McCreesh and Prosser's sequential max clique algorithm
    as presented in 'doi:10.3390/a6040618'. This is a dynamic branch and bound algorithm that uses a
    greedy coloring heuristic to reduce the search space. NOTE: Bitset encodings of graph and vertices
    are omitted in this implementation.
    :param g: (Graph) a networkx graph
    :return: (set) the set of vertices that belong to the maximum clique of graph 'g'
    """
    def expand(c: set, p: set, c_max: set):
        """
        The recursive part of the algorithm
        :param c: (set) the candidate set of vertices
        :param p: (set) the set of unprocessed vertices
        :param c_max: (set) the current best candidate max clique
        :return: (set) the maximum clique of graph 'g'
        """
        color, order = color_order(g, p)
        for i in range(len(p) - 1, -1, -1):
            if len(c) + color[i] > len(c_max):
                v = order[i]
                c = c.union({v})
                q = p.intersection(set(g.adj[v]))

                if len(q) == 0:
                    if len(c) > len(c_max):
                        c_max = c
                else:
                    c_max = expand(c, q, c_max)
                c = c - {v}
                p = p - {v}
            else:
                break

        return c_max

    return expand(set(), set(g.nodes), set())


def test():
    graph = utils.read_dimacs_graph("in/miles250.col")
    assert seq_max_clique(graph) == {'116', '53', '30', '10', '38', '113', '20', '24'}

    graph = utils.read_dimacs_graph("in/huck.col")
    assert seq_max_clique(graph) == {'55', '11', '59', '49', '1', '50', '5', '25', '29', '13', '40'}

    graph = utils.read_dimacs_graph("in/anna.col")
    assert seq_max_clique(graph) == {'36', '81', '116', '91', '135', '136', '74', '7', '18', '138', '99'}

    graph = utils.read_dimacs_graph("in/homer.col")
    assert seq_max_clique(graph) == {'452', '114', '189', '285', '353', '381', '491', '277', '387', '64', '549', '545',
                                     '314'}


if __name__ == "__main__":
    test()
