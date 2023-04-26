#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""

import networkx as nx


def color_order(g: nx.Graph, P: set) -> (list, list):
    """
    Colors the expected set of vertices (P) of the expected graph (g) using
    a greedy coloring algorithm that processes each vertex of P in decreasing degree order.
    :param g: (nx.Graph) a networkx Graph that contains vertex set P
    :param P: (set) vertices that are a subset of graph 'g'.
    :return: (List, List) color of each vertex, the order of the vertices.
    """
    nodes = [node[0] for node in sorted(nx.degree(g, nbunch=P), key=lambda x: x[1])]
    color = []
    order = []
    k = 1
    while len(nodes) > 0:
        q = nodes.copy()
        while len(q) > 0:
            v = q.pop()
            nodes.remove(v)
            color.append(k)
            order.append(v)
            neighbors = g.adj[v]
            q = list(filter(lambda x: x not in neighbors, q))
        k += 1

    return color, order


def test():
    # TODO: Implement testing function of color_order
    pass


if __name__ == "__main__":
    test()
