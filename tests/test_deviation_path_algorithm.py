import networkx as nx
import pytest

from kspath.deviation_path.mps import (
    SingleTargetDeviationPathAlgorithm
)
from tests.utils import check_dpa_mps_implementation, compute_path_weight


@pytest.mark.fast
def test_target_node_not_found():
    G = nx.DiGraph()
    G.add_edge('a', 'b', weight=0.6)
    G.add_edge('a', 'c', weight=0.2)
    G.add_edge('c', 'd', weight=0.1)
    G.add_edge('c', 'e', weight=0.7)
    G.add_edge('c', 'f', weight=0.9)
    G.add_edge('a', 'd', weight=0.3)

    with pytest.raises(nx.NodeNotFound):
        SingleTargetDeviationPathAlgorithm.create_from_graph(
            G=G, target='z', weight='weight'
        )


@pytest.mark.fast
def test_source_node_not_found():
    G = nx.DiGraph()
    G.add_edge('a', 'b', weight=0.6)
    G.add_edge('a', 'c', weight=0.2)
    G.add_edge('c', 'd', weight=0.1)
    G.add_edge('c', 'e', weight=0.7)
    G.add_edge('c', 'f', weight=0.9)
    G.add_edge('a', 'd', weight=0.3)

    dpa_mps = SingleTargetDeviationPathAlgorithm.create_from_graph(
        G=G, target='d', weight='weight'
    )
    
    with pytest.raises(nx.NodeNotFound):
        dpa_mps.shortest_simple_paths(source='z')


@pytest.mark.fast
def test_deviation_path_fast():
    G = nx.DiGraph()

    G.add_edge(1, 3, weight=0)
    G.add_edge(1, 2, weight=0)
    G.add_edge(1, 4, weight=0)
    G.add_edge(2, 3, weight=1)
    G.add_edge(2, 4, weight=2)
    G.add_edge(3, 5, weight=2)
    G.add_edge(3, 6, weight=2)
    G.add_edge(4, 5, weight=1)
    G.add_edge(4, 6, weight=1)
    G.add_edge(5, 2, weight=1)
    G.add_edge(5, 6, weight=0)

    dpa_mps = (
        SingleTargetDeviationPathAlgorithm
        .create_from_graph(G=G, target=6, weight='weight')
    )

    for source in range(1, 6):
        assert (
            len(list(dpa_mps.shortest_simple_paths(source)))
            == len(list(nx.shortest_simple_paths(G, source, 6, 'weight')))
        )

        paths = {}
        for path in dpa_mps.shortest_simple_paths(source):
            dist = compute_path_weight(G=G, weight='weight', path=path)
            if dist not in paths:
                paths[dist] = {tuple(path)}
            else:
                paths[dist].add(tuple(path))

        for path in list(nx.shortest_simple_paths(G=G,
                                                  source=source,
                                                  target=6,
                                                  weight='weight')):
            assert tuple(path) in paths[compute_path_weight(G=G,
                                                            path=path,
                                                            weight='weight')]


@pytest.mark.slow
def test_deviation_path(test_graph_data):
    test_graph, _ = test_graph_data

    index_to_dst_srcs_dict = {
        0: {9: [20890]},
        1: {26: [5092]},
        2: {71: [20114]},
        3: {98: [24649]}
    }

    check_dpa_mps_implementation(
        index_to_dst_srcs_dict=index_to_dst_srcs_dict,
        G=test_graph,
        indices=[0, 1, 2, 3],
        num_paths_to_test=100,
        lock=None,
        test_assert=True
    )


@pytest.mark.comprehensive
def test_deviation_path_comprehensive(test_graph_data):
    test_graph, test_source_target = test_graph_data

    index = 0
    dst_to_index = {}
    index_to_dst_srcs_dict = {}
    for source, destination in test_source_target:
        # only include source and destination if the nodes can be found in
        # the graph and source is not destination
        include_source_destination = (
                source in test_graph
                and destination in test_graph
                and source != destination
        )

        if include_source_destination:
            if destination not in dst_to_index:
                dst_to_index[destination] = index
                index_to_dst_srcs_dict[dst_to_index[destination]] = {
                    destination: [source]
                }
                index += 1
            else:
                dst_index = dst_to_index[destination]
                index_to_dst_srcs_dict[dst_index][destination].append(source)

    check_dpa_mps_implementation(
        index_to_dst_srcs_dict=index_to_dst_srcs_dict,
        G=test_graph,
        indices=list(index_to_dst_srcs_dict.keys()),
        num_paths_to_test=100,
        lock=None,
        test_assert=True
    )
