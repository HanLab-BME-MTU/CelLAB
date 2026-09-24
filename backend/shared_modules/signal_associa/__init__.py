"""
Associa — Signal Coupling Analysis Engine
==========================================
Shared analysis engine for signal association / coupling detection.
Used by FASTIA (FA protein signals) and IMMUNIA (cell trajectories).

Modules:
    stationarizer    — Make signals stationary (bandpass, detrend, lazy, diff)
    surrogate_generator — Generate null-hypothesis surrogates (IAAFT, shuffle, etc.)
    methods/         — Association methods (GC, CCM, correlation, MI, TE)
    associa          — Single-pair master orchestrator
    batch_associa    — Multi-pair parallel orchestrator

Author: CelLAB / Han Mechanobiology Lab, Michigan Tech
"""

from .stationarizer import Stationarizer, StationarityResult, run_diagnostics
from .surrogate_generator import SurrogateGenerator
from .signal_associa import Associa
