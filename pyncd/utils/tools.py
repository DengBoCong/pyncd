# -*- coding: utf-8 -*-
"""A set of utility functions to support community detection.
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause


import networkx as nx
import numpy as np
import os
import random
import torch
from inspect import isclass
from typing import Any, Union, List, Tuple, Dict, Set


def set_seed(manual_seed: int) -> None:
    """Set random seeds
    """
    random.seed(manual_seed)
    os.environ['PYTHONHASHSEED'] = str(manual_seed)
    np.random.seed(manual_seed)
    torch.manual_seed(manual_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(manual_seed)
        torch.cuda.manual_seed_all(manual_seed)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        torch.backends.cudnn.enabled = False


def check_is_fitted(
        detector: Any,
        attrs: Union[str, List[str], Tuple[str]] = None,
        msg: str = None,
        all_or_any: Union[all, any] = all) -> None:
    """Perform is_fitted validation for detector.
    Reference implementation: https://github.com/scikit-learn/scikit-learn/blob/98cf537f5/sklearn/utils/validation.py#L1312

    Checks if the detector is fitted by verifying the presence of
    fitted attributes (ending with a trailing underscore) and otherwise
    raises a NotFittedError with the given message.

    Parameters
    ----------
    detector : detector instance
        Detector instance for which the check is performed.
    attrs : str, list or tuple of str, default=None
        Attribute name(s) given as string or a list/tuple of strings

        If `None`, `detector` is considered fitted if there exist an
        attribute that ends with a underscore and does not start with double
        underscore.
    msg : str, default=None
        The default error message is, "This %(name)s instance is not fitted
        yet. Call 'fit' with appropriate arguments before using this detector."

        For custom messages if "%(name)s" is present in the message string,
        it is substituted for the detector name.
    all_or_any : callable, {all, any}, default=all
        Specify whether all or any of the given attributes must exist.

    Raises
    ------
    TypeError
        If the detector is a class or not an detector instance
    NotFittedError
        If the attributes are not found.
    """
    if isclass(detector):
        raise TypeError(f"{detector} is a class, not an instance.")
    if msg is None:
        msg = (
            "This %(name)s instance is not fitted yet. Call 'fit' with "
            "appropriate arguments before using this detector."
        )

    if not hasattr(detector, "fit"):
        raise TypeError(f"{detector} is not an detector instance.")

    if attrs is not None:
        if not isinstance(attrs, (list, tuple)):
            attrs = [attrs]
        fitted = all_or_any([hasattr(detector, attr) and getattr(detector, attr) is not None for attr in attrs])
    elif hasattr(detector, "__detector_is_fitted__"):
        fitted = detector.__detector_is_fitted__()
    else:
        fitted = [
            v for v in vars(detector) if v.endswith("_") and not v.startswith("__")
        ]

    if not fitted:
        raise RuntimeError(msg % {"name": type(detector).__name__})


def color_network(graph: nx.Graph) -> Dict[int, Set[Any]]:
    """Colors the network so that neighboring nodes all have distinct colors.
    Returns a dict keyed by color to a set of nodes with that color.
    """
    coloring = dict()  # color => set(node)
    colors = nx.coloring.greedy_color(graph)
    for node, color in colors.items():
        if color in coloring:
            coloring[color].add(node)
        else:
            coloring[color] = {node}
    return coloring
