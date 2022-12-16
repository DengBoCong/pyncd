# -*- coding: utf-8 -*-
"""A set of utility functions to support community detection.
"""
# Author: DengBoCong <bocongdeng@gmail.com>
# License: BSD 2 clause

import networkx as nx
from typing import Any, Iterable, Union, Optional


def convert_multigraph(
        graph: Iterable[Any],
        weight: Optional[Union[str, bool]] = False,
        default: Union[int, float] = None,
        is_directed: bool = False,
        **kwargs) -> Union[nx.Graph, nx.DiGraph]:
    """Convert a Multigraph to normal Graph

    Parameters
    ----------
    graph : iterable container
        A container of nodes (list, dict, set, etc.).
        OR
        A container of (node, attribute dict) tuples.
        Node attributes are updated using the attribute dict.
    weight : string or bool, optional (default=False)
        The edge attribute returned in 3-tuple (u, v, ddict[data]).
        If True, return edge attribute dict in 3-tuple (u, v, ddict).
        If False, return 2-tuple (u, v).
    default: value, optional (default=None)
        Value used for edges that don’t have the requested attribute.
        Only relevant if data is not True or False.
    is_directed : bool, optional (default=False)
        Indicates whether the graph is directed.
    kwargs : keyword arguments, optional (default= no attributes)
        Update attributes for all nodes in nodes.
        Node attributes specified in nodes as a tuple take
        precedence over attributes specified via keyword arguments.

    Returns
    ----------
        NetworkX Graph or DiGraph
    """
    if is_directed:
        new_graph = nx.DiGraph()
    else:
        new_graph = nx.Graph()
    new_graph.add_nodes_from(graph, **kwargs)
    for u, v, wt in graph.edges(data=weight, default=default):
        if new_graph.has_edge(u, v):
            new_graph[u][v]["weight"] += wt
        else:
            new_graph.add_edge(u, v, weight=wt)
    return new_graph
