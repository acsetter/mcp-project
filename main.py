#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
import sys
import time
import networkx as nx

from sequential import seq_max_clique
# sys.setrecursionlimit(10**6)


def timing(f):
    """
    Wraps a function in a timer and returns the function's return value and the time it
    took to execute the function in seconds. Source: https://github.com/donfaq/max_clique
    :param f: a function annotated with `@timing`
    :return: (func, float) return value of f, and execution time of f
    """
    def wrap(*args):
        t1 = time.perf_counter()
        fn = f(*args)
        t2 = time.perf_counter()
        return fn, t2 - t1
    return wrap


@timing
def run_seq_mca(g: nx.Graph):
    return seq_max_clique(g)


def read_dimacs_graph(file_path: str) -> nx.Graph:
    """
    Parse .col file and return graph object
    Source: https://github.com/donfaq/max_clique
    :param file_path: (Str) path to the .col
    :return: (nx.graph) the graph built from expected file path.
    """
    edges = []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('c'):  # graph description
                print(*line.split()[1:])
            # first line: p name num_of_vertices num_of_edges
            elif line.startswith('p'):
                p, name, vertices_num, edges_num = line.split()
                print('{0} {1} {2}'.format(name, vertices_num, edges_num))
            elif line.startswith('e'):
                _, v1, v2 = line.split()
                edges.append((v1, v2))
            else:
                continue
        return nx.Graph(edges)


def main() -> None:
    """
    Main entry point of program.
    """
    sys_args = sys.argv
    num_args = len(sys_args)

    graph = read_dimacs_graph("samples\le450_5a.col")
    r, t = run_seq_mca(graph)
    print(f"{len(r)} took {(t*1000):.3f} ms")


if __name__ == '__main__':
    main()
