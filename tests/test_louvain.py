# -*- coding: utf-8 -*-
"""A test unit for Louvain Detector
"""

import unittest
import networkx as nx
from pyncd.models.louvain import LouvainDetector


class TestLouvain(unittest.TestCase):
    def setUp(self) -> None:
        self.resolution = 1
        self.threshold = 0.0000001
        self.random_state = 123

        self.graph = nx.petersen_graph()
        self.nodes = [node for node in self.graph.nodes()]
        self.detector = LouvainDetector(self.resolution, self.threshold, self.random_state)
        self.detector.fit(self.graph)

    def test_parameters(self):
        assert (hasattr(self.detector, "decision_com_graph_") and
                self.detector.decision_com_graph_ is not None)
        assert (hasattr(self.detector, "decision_com_num_") and
                self.detector.decision_com_num_ is not None)
        assert (hasattr(self.detector, "decision_com_node2com_") and
                self.detector.decision_com_node2com_)

    def test_decision_function(self):
        node_com = self.detector.decision_function(self.nodes)
        assert len(node_com) == len(self.nodes)

    def test_gen_partition(self):
        for graph, inner_partition in self.detector.gen_partition(self.graph):
            assert len(graph) == len(inner_partition)

    def test_one_level(self):
        partition = [{u} for u in self.graph.nodes()]

        partition, inner_partition, improvement = self.detector.one_level(
            self.graph, self.graph.size(weight="weight"), partition,
            "weight", self.resolution, self.graph.is_directed()
        )

        assert isinstance(improvement, bool)
        assert len(partition) == len(inner_partition)

    def tearDown(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
