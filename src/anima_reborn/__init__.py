"""anima-reborn — the anima-experience engines, as plain Python.

`dancinlab/anima-experience` runs four simulations in a browser canvas at 60
fps. This is the same four with the rendering taken away: the maths, headless,
stdlib only, seedable so a run can be reproduced.

    from anima_reborn import EmergenceEngine

    bound = EmergenceEngine(coupling=0.9, seed=7).run(250)
    free = EmergenceEngine(coupling=0.0, seed=7).run(250)
    print(bound.mutual_information > free.mutual_information)   # True

The engines:

    emergence.py  two streams sharing one oscillator; mutual information rises
                  as they bind
    crystal.py    a driven Ising ring that locks into a period-2 rhythm and
                  keeps it despite an imperfect drive
    repulsion.py  two latent engines held apart; tension, concept, meaning and
                  mood read off the gap between them
    pipeline.py   the last two joined: engine separation drives two streams,
                  and emergence is measured on the pair
    info.py       the entropy and mutual-information estimators the first and
                  last share

Every engine is a class you step yourself: no threads, no timers, no clock of
its own. Pass `seed=` for a reproducible run.

Two more pieces sit alongside them:

    iit4/         Integrated Information Theory 4.0 — how much a system is one
                  thing rather than parts. Ported from the hexa engine in
                  `dancinlab/selfhost-work`, and bit-exact against it.
    coupled.py    the gap as a channel — A and G reading each other, the one
                  engine here whose integration is bought by its own wiring
    align.py      the only module that learns — two modalities brought to one
                  place by co-occurrence, scored on concepts never trained on
    substrate.py  the bridge: drive an engine from every state, measure its
                  transition matrix, and hand it to Phi.
    words.py      words as a drive — with the null control that stops an
                  estimator artefact reading as emergence.
"""

from __future__ import annotations

from .align import AlignState, Aligner
from .coupled import CoupledEngine, CoupledState, Wiring
from .crystal import CrystalState, CrystalVerdict, TimeCrystal, autocorrelation
from .emergence import EmergenceEngine, EmergenceMetrics
from .info import Binning, Emergence, entropy, joint_entropy, mutual_information
from .pipeline import Pipeline, PipelineState
from .repulsion import Mood, RepulsionField, RepulsionState
from .substrate import (
    CoupledReading,
    RecurrenceEvidence,
    SubstrateReading,
    binarize,
    crystal_matrix,
    crystal_phi,
    coupled_matrix,
    coupled_phi,
    estimate_matrix,
    recurrence_evidence,
)
from .words import Channel, WordReading, blake_scalar, drive, measure, measure_channel

__version__ = "0.1.0"

__all__ = [
    "AlignState",
    "Aligner",
    "Binning",
    "Channel",
    "CoupledEngine",
    "CoupledReading",
    "CoupledState",
    "CrystalState",
    "CrystalVerdict",
    "Emergence",
    "EmergenceEngine",
    "EmergenceMetrics",
    "Mood",
    "Pipeline",
    "PipelineState",
    "RecurrenceEvidence",
    "RepulsionField",
    "RepulsionState",
    "SubstrateReading",
    "TimeCrystal",
    "Wiring",
    "WordReading",
    "autocorrelation",
    "binarize",
    "blake_scalar",
    "coupled_matrix",
    "coupled_phi",
    "crystal_matrix",
    "crystal_phi",
    "drive",
    "entropy",
    "estimate_matrix",
    "joint_entropy",
    "measure",
    "measure_channel",
    "mutual_information",
    "recurrence_evidence",
]
