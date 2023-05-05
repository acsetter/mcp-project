#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
import sys

import networkx as nx
import utils
from sequential import seq_max_clique
from parallel import par_max_clique

sys.setrecursionlimit(10 ** 6)


@utils.timing
def run_seq_mca(g: nx.Graph):
    return seq_max_clique(g)


@utils.timing
def run_par_mca(g: nx.Graph, num_processes: int):
    return par_max_clique(g, num_processes)


def run_par_test(file_path, num_processes=range(2, 13)):
    g = utils.read_dimacs_graph(file_path)
    utils.print_graph_info(g)
    for i in num_processes:
        print(f"Running parallel using {i} processes...")
        par = run_par_mca(g, i)
        print(f"...took {par[1]} seconds.\n")


def run_test(file_path, num_processes=range(2, 13), status=True):
    """

    :param file_path: (str)
    :param num_processes: (Iterable)
    :param status: (bool) whether to print status or not
    :return: (dict) results of the test.
    """
    g = utils.read_dimacs_graph(file_path)
    utils.print_graph_info(g)
    data = utils.fetch_graph_info(g)
    if status:
        print("Running sequential...")

    seq = run_seq_mca(g)
    if status:
        print(f"...took {seq[1]} seconds.\n")

    data["Max Clique"] = seq[0]
    data["Seq Time"] = seq[1]

    for i in num_processes:
        if status:
            print(f"Running parallel using {i} processes...")
        par = run_par_mca(g, i)
        data[i] = par[1]
        if par[0] != len(seq[0]):
            print(f"ERROR: Incorrect results:\n"
                  f"> SEQ   :\t{len(seq[0])}\n"
                  f"> PAR({i}):\t{par[0]}")
        if status:
            print(f"...took {data[i]} seconds.\n")

    return data


def main() -> None:
    """
    Main entry point of program.
    """
    # add any .col or .mtx graphs you wish to test to the list:
    graphs = [
        "in/C125.9.col",
        "in/brock200-1.mtx",  #
        "in/gen200_p0.9_44.col",
        "in/p_hat300-3.col",
    ]
    for graph in graphs:
        res = run_test(graph)
        utils.print_test_results(res)
        utils.log_results(res)  # results are stored in /results.csv


if __name__ == '__main__':
    main()
