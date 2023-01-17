# -*- coding: utf-8 -*-
"""Near linear time algorithm to detect community structures in large-scale networks (LPA)
Reference implementation: https://github.com/networkx/networkx/blob/main/networkx/algorithms/community/label_propagation.py
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause

import networkx as nx
import random
from collections import Counter, defaultdict
from networkx.convert import from_dict_of_lists
from networkx.utils import groups
from pyncd.models.base import BaseDetector
from pyncd.utils.converter import convert_multigraph
from pyncd.utils.tools import color_network, check_is_fitted
from typing import Any, Union, List, Dict, Set


class LPADetector(BaseDetector):
    """Wrapper of networkx Label Propagation with more functionalities.

    The Label Propagation algorithm (LPA) is a fast algorithm for finding communities in a graph.
    It detects these communities using network structure alone as its guide, and doesn’t require
    a pre-defined objective function or prior information about the communities.

    LPA works by propagating labels throughout the network and forming communities based
    on this process of label propagation.

    Parameters
    ----------
    async_type : str, default="async", ["async", "semi"]
        If "async", each node is updated without waiting for updates on the remaining nodes.
        If "semi", using a semi-synchronous label propagation method. This method combines the
        advantages of both the synchronous and asynchronous models. Not implemented for directed graphs.
    alpha : float, default=1.0
        The parameter of the node's out edge, which takes effect in a directed graph.
    beta : float, default=1.0
        The parameter of the node's in edge, which takes effect in a directed graph.
    random_state： int, default=123
        the seed used by the random
    """

    def __init__(self, async_type: str = "async", alpha: float = 1.0, beta: float = 1.0, random_state: int = 123):
        super(LPADetector, self).__init__()
        self.async_type = async_type
        self.alpha = alpha
        self.beta = beta
        self.random_state = random_state
        random.seed(random_state)

        self.decision_com_graph_ = None
        self.decision_com_num_ = None
        self.decision_com_node2com_ = None

    def fit(self, graph: nx.Graph, weight: Union[str, None] = "weight") -> object:
        """Fit detector. Find the best partition of a graph using the Label Propagation Community Detection Algorithm.

        Parameters
        ----------
        graph : NetworkX Graph or DiGraph
            The graph from which to detect communities
        weight : string or None, optional (default="weight")
            The name of an edge attribute that holds the numerical value
            used as a weight. If None then each edge has weight 1.

        Returns
        -------
        self : object
            Fitted detector.

        Notes
        -----
        The order in which the nodes are considered can affect the final output. In the algorithm
        the ordering happens using a random shuffle.
        """
        is_directed = graph.is_directed()
        if graph.is_multigraph():
            new_graph = convert_multigraph(graph, weight, is_directed)
        else:
            new_graph = graph.__class__()
            new_graph.add_nodes_from(graph)
            new_graph.add_weighted_edges_from(
                graph.edges(data=weight, default=1))

        if self.async_type == "async":
            labels = self.async_lpa(new_graph, weight)
        elif self.async_type == "semi":
            labels = self.semi_async_lpa(new_graph, weight)
        else:
            raise NotImplementedError(f"`{self.async_type}` is not implemented")

        self.decision_com_num_ = len(set(labels.values()))
        self.decision_com_node2com_ = labels
        self.decision_com_graph_ = from_dict_of_lists(groups(labels))

        return self

    def decision_function(self, nodes: List[Any]) -> List[Any]:
        """Estimate partition of nodes using the fitted detector

        Parameters
        ----------
        nodes : The input nodes.

        Returns
        -------
        partitions : The communities index of the input nodes.
        Examples
        --------
        >>> import networkx as nx
        >>> from pyncd.models.label_propagation import LPADetector
        >>> G = nx.tutte_graph()
        >>> detector = LPADetector()
        >>> detector.fit(G)
        >>> detector.decision_function([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        [1, 1, 10, 1, 1, 29, 27, 8, 8, 10]
        """
        check_is_fitted(self, ["decision_com_graph_", "decision_com_num_", "decision_com_node2com_"])
        return [self.decision_com_node2com_[node] for node in nodes]

    def async_lpa(self, graph: nx.Graph, weight: Union[str, None] = "weight") -> Dict[Any, int]:
        """Returns communities in `G` as detected by asynchronous label propagation.

        The algorithm proceeds as follows. After initializing each node with
        a unique label, the algorithm repeatedly sets the label of a node to
        be the label that appears most frequently among that nodes
        neighbors. The algorithm halts when each node has the label that
        appears most frequently among its neighbors. The algorithm is
        asynchronous because each node is updated without waiting for
        updates on the remaining nodes.

        Parameters
        ----------
        graph : NetworkX Graph or DiGraph
            The graph from which to detect communities
        weight : string or None, optional (default="weight")
            The edge attribute representing the weight of an edge.
            If None, each edge is assumed to have weight one. In this
            algorithm, the weight of an edge is used in determining the
            frequency with which a label appears among the neighbors of a
            node: a higher weight means the label appears more often.

        Returns
        -------
        labels : A dict keyed by node to labels
        """
        labels = {n: i for i, n in enumerate(graph)}
        neighbours = self._get_neighbours_weight(graph, weight)
        cont = True

        while cont:
            cont = False
            nodes = list(graph)

            for node in nodes:
                best_labels = self.most_frequent_labels(node, labels, neighbours)

                # If the node does not have one of the maximum frequency labels,
                # randomly choose one of them and update the node's label.
                # Continue the iteration as long as at least one node
                # doesn't have a maximum frequency label.
                if labels[node] not in best_labels:
                    labels[node] = random.choice(list(best_labels))
                    cont = True

        return labels

    def semi_async_lpa(self, graph: nx.Graph, weight: Union[str, None] = "weight"):
        """Generates community sets determined by label propagation

        Finds communities in `graph` using a semi-synchronous label propagation
        method. This method combines the advantages of both the synchronous
        and asynchronous models.

        Parameters
        ----------
        graph : NetworkX Graph or DiGraph
            The graph from which to detect communities
        weight : string or None, optional (default="weight")
            The edge attribute representing the weight of an edge.
            If None, each edge is assumed to have weight one. In this
            algorithm, the weight of an edge is used in determining the
            frequency with which a label appears among the neighbors of a
            node: a higher weight means the label appears more often.

        Returns
        -------
        labels : A dict keyed by node to labels
        """
        coloring = color_network(graph)
        neighbours = self._get_neighbours_weight(graph, weight)

        # Create a unique label for each node in the graph
        labels = {v: k for k, v in enumerate(graph)}
        while not self._labeling_complete(labels, neighbours):
            # Update the labels of every node with the same color.
            for color, nodes in coloring.items():
                for n in nodes:
                    self._update_label(n, labels, neighbours)

        return labels

    def _labeling_complete(self,
                           labels: Dict[Any, int],
                           neighbours: Dict[Any, Dict[Any, float]]) -> bool:
        """Determines whether or not LPA is done.

        Label propagation is complete when all nodes have a label that is
        in the set of highest frequency labels amongst its neighbors.
        Nodes with no neighbors are considered complete.

        Parameters
        ----------
        labels : a dict keyed by node to labels
        neighbours : The edge weight dict of the neighbor node.

        Returns
        -------
        Whether the LPA is done
        """
        return all(
            labels[v] in self.most_frequent_labels(
                v, labels, neighbours) for v in neighbours.keys() if len(neighbours[v]) > 0
        )

    @staticmethod
    def most_frequent_labels(
            node: Any,
            labels: Dict[Any, int],
            neighbours: Dict[Any, Dict[Any, float]]) -> Set[int]:
        """Returns a set of all labels with maximum frequency in `labels`.
        Input `labels` should be a dict keyed by node to labels.

        Parameters
        ----------
        node : node in 'graph'
        labels : A dict keyed by node to labels.
        neighbours : The edge weight dict of the neighbor node.

        Returns
        -------
        A set of all labels with maximum frequency in `labels`.
        """
        if not neighbours[node]:
            # Nodes with no neighbors are themselves a community and are labeled
            # accordingly, hence the immediate if statement.
            return {labels[node]}

        # Compute the frequencies of all neighbours of node
        label_freq = defaultdict(float)
        for n, wt in neighbours[node].items():
            label_freq[labels[n]] += wt

        max_freq = max(label_freq.values())
        return {label for label, freq in label_freq.items() if freq == max_freq}

    def _update_label(self,
                      node: Any,
                      labels: Dict[Any, int],
                      neighbours: Dict[Any, Dict[Any, float]]) -> None:
        """Updates the label of a node using the Prec-Max tie breaking algorithm

        The algorithm is explained in: 'Community Detection via Semi-Synchronous
        Label Propagation Algorithms' Cordasco and Gargano, 2011

        Parameters
        ----------
        node : node in 'graph'
        labels : A dict keyed by node to labels
        neighbours : The edge weight dict of the neighbor node.
        """
        high_labels = self.most_frequent_labels(node, labels, neighbours)
        if len(high_labels) == 1:
            labels[node] = high_labels.pop()
        elif len(high_labels) > 1:
            # Prec-Max
            if labels[node] not in high_labels:
                labels[node] = max(high_labels)

    def _get_neighbours_weight(self,
                               graph: nx.Graph,
                               weight: Union[str, None] = "weight") -> Dict[Any, Dict[Any, float]]:
        """Gets the weight dict for the edges in the graph.

        Parameters
        ----------
        graph : NetworkX Graph or DiGraph
        weight : string or None, optional (default="weight")
            The edge attribute representing the weight of an edge.
            If None, each edge is assumed to have weight one. In this
            algorithm, the weight of an edge is used in determining the
            frequency with which a label appears among the neighbors of a
            node: a higher weight means the label appears more often.

        Returns
        -------
        neighbours : The edge weight dict of the neighbor node
        """
        if graph.is_directed():
            neighbours = {}
            for node in graph:
                neighbours[node] = defaultdict(float)
                for _, n, wt in graph.out_edges(node, data=weight):
                    neighbours[node][n] += wt * self.beta if wt else self.beta
                for n, _, wt in graph.in_edges(node, data=weight):
                    neighbours[node][n] += wt * self.alpha if wt else self.alpha
        else:
            neighbours = {
                node: {v: data.get(weight, 1) for v, data in graph[node].items() if v != node} for node in graph
            }

        return neighbours
