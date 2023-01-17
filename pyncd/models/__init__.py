# -*- coding: utf-8 -*-
"""Make certain functions from some of the previous subpackages available
to the user as direct imports from the `pyncd.models` namespace.
"""
from pyncd.models.louvain import LouvainDetector
from pyncd.models.label_propagation import LPADetector

__all__ = ["LouvainDetector", "LPADetector"]
