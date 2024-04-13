# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 12:29:49 2024

@author: klyim
"""

from MasterRunner import Runner
import numpy as np
from qiskit import QuantumCircuit
from qiskit.providers.fake_provider import GenericBackendV2

backend = GenericBackendV2(5)

theta = 2 * np.arccos(1 / np.sqrt(3))

num_qubits = 3

qc = QuantumCircuit(3, 1)

qc.ry(theta, 0)
qc.ch(0, 1)
qc.cx(1, 2)
qc.cx(0, 1)
qc.x(0)

qc.measure([0], [0])

run = Runner(name="QRISE.json", dir="./", qc=qc, num_qubits=num_qubits)

run.decompose()
run.parse_json()
run.SMT()
run.singles_reinsert()
run.animate()
