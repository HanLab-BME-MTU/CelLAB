"""
Associa — Association Methods
==============================
Each method takes two 1-D signals and returns a standardized result dict.

Standard result fields:
    method       : str    — method name
    statistic    : float  — primary coupling metric (rho, F-stat, r, MI, TE)
    p_value      : float  — parametric p-value (if available)
    direction    : str    — '1→2', '2→1', or 'symmetric'
    details      : dict   — method-specific extras
    error        : str    — only present if method failed
"""

from .correlation import pearson, spearman
from .mutual_info import mutual_information
from .granger import granger_causality
from .ccm import ccm
from .transfer_entropy import transfer_entropy
