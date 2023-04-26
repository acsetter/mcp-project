#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
import copy
import datetime
import time
import networkx as nx
import csv
from os import listdir, mkdir, remove
from os.path import exists


def timing(f):
    """
    Wraps a function in a timer and returns the function's return value and the time it
    took to execute the function in seconds. Source: https://github.com/donfaq/max_clique
    :param f: a function annotated with `@timing`
    :return: (func, float) return value of f, execution time of f
    """
    def wrap(*args):
        t1 = time.perf_counter()
        fn = f(*args)
        t2 = time.perf_counter()
        return fn, t2 - t1
    return wrap


def read_dimacs_graph(file_path: str, name="", verbose=False) -> nx.Graph:
    """
    Parse .col file and return graph object
    :param name: (Str) the name of the graph.
    :param verbose: (bool) whether to print .col file info or not.
    :param file_path: (Str) path to the .col
    :return: (nx.graph) the graph built from expected file path.
    """
    if name == "":
        start = max(file_path.rfind('/'), file_path.rfind('\\')) + 1
        name = file_path[start:file_path.rfind('.')]
    edges = []
    ext = file_path.endswith('mtx')
    with open(file_path, 'r') as file:
        if file_path.endswith('mtx'):
            lines = file.readlines()[2:]
            for line in lines:
                v1, v2 = line.split()
                edges.append((v1, v2))
        elif file_path.endswith('col'):
            for line in file:
                if verbose and line.startswith(('c', 'p')):
                    print(line[2:].strip())

                if line.startswith('e'):
                    _, v1, v2 = line.split()
                    edges.append((v1, v2))
        else:
            raise ValueError("Filetype not supported.")

        return nx.Graph(edges, name=name)


def graph_max_degree(g: nx.Graph):
    return sorted(nx.degree(g), key=lambda x: x[1])[-1][1]


def fetch_graph_info(g: nx.Graph, printable=False) -> dict:
    nodes = sorted(nx.degree(g), key=lambda x: x[1])
    w_space = '   ' if printable else ''
    return {
        "Graph Name": g.name,
        "# Vertices": g.number_of_nodes(),
        f"# Edges{w_space}": g.number_of_edges(),
        f"Density{w_space}": nx.density(g),
        "Avg Degree": sum([x[1] for x in nodes]) / len(nodes),
        "Max Degree": nodes[-1][1],
        "Min Degree": nodes[0][1],
        "# Isolated": [x[1] for x in nodes].count(0)
    }


def print_graph_info(g: nx.Graph):
    # nodes = sorted(nx.degree(g), key=lambda x: x[1])
    g_info = fetch_graph_info(g, printable=True)
    p_str = ""

    for key in g_info.keys():
        p_str += f"{key}\t{g_info[key]}\n"

    print(p_str)


def print_test_results(results: dict):
    s = ""
    for key in results.keys():
        s += f"{key}\t{results[key]}\n"

    print(s)


def log_results(results: dict, file_path="results.csv"):
    mode = "a+"
    if not exists(f"./{file_path}"):
        mode = "w+"
    with open(file_path, mode, newline='') as f:
        writer = csv.writer(f)
        if mode == "w+":
            writer.writerow(results.keys())
        writer.writerow(results.values())


if __name__ == '__main__':
    pass
