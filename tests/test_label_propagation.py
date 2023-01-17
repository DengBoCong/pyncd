# -*- coding: utf-8 -*-
"""A test unit for LPA Detector
"""

import unittest
import networkx as nx
from pyncd.models.label_propagation import LPADetector


class TestLPA(unittest.TestCase):
    def setUp(self) -> None:
        self.async_type = "async"
        self.alpha = 1.0
        self.beta = 1.0
        self.random_state = 123

        self.graph = nx.tutte_graph()
        self.nodes = [node for node in self.graph.nodes()]
        self.detector = LPADetector(self.async_type, self.alpha, self.beta, self.random_state)
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

    def test_async_lpa(self):
        res = self.detector.async_lpa(self.graph)
        assert len(res) == len(self.graph)
        assert len(set(res.values())) > 0

    def test_semi_async_lpa(self):
        res = self.detector.semi_async_lpa(self.graph)
        assert len(res) == len(self.graph)
        assert len(set(res.values())) > 0

    def test_most_frequent_labels(self):
        pass

    def tearDown(self) -> None:
        pass


if __name__ == "__main__":
    unittest.main()
