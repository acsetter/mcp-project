#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
from multiprocessing import shared_memory, Process, current_process, Queue
from queue import Empty, Full

from networkx import Graph
from color import color_order
import utils
import sys

sys.setrecursionlimit(10 ** 6)


class C_Max:
    def __init__(self, init=False):
        if init:
            self.shl = shared_memory.ShareableList([0], name="c_max")
        else:
            self.shl = shared_memory.ShareableList(name="c_max")

    def get(self):
        n = self.shl[0]
        return n

    def set(self, c_max):
        n = len(c_max)
        if n > self.shl[0]:
            self.shl[0] = n

    def close(self):
        self.shl.shm.close()

    def unlink(self):
        self.shl.shm.unlink()


class Idle:
    def __init__(self, size=None):
        if size is not None:
            a = [0] * size
            self.shl = shared_memory.ShareableList(a, name="threads")
        else:
            self.shl = shared_memory.ShareableList(name="threads")

    def set(self, pid: int, val: bool):
        self.shl[pid] = int(val)

    def any(self):
        try:
            return any(self.shl)
        except:
            return self.any()

    def all(self):
        try:
            return all(self.shl)
        except:
            return self.all()

    def close(self):
        self.shl.shm.close()

    def unlink(self):
        self.shl.shm.unlink()


def expand(g: Graph, task_queue: Queue, idle: Idle, c: set, p: set, c_max: C_Max, pop=False):
    """
    :param g: (Graph) a networkx graph
    :param task_queue: (Queue) queue to distribute work among threads
    :param c: (set) the candidate set of vertices
    :param p: (set) the set of unprocessed vertices
    :return: (None)
    """
    color, order = color_order(g, p)
    populate = True if pop and len(c) == 1 else False

    for i in range(len(p) - 1, -1, -1):

        if len(c) + color[i] > c_max.get():
            v = order[i]
            c = c.union({v})
            q = p.intersection(set(g.adj[v]))
            if len(q) == 0:
                if len(c) > c_max.get():
                    c_max.set(c)
            else:
                if not pop and idle.any() and task_queue.empty():
                    populate = True
                if populate:
                    try:
                        task_queue.put((c, q))
                    except Full:
                        expand(g, task_queue, idle, c, q, c_max)
                else:
                    expand(g, task_queue, idle, c, q, c_max)
            c = c - {v}
            p = p - {v}
        else:
            break


def work(g: Graph, task_queue: Queue):
    """
    The work of a single processes treated as a worker thread.
    :param g: (Graph) a networkx graph
    :param task_queue: (Queue) queue to distribute work among threads
    :return: (None)
    """
    c_max, idle = C_Max(), Idle()
    pid = int(current_process().name)
    flag, init = True, True

    while init or not idle.all() or not task_queue.empty():
        if init:
            flag, init = False, False
            if pid == 0:  # first process is the populating 'thread'
                expand(g, task_queue, idle, set(), set(g.nodes), c_max, pop=True)

        while not task_queue.empty():
            if flag:
                idle.set(pid, False)
                flag = False
            try:
                c, p = task_queue.get(block=False)
                # print(c_max.get())
                expand(g, task_queue, idle, c, p, c_max)
            except Empty:
                continue

        if not flag:
            flag = True
            idle.set(pid, True)

    c_max.close()
    idle.close()


def par_max_clique(g: Graph, num_processes: int):
    """
    A python-friendly (naive) implementation of McCreesh and Prosser's parallel max clique algorithm
    as presented in 'doi:10.3390/a6040618'. This is a dynamic branch and bound algorithm that uses a
    greedy coloring heuristic to reduce the search space. NOTE: Bitset encodings of graph and vertices
    are omitted in this implementation as well as shared memory optimizations.
    :param g: (Graph) a networkx graph
    :param num_processes: (int) the number of concurrent processes to run
    :return: (set) the maximum clique of graph 'g'
    """
    c_max, idle = C_Max(init=True), Idle(size=num_processes)
    task_queue = Queue()
    workers = []

    for i in range(num_processes):
        worker = Process(target=work, args=(g, task_queue), name=str(i))
        worker.start()
        workers.append(worker)

    [w.join() for w in workers]

    result = c_max.get()
    c_max.unlink()
    idle.unlink()

    return result


def test():
    graph = utils.read_dimacs_graph("in/miles250.col")
    assert par_max_clique(graph, 1) == len({'116', '53', '30', '10', '38', '113', '20', '24'})

    graph = utils.read_dimacs_graph("in/huck.col")
    assert par_max_clique(graph, 2) == len({'55', '11', '59', '49', '1', '50', '5', '25', '29', '13', '40'})

    graph = utils.read_dimacs_graph("in/anna.col")
    assert par_max_clique(graph, 3) == len({'36', '81', '116', '91', '135', '136', '74', '7', '18', '138', '99'})

    graph = utils.read_dimacs_graph("in/homer.col")
    assert par_max_clique(graph, 4) == {'452', '114', '189', '285', '353', '381', '491', '277', '387', '64', '549',
                                        '545', '314'}


if __name__ == "__main__":
    test()
