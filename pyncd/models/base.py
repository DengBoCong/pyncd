# -*- coding: utf-8 -*-
"""Base class for all community detector models
"""
# Author: Bocong Deng <bocongdeng@gmail.com>
# License: BSD 2 clause

import abc


class BaseDetector(object, metaclass=abc.ABCMeta):
    """Abstract class for all community detection algorithms.

    Parameters
    ----------

    """

    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def gen_partition(self):
        pass


    def draw(self):
        pass


