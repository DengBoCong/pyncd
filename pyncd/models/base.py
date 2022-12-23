# -*- coding: utf-8 -*-
"""Base class for all community detector models
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause

import abc
import networkx as nx
from typing import Any, Union, List


class BaseDetector(object, metaclass=abc.ABCMeta):
    """Abstract class for all community detection algorithms.
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def fit(self, graph: nx.Graph, weight: Union[str, None] = "weight") -> object:
        """Fit detector. Find the best partition of a graph using the Community Detection Algorithm.

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
        """
        pass

    @abc.abstractmethod
    def decision_function(self, nodes: List[Any]) -> List[Any]:
        """Estimate partition of nodes using the fitted detector

        Parameters
        ----------
        nodes : The input nodes.

        Returns
        -------
        partitions : The partition of the input nodes.
        """
        pass

    # def draw(self):
    #     pass

    def __repr__(self):
        # Extend as needed
        class_name = self.__class__.__name__
        return f"{class_name}"
