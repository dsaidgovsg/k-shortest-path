import networkx as nx
import numpy as np

from kspath.deviation_path.mps import SingleTargetDeviationPathAlgorithm


def compute_path_weight(G, weight, path):
    """Returns the distance/weight of a path.

    Parameters
    ----------
        G : networkx.DiGraph
            The graph to compute weight of the path

        weight : str | unicode
            weight attribute in the `graph`

        path : list[str | unicode]
            The list of nodes representing the path

    Returns
    -------
        : float
    """
    return np.sum([G[src][dst][weight]
                   for src, dst in zip(path[:-1], path[1:])])


class ClusteredPaths(object):
    """Stores clusters (with same weight) of paths.
    Assume paths are added in non-increasing weight order.
    Allows one to compare two clusters of paths.
    """
    def __init__(self, G, weight='weight'):
        """
        Parameters
        ----------
            G : networkx.DiGraph

            weight : str | unicode
        """
        self._clustered_paths = []
        self._previous_path_weight = None
        self._paths_with_same_weight = set()
        self._graph = G
        self._weight = weight

    def add(self, path):
        """Add a path.

        Parameters
        ----------
            path : list[str | unicode]
        """
        path_weight = compute_path_weight(G=self._graph,
                                          weight=self._weight,
                                          path=path)

        should_add_path_to_current_set = (
            self._previous_path_weight is None
            or round(abs(path_weight - self._previous_path_weight), 10) == 0.0
        )
        if should_add_path_to_current_set:
            self._paths_with_same_weight.add(tuple(path))
        else:
            if self._paths_with_same_weight:
                self._clustered_paths.append(self._paths_with_same_weight)
            self._paths_with_same_weight = {tuple(path)}
        self._previous_path_weight = path_weight

    def __len__(self):
        return len(self._clustered_paths)

    def __ne__(self, other):
        return not self == other

    def __eq__(self, other):
        """Checks whether self._clustered_paths is exactly the same as
        other._clustered_paths.
        """
        if len(self._clustered_paths) != len(other._clustered_paths):
            return False
        else:
            for s1, s2 in zip(self._clustered_paths, other._clustered_paths):
                if s1 != s2:
                    return False
        return True


def lock_print(message, lock=None):
    """Locks and then prints if lock is not None, else prints.

    Parameters
    ----------
        message : str | unicode

        lock : multiprocessing.Lock | None
    """
    if lock is not None:
        lock.acquire()
    print(message)
    if lock is not None:
        lock.release()


def check_dpa_mps_implementation(index_to_dst_srcs_dict,
                                 G,
                                 indices,
                                 num_paths_to_test,
                                 lock=None,
                                 test_assert=False):
    """Tests the implementation (includes Yen's algorithm if there are
    too many deviations) of the deviation path algorithm by Martins, Pascoal
    and Santos with Yen's algorithm. Prints source and target if the
    paths differs. Can be used with multiprocessing as well as for pytest (
    single process)

    Parameters
    ----------
        index_to_dst_srcs_dict : dict[int,
                                      dict[str|unicode, list[str|unicode]]]
            A dict mapping an integer index to another dict mapping a target
            to a list of sources, e.g.,
            {
                0 : {
                    "15100" : ["25100", "35100"]
                }
            }

        G : networkx.DiGraph
            The graph of interest to find k shortest paths.

        indices : list[int]
            The indices/keys of `index_to_dst_srcs_dict` to process.

        num_paths_to_test : int
            The number of paths to test

        lock : multiprocessing.Lock | None
            If None, there is no multiprocessing, and therefore no need to
            lock when printing.

        test_assert : boolean
            If True, make assertions for pytest
    """
    for index in indices:
        # when include_source_destination is False
        if index not in index_to_dst_srcs_dict:
            continue
        target = list(index_to_dst_srcs_dict[index].keys())[0]
        try:
            dpa_mps_mcc500 = (SingleTargetDeviationPathAlgorithm
                              .create_from_graph(G=G,
                                                 target=target,
                                                 weight='weight',
                                                 max_consecutive_cycles=500))
        except:
            msg = "Index : {} | Unable to process target : {}".format(
                index, target
            )
            lock_print(msg, lock)
            continue

        sources = index_to_dst_srcs_dict[index][target]
        for source in sources:
            k_shortest_paths_dpa_mps_mcc500 = ClusteredPaths(G=G,
                                                             weight='weight')
            try:
                shortest_simple_paths_iter = (
                    dpa_mps_mcc500.shortest_simple_paths(source=source)
                )
                for path_index, path in enumerate(shortest_simple_paths_iter):
                    k_shortest_paths_dpa_mps_mcc500.add(path)
                    if path_index == num_paths_to_test:
                        break
            except:
                pass

            k_shortest_paths_yen = ClusteredPaths(G=G,
                                                  weight='weight')
            try:
                shortest_simple_paths_iter = nx.shortest_simple_paths(
                    G=G,
                    source=source,
                    target=target,
                    weight='weight'
                )
                for path_index, path in enumerate(shortest_simple_paths_iter):
                    k_shortest_paths_yen.add(path)
                    if path_index == num_paths_to_test:
                        break
            except:
                pass

            msg = "Index : {} | Source : {} -> Target : {}".format(
                index,
                source,
                target
            )
            if test_assert:
                assert (
                    k_shortest_paths_dpa_mps_mcc500 == k_shortest_paths_yen, msg
                )
            elif k_shortest_paths_dpa_mps_mcc500 != k_shortest_paths_yen:
                lock_print(msg, lock)

        msg = "Completed index : {}".format(index)
        lock_print(msg, lock)
