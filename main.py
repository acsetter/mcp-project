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

sys.setrecursionlimit(10**6)


@utils.timing
def run_seq_mca(g: nx.Graph):
    return seq_max_clique(g)


@utils.timing
def run_par_mca(g: nx.Graph, num_processes: int):
    return par_max_clique(g, num_processes)


def run_test(file_path, num_processes=(2, 4, 6, 8, 10), status=True, seq=True):
    g = utils.read_dimacs_graph(file_path)
    if status:
        utils.print_graph_info(g)
    data = utils.fetch_graph_info(g)
    if seq:
        if status:
            print("Running sequential...")
        seq_t = run_seq_mca(g)
        if status:
            print(f"...took {seq_t[1]} seconds.\n")
        data["Max Clique"] = seq_t[0]
        data["Seq Time"] = seq_t[1]
    for i in num_processes:
        if status:
            print(f"Running parallel using {i} processes...")
        data[i] = run_par_mca(g, i)[1]
        if status:
            print(f"...took {data[i]} seconds.\n")

    return data


def main() -> None:
    """
    Main entry point of program.
    """
    res = run_test("in/p_hat300-3.col")
    utils.print_test_results(res)
    utils.log_results(res)


if __name__ == '__main__':
    main()
