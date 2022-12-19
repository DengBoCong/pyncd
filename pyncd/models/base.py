# -*- coding: utf-8 -*-
"""Base class for all community detector models
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause

import abc
from typing import Any


class BaseDetector(object, metaclass=abc.ABCMeta):
    """Abstract class for all community detection algorithms.
    """

    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def best_partition(self, graph: Any):
        """Find the best partition of a graph using the Louvain Community Detection Algorithm.

        Parameters
        ----------
        graph : The graph from which to detect communities

        Returns
        -------
        NetworkX graph
            Each node represents one community and contains all the nodes that constitute it.
        """
        pass

    # def draw(self):
    #     pass


