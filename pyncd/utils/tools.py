# -*- coding: utf-8 -*-
"""A set of utility functions to support community detection.
"""
# Author: DengBoCong <bocongdeng@gmail.com>
# License: BSD 2 clause


import numpy as np
import os
import random
import torch


def set_seed(manual_seed: int):
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
