import json
from os import path

from git import Repo
import networkx as nx
import pandas as pd
import pytest


# *slow* and *comprehensive* datasets are stored in a private repo
# and requires the right credentials to download
@pytest.mark.slow
@pytest.mark.comprehensive
@pytest.fixture(scope='module')
def test_graph_data():
    """fixture for comprehensive graph and test data
    """
    current_path = path.dirname(path.realpath(__file__))
    test_data_path = path.join(current_path, 'test-data')

    if not path.exists(test_data_path):
        Repo.clone_from("git@github.com:datagovsg/test-data.git",
                        test_data_path)
    graph_data = json.load(
        open(path.join(test_data_path, 'graph/test_graph.json'))
    )
    test_graph = nx.readwrite.json_graph.adjacency_graph(graph_data)

    test_source_target_pd = pd.read_csv(
        path.join(test_data_path, 'graph/test_source_target.csv')
    )
    test_source_target = zip(test_source_target_pd['source'],
                             test_source_target_pd['target'])

    return test_graph, test_source_target
