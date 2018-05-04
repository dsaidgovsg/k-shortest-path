"""
Martins, Pascoal and Santos deviation path algorithm.
"""

from heapq import heappush, heappop
from itertools import count

import networkx as nx


# Modified from networkx/algorithms/simple_paths.py:
class PathBuffer(object):
    """Heap priority queue to add and remove paths in sorted order
    """
    def __init__(self):
        self._paths = set()
        self._sorted_paths = list()
        self._counter = count()

    def __len__(self):
        return len(self._sorted_paths)

    def push(self, cost, path, deviation_index, deviation_path_cost):
        """Adds relevant info for a path to the priority queue.

            Parameters
            ----------
                cost : float
                    Cost of the path

                path : list[str | int]
                    Nodes of the path

                deviation_index : int

                deviation_path_cost : float
        """
        hashable_path = tuple(path)
        if hashable_path not in self._paths:
            heappush(self._sorted_paths, (cost,
                                          next(self._counter),
                                          path,
                                          deviation_index,
                                          deviation_path_cost))
            self._paths.add(hashable_path)

    def pop(self):
        """Returns relevant info for a path from the priority queue.

            Returns
            -------
                (cost,
                 path,
                 deviation_index,
                 deviation_path) : tuple[float, tuple[str | int], int, float]
        """
        (cost, _, path, deviation_index, deviation_path_cost) = heappop(
            self._sorted_paths
        )
        self._paths.remove(tuple(path))
        return cost, path, deviation_index, deviation_path_cost


class SingleTargetDeviationPathAlgorithm(object):
    """Implements the deviation path algorithm in "A New Algorithm for
    Ranking Loopless Paths" by E.Q. Martins, M.M. Pascoal and J.L. Santos,
    Research Report, CISUC, May 1997.

    The target node is fixed but we may determine the K shortest simple
    paths for any source nodes. This reduces the number of times the
    dijkstra's algorithm is called.

    We also modify the algorithm to use Yen's algorithm if too many deviation
    paths are searched without finding a simple path. This modification seems
    to run slightly faster.
    """
    def __init__(self,
                 G,
                 G_reverse,
                 target,
                 weight='weight',
                 max_consecutive_cycles=500):
        """Input Parameters

        Parameters
        ----------
            G : networkx.DiGraph
                The directed network graph

            G_reverse : networkx.DiGraph
                The directed network graph with edges of `graph` reversed

            target : str
                The fixed target to determine the K shortest simple paths

            weight : str
                The key attribute of `graph` and `graph_reverse` indicating
                the weight of an edge

            max_consecutive_cycles : int
                Maximum number of deviation paths to search for a simple path
                before reverting to Yen's algorithm. Set to None or negative
                value if one wants to search for an unlimited number of
                deviation paths.
        """
        if target not in G:
            raise nx.NodeNotFound('target node %s not in graph' % target)

        dist, paths = nx.single_source_dijkstra(G_reverse, target)
        for node in paths:
            paths[node] = paths[node][::-1]

        self.target = target
        self.graph = G
        self._graph_reverse = G_reverse
        self._dist = dist
        self._paths = paths
        self._sorted_arcs = {}
        self._max_consecutive_cycles = max_consecutive_cycles
        self._weight = weight

    @classmethod
    def create_from_graph(cls,
                          G,
                          target,
                          weight='weight',
                          max_consecutive_cycles=500):
        """Creates graph and graph_reverse from G with
        only `weight` attribute.
        """
        graph = nx.DiGraph()
        for src, dst, data in G.edges(data=True):
            if weight is None:
                graph.add_edge(src, dst, weight=1.0)
            else:
                graph.add_edge(src, dst, weight=data[weight])

        graph_reverse = graph.reverse()

        if weight is None:
            weight = 'weight'
        return cls(
            graph, graph_reverse, target, weight, max_consecutive_cycles
        )

    def _update_sorted_arcs(self, tail_node):
        """Updates _sorted_arcs dict."""
        tail_node_to_target_dist = self._dist[tail_node]
        cost_head_node_list = []  # list to store (cost, head_node) tuple
        best_head_node = self._paths[tail_node][1]

        for head_node in self.graph[tail_node]:
            if head_node in self._dist:
                cost = (
                    self._dist[head_node]
                    - tail_node_to_target_dist
                    + self.graph[tail_node][head_node]['weight']
                )
                cost_head_node_list.append((cost, head_node))
        cost_head_node_list.sort()

        head_node_to_index = {}
        for index, (cost, head_node) in enumerate(cost_head_node_list):
            # swap if the current head node is in the best path
            if head_node == best_head_node and index != 0:
                cost_head_node_1 = cost_head_node_list[0]
                cost_head_node_list[0] = (cost, head_node)
                cost_head_node_list[index] = cost_head_node_1
                head_node_to_index[head_node] = 0
                head_node_to_index[cost_head_node_1[1]] = index
            else:
                head_node_to_index[head_node] = index

        self._sorted_arcs[tail_node] = {
            'cost_head_node_list': cost_head_node_list,
            'head_node_to_index': head_node_to_index
        }

    def mps_deviation_paths(self,
                            path_cost,
                            path,
                            deviation_index,
                            deviation_path_cost,
                            list_x):
        """Implementation for Martins, Pascoal and Santos (MPS) deviation
        path algorithm.
        """
        for i in range(deviation_index, len(path) - 1):
            v_i = path[i]
            v_j = path[i + 1]
            root_path = path[:i + 1]
            root_path_nodes = set(root_path)

            # add a simple check to stop search for deviation paths
            # if there is only one path from deviation node to target node
            no_other_path = True
            for node in path[-1:i:-1]:
                if len(self._graph_reverse[node]) > 1:
                    no_other_path = False
                    break
            if no_other_path:
                break

            # check for cycles
            if len(root_path_nodes) < len(root_path):
                break

            if v_i not in self._sorted_arcs:
                self._update_sorted_arcs(v_i)

            vj_index = self._sorted_arcs[v_i]['head_node_to_index'][v_j]
            cost_head_node_list = (
                self._sorted_arcs[v_i]['cost_head_node_list'][vj_index + 1:]
            )
            for cost, head_node in cost_head_node_list:
                if head_node not in root_path_nodes:
                    new_path = root_path + self._paths[head_node]
                    if i == deviation_index:
                        list_x.push(deviation_path_cost + cost,
                                    new_path,
                                    i,
                                    deviation_path_cost)
                    else:
                        list_x.push(path_cost + cost, new_path, i, path_cost)
                    break

    def _shortest_simple_paths(self, source):
        """Determines the K shortest simple paths from a source to self.target

        Parameters
        ----------
            source : str
                The source node of interest

        Yields
        ------
            path : list[str]
                List of nodes indicating the kth shortest simple path from
                source to self.target
        """
        # check that there is actually a path from source to self.target
        if source in self._paths:
            candidate_paths = PathBuffer()

            # first candidate path is the shortest path
            candidate_paths.push(cost=0.0,
                                 path=self._paths[source],
                                 deviation_index=0,
                                 deviation_path_cost=0.0)

            consecutive_cycles = 0
            simple_paths_found = set()
            max_consecutive_cycles_reached = None

            # check whether all candidate paths have been searched
            while candidate_paths:
                # search infinitely if max_consecutive_cycles is None or < 0
                # Yen's algorithm if self._max_consecutive_cycles == 0
                max_consecutive_cycles_reached = (
                    self._max_consecutive_cycles is not None
                    and 0 <= self._max_consecutive_cycles <= consecutive_cycles
                )

                if max_consecutive_cycles_reached:
                    break
                else:
                    path_cost, path, deviation_index, deviation_path_cost = (
                        candidate_paths.pop()
                    )

                    # check for no cycles
                    if len(set(path)) == len(path):
                        simple_paths_found.add(tuple(path))
                        yield path
                        consecutive_cycles = 0  # reset consecutive cycles to 0
                    else:
                        consecutive_cycles += 1

                    self.mps_deviation_paths(path_cost,
                                             path,
                                             deviation_index,
                                             deviation_path_cost,
                                             candidate_paths)

            if max_consecutive_cycles_reached:
                for path in nx.shortest_simple_paths(self.graph,
                                                     source,
                                                     self.target,
                                                     'weight'):
                    if tuple(path) not in simple_paths_found:
                        yield path

    def shortest_simple_paths(self, source):
        """Determines the K shortest simple paths from a source to self.target

        Parameters
        ----------
            source : str
                The source node of interest

        Returns
        ------
            : mps._shortest_simple_paths
                Generator object which yields the kth shortest simple path.

        Raises
        ------
            networkx.NodeNotFound : If source is not in graph
        """
        if source not in self.graph:
            raise nx.NodeNotFound('source node %s not in graph' % source)

        return self._shortest_simple_paths(source)
