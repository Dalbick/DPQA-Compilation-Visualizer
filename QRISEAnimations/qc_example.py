# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 12:29:49 2024

@author: klyim
"""

from transpiler import DPQAtranspile

import numpy as np
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2
 
backend = GenericBackendV2(5)
 
qc = QuantumCircuit(4, 1)
 
qc.h(0)
qc.h(3)
qc.x(0)
qc.x(3)
qc.ccx(0, 3, 1)
qc.x(0)
qc.x(3)
qc.ccx(0, 3, 2)
qc.cx(2, 0)
qc.cx(2, 3)

qc.measure([0], [0])

test = DPQAtranspile(qc, "json", 4, jsonpath = "w_state")