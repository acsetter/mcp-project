#!/usr/bin/env python
"""
** CSC 532 Final Research Project **
Comparing Sequential and Parallel Algorithm Performance for Solving the Maximum Clique Problem
By: Aaron Csetter, Dmytro Dobryin, Ian Pena, and Nathan Davis
UNCW: Spring 2023
"""
import time
from multiprocessing import shared_memory, Lock, Process, current_process, Queue
from queue import Empty

from networkx import Graph
from color import color_order
import utils
import sys

c_max_lock = Lock()
idle_lock = Lock()
sys.setrecursionlimit(10 ** 6)


def init_c_max(size: int):
    """
    Initialize the shared_memory of c_max. Note: size should be set to
    the max_degree of graph g to ensure enough memory is allocated.
    :param size: (int) how large the initial value should be.
    :return:
    """
    a = [0]
    a += [None] * size
    return shared_memory.ShareableList(a, name="c_max")


def maybe_get_c_max(curr: set) -> set:
    if c_max_lock.acquire(block=False):
        shl = shared_memory.ShareableList(None, name="c_max")
        c_max = {shl[i] for i in range(1, shl[0] + 1)}
        c_max_lock.release()
        shl.shm.close()

        return c_max

    return curr


def get_c_max() -> set:
    """
    Get the shared_memory value of c_max
    :return: (set) the shared_memory value of c_max
    """
    shl = shared_memory.ShareableList(None, name="c_max")
    c_max_lock.acquire()
    c_max = {shl[i] for i in range(1, shl[0] + 1)}
    c_max_lock.release()
    shl.shm.close()

    return c_max


def set_c_max(c: set):
    """
    Set the shared_memory value of c_max.
    :param c: (set) new assignment of c_max
    :return: (None)
    """
    shl = shared_memory.ShareableList(None, name="c_max")
    n = len(c)
    c_max_lock.acquire()
    if n > shl[0]:
        d = c.copy()
        shl[0] = n
        for i in range(1, n + 1):
            shl[i] = d.pop()
    c_max_lock.release()
    shl.shm.close()



def init_idle_threads(num_processes: int):
    """
    Initialize the list of bools indicating the idle status of running processes.
    :param num_processes: (int) the number of concurrent processes running
    :return: (None)
    """
    a = [False] * num_processes
    return shared_memory.ShareableList(a, name="idle_threads")


def get_idle_threads() -> list:
    """
    Get idle status of threads as a list of bools.
    :return: (list) of bools indicating thread idle status
    """
    shl = shared_memory.ShareableList(name="idle_threads")
    idle_lock.acquire()
    a = [shl[i] == True for i in range(0, len(shl))]
    idle_lock.release()
    shl.shm.close()

    return a


def set_idle_threads(pid: int, b: bool):
    """
    Set whether a thread is idle or not.
    :param pid: (int) the id of thread assigned at start
    :param b: (bool) whether the thread is idle or not
    :return: (None)
    """
    shl = shared_memory.ShareableList(name="idle_threads")
    idle_lock.acquire()
    n = len(shl)
    if 0 <= pid < n:
        if shl[pid] != b:
            shl[pid] = b
    else:
        raise IndexError(f"pid out of range: 0 <= {id} < {n}")
    idle_lock.release()
    shl.shm.close()


def all_idle_threads() -> bool:
    v = False
    if idle_lock.acquire(block=False):
        v = True
        shl = shared_memory.ShareableList(name="idle_threads")
        for i in range(len(shl)):
            if not shl[i]:
                v = False
                break
        idle_lock.release()
        shl.shm.close()

    return v


def expand(g: Graph, queue: Queue, c: set, p: set, pop=False):
    """
    :param g: (Graph) a networkx graph
    :param queue: (Queue) queue to distribute work among threads
    :param c: (set) the candidate set of vertices
    :param p: (set) the set of unprocessed vertices
    :return: (None)
    """
    color, order = color_order(g, p)
    populate = True if pop and len(c) == 1 else False
    c_max = get_c_max()

    for i in range(len(p) - 1, -1, -1):
        if populate:
            c_max = get_c_max()

        if len(c) + color[i] > len(c_max):
            v = order[i]
            c = c.union({v})
            q = p.intersection(set(g.adj[v]))
            if len(q) == 0:
                c_max = get_c_max()
                if len(c) > len(c_max):
                    # print(c)
                    set_c_max(c)
            else:
                if not pop and any(get_idle_threads()) and queue.empty():
                    populate = True
                if populate and not queue.full():
                    queue.put((c, q))
                else:
                    expand(g, queue, c, q)
            c = c - {v}
            p = p - {v}
        else:
            continue


def work(g: Graph, queue: Queue):
    """
    The work of a single processes treated as a worker thread.
    :param g: (Graph) a networkx graph
    :param queue: (Queue) queue to distribute work among threads
    :param populating: (bool) whether the process should populate the queue on start
    :return: (None)
    """
    pid = int(current_process().name)
    flag = True
    if pid == 0:  # first process is the populating 'thread'
        expand(g, queue, set(), set(g.nodes), pop=True)
        set_idle_threads(pid, True)

    while flag or not queue.empty():
        if not queue.empty():
            set_idle_threads(pid, False)

        while not queue.empty():
            try:
                c, p = queue.get(block=False)
                # print(queue.qsize())
                expand(g, queue, c, p)
            except Empty:
                continue

        set_idle_threads(pid, True)
        flag = not all_idle_threads()
        # time.sleep(0.002)


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
    idle_threads = init_idle_threads(num_processes)  # must be assigned to a var
    cmax = init_c_max(utils.graph_max_degree(g))
    queue = Queue()
    workers = []

    for i in range(num_processes):
        worker = Process(target=work, args=(g, queue), name=str(i))
        worker.start()
        workers.append(worker)

    [w.join() for w in workers]
    idle_threads.shm.close()
    idle_threads.shm.unlink()

    res = {cmax[i] for i in range(1, cmax[0] + 1)}
    cmax.shm.close()
    cmax.shm.unlink()

    return res


def test():
    graph = utils.read_dimacs_graph("in/miles250.col")
    assert par_max_clique(graph, 1) == {'116', '53', '30', '10', '38', '113', '20', '24'}

    graph = utils.read_dimacs_graph("in/huck.col")
    assert par_max_clique(graph, 2) == {'55', '11', '59', '49', '1', '50', '5', '25', '29', '13', '40'}

    graph = utils.read_dimacs_graph("in/anna.col")
    assert par_max_clique(graph, 3) == {'36', '81', '116', '91', '135', '136', '74', '7', '18', '138', '99'}

    graph = utils.read_dimacs_graph("in/homer.col")
    assert par_max_clique(graph, 4) == {'452', '114', '189', '285', '353', '381', '491', '277', '387', '64', '549',
                                        '545', '314'}


if __name__ == "__main__":
    test()
