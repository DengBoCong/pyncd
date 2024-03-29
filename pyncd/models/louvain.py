# -*- coding: utf-8 -*-
"""Fast unfolding of Communities in Large Networks (Louvain)
Reference implementation: https://github.com/networkx/networkx/blob/main/networkx/algorithms/community/louvain.py
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause


import networkx as nx
import random
from collections import defaultdict, deque
from networkx.algorithms.community import modularity
from pyncd.models.base import BaseDetector
from pyncd.utils.converter import convert_multigraph
from pyncd.utils.tools import check_is_fitted
from typing import Union, List, Set, Any, Tuple, Iterator


class LouvainDetector(BaseDetector):
    """Wrapper of networkx Louvain with more functionalities.

    Louvain Community Detection Algorithm is a simple method to extract the community
    structure of a network. This is a heuristic method based on modularity optimization.

    The partitions at each level (step of the algorithm) form a dendogram of communities.
    A dendrogram is a diagram representing a tree and each level represents
    a partition of the G graph. The top level contains the smallest communities
    and as you traverse to the bottom of the tree the communities get bigger
    and the overal modularity increases making the partition better.

    Each level is generated by executing the two phases of the Louvain Community
    Detection Algorithm.

    Parameters
    ----------
    resolution : float, optional (default=1)
        If resolution is less than 1, the algorithm favors larger communities.
        Greater than 1 favors smaller communities
    threshold : float, optional (default=0.0000001)
        Modularity gain threshold for each level. If the gain of modularity
        between 2 levels of the algorithm is less than the given threshold
        then the algorithm stops and returns the resulting communities.
    random_state： int, optional (default=123)
        the seed used by the random

    Attributes
    ----------
    decision_com_graph_ : Networkx Graph
        The graph of best communities.
        Each node represents one community and contains all the nodes that constitute it.
    decision_com_num_ : int
        The number of best communities
    decision_com_node2com_ : dict
        Mapping of nodes and best communities index.
    """

    def __init__(self, resolution: float = 1, threshold: float = 0.0000001, random_state: int = 123) -> None:
        super(LouvainDetector, self).__init__()
        self.resolution = resolution
        self.threshold = threshold
        self.random_state = random_state
        random.seed(random_state)

        self.decision_com_graph_ = None
        self.decision_com_num_ = None
        self.decision_com_node2com_ = None

    def fit(self, graph: nx.Graph, weight: Union[str, None] = "weight") -> object:
        """Fit detector. Find the best partition of a graph using the Louvain Community Detection Algorithm.

        Parameters
        ----------
        graph : NetworkX graph
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
        generator = self.gen_partition(graph, weight)
        queue = deque(generator, maxlen=1)
        self.decision_com_graph_ = queue.pop()[0]
        self.decision_com_num_ = len(self.decision_com_graph_)
        self.decision_com_node2com_ = {}
        for com, attr in self.decision_com_graph_.nodes(data=True):
            for node in attr["nodes"]:
                self.decision_com_node2com_[node] = com

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
        >>> from pyncd.models.louvain import LouvainDetector
        >>> G = nx.petersen_graph()
        >>> detector = LouvainDetector()
        >>> detector.fit(G)
        >>> detector.decision_function([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        [0, 1, 1, 1, 0, 0, 1, 0, 1, 0]
        """
        check_is_fitted(self, ["decision_com_graph_", "decision_com_num_", "decision_com_node2com_"])
        return [self.decision_com_node2com_[node] for node in nodes]

    def gen_partition(
            self,
            graph: nx.Graph,
            weight: Union[str, None] = "weight") -> Iterator[Tuple[nx.Graph, List[Set[Any]]]]:
        """Partition generator

        Parameters
        ----------
        graph : NetworkX graph
            The graph from which to detect communities
        weight : string or None, optional (default="weight")
            The name of an edge attribute that holds the numerical value
            used as a weight. If None then each edge has weight 1.

        Yields
        ------
        new_graph
            Each node represents one community and contains all the nodes that constitute it.
        inner_partition
            These node sets represent a partition of graph's nodes.
        """
        partition = [{u} for u in graph.nodes()]
        mod = modularity(graph, partition,
                         resolution=self.resolution, weight=weight)
        is_directed = graph.is_directed()
        if graph.is_multigraph():
            new_graph = convert_multigraph(graph, weight, is_directed)
        else:
            new_graph = graph.__class__()
            new_graph.add_nodes_from(graph)
            new_graph.add_weighted_edges_from(
                graph.edges(data=weight, default=1))

        m = new_graph.size(weight="weight")
        partition, inner_partition, improvement = self.one_level(
            new_graph, m, partition, "weight", self.resolution, is_directed
        )
        improvement = True
        while improvement:
            new_mod = modularity(
                new_graph, inner_partition, resolution=self.resolution
            )

            new_graph = self.gen_graph(new_graph, inner_partition)
            yield new_graph, inner_partition

            if new_mod - mod <= self.threshold:
                return
            mod = new_mod

            partition, inner_partition, improvement = self.one_level(
                new_graph, m, partition, "weight", self.resolution, is_directed
            )

    @staticmethod
    def one_level(
            graph: nx.Graph,
            graph_size: int,
            partition: List[Set[Any]],
            weight: Union[str, None] = None,
            resolution: float = 1,
            is_directed: bool = False) -> Tuple[List[Set[Any]], List[Set[Any]], bool]:
        """Calculate one level of the Louvain partitions tree

        Parameters
        ----------
        graph : NetworkX Graph or DiGraph
            The graph from which to detect communities
        graph_size : number
            The size of the graph `graph`.
        partition : list of sets of nodes
            A valid partition of the graph `graph`
        weight: string or None, optional (default=None)
            The name of an edge attribute that holds the numerical value used as a weight.
            If None, then each edge has weight 1.
            The degree is the sum of the edge weights adjacent to the node.
        resolution : positive number
            The resolution parameter for computing the modularity of a partition
        is_directed : bool
            True if `graph` is a directed graph.

        Returns
        -------
        partition
            A list of sets of nodes. A valid partition of the graph `graph` at the level.
        inner_partition
            A list of sets. These node sets represent a partition of graph's nodes.
        improvement
            Whether the modularity gain is obtained.
        """
        node2com = {node: i for i, node in enumerate(graph.nodes())}
        inner_partition = [{node} for node in graph.nodes()]
        if is_directed:
            in_degrees = dict(graph.in_degree(weight=weight))
            out_degrees = dict(graph.out_degree(weight=weight))
            stot_in = [deg for deg in in_degrees.values()]
            stot_out = [deg for deg in out_degrees.values()]
            # Calculate weights for both in and out neighbours
            neighbours = {}
            for node in graph:
                neighbours[node] = defaultdict(float)
                for _, n, wt in graph.out_edges(node, data=weight):
                    neighbours[node][n] += wt if wt else 1
                for n, _, wt in graph.in_edges(node, data=weight):
                    neighbours[node][n] += wt if wt else 1
        else:
            degrees = dict(graph.degree(weight=weight))
            stot = [deg for deg in degrees.values()]
            neighbours = {node: {v: data.get(
                weight, 1) for v, data in graph[node].items() if v != node} for node in graph}
        rand_nodes = list(graph.nodes)
        random.shuffle(rand_nodes)
        nb_moves = 1
        improvement = False
        while nb_moves > 0:
            nb_moves = 0
            for node in rand_nodes:
                best_mod = 0
                best_com = node2com[node]

                # Calculate weights between node and its neighbor communities.
                weights2com = defaultdict(float)
                for nbr, wt in neighbours[node].items():
                    weights2com[node2com[nbr]] += wt

                if is_directed:
                    in_degree = in_degrees[node]
                    out_degree = out_degrees[node]
                    stot_in[best_com] -= in_degree
                    stot_out[best_com] -= out_degree
                    remove_cost = (
                            -weights2com[best_com] / graph_size
                            + resolution
                            * (out_degree * stot_in[best_com] + in_degree * stot_out[best_com])
                            / graph_size ** 2
                    )
                else:
                    degree = degrees[node]
                    stot[best_com] -= degree
                    remove_cost = -weights2com[best_com] / graph_size + resolution * (
                            stot[best_com] * degree) / (2 * graph_size ** 2)
                for nbr_com, wt in weights2com.items():
                    if is_directed:
                        gain = (
                                remove_cost
                                + wt / graph_size
                                - resolution
                                * (
                                        out_degree * stot_in[nbr_com]
                                        + in_degree * stot_out[nbr_com]
                                )
                                / graph_size ** 2
                        )
                    else:
                        gain = (remove_cost + wt / graph_size - resolution *
                                (stot[nbr_com] * degree) / (2 * graph_size ** 2))
                    if gain > best_mod:
                        best_mod = gain
                        best_com = nbr_com
                if is_directed:
                    stot_in[best_com] += in_degree
                    stot_out[best_com] += out_degree
                else:
                    stot[best_com] += degree
                if best_com != node2com[node]:
                    com = graph.nodes[node].get("nodes", {node})
                    partition[node2com[node]].difference_update(com)
                    inner_partition[node2com[node]].remove(node)
                    partition[best_com].update(com)
                    inner_partition[best_com].add(node)
                    improvement = True
                    nb_moves += 1
                    node2com[node] = best_com
        partition = list(filter(len, partition))
        inner_partition = list(filter(len, inner_partition))
        return partition, inner_partition, improvement

    @staticmethod
    def gen_graph(graph: nx.Graph, partition: List[Set[Any]]) -> nx.Graph:
        """Generate a new graph based on the partitions of a given graph

        Parameters
        ----------
        graph : NetworkX Graph
        partition : list of sets
            A valid partition of the graph `graph` at the level.

        Returns
        -------
        NetworkX Graph
        """
        new_graph = graph.__class__()
        node2com = {}
        for i, part in enumerate(partition):
            nodes = set()
            for node in part:
                node2com[node] = i
                nodes.update(graph.nodes[node].get("nodes", {node}))
            new_graph.add_node(i, nodes=nodes)

        for node1, node2, wt in graph.edges(data=True):
            wt = wt["weight"]
            com1 = node2com[node1]
            com2 = node2com[node2]
            temp = new_graph.get_edge_data(com1, com2, {"weight": 0})["weight"]
            new_graph.add_edge(com1, com2, **{"weight": wt + temp})
        return new_graph
