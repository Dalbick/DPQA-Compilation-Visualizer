# -*- coding: utf-8 -*-
"""
Created on Thu Apr  4 01:51:41 2024

@author: klyim
"""

from qiskit.providers.fake_provider import GenericBackendV2
from qiskit import transpile
from qiskit import QuantumCircuit
from qiskit import assemble
import json
import numpy as np

backend = GenericBackendV2(5)

#User may define a quantum circuit in this block
#Example of one as follows:
qc = QuantumCircuit(3, 1)
 
qc.h(0)
qc.x(1)
qc.cp(np.pi/4, 0, 1)
qc.h(0)
qc.ccz(0,1,2)
qc.MCMT('z',2, 1)
qc.measure([0], [0])

def transpile(qc, outputformat, backend=backend, basis_gates=['rx', 'ry', 'rz', 'cz'], show=False, jsonpath=None):
    if (outputformat != "string") and (outputformat != "json") and (outputformat != "dict"):
        print("outputformat must be strong, json, or dict")
        return
    transpiled_qc = transpile(qc, backend, basis_gates)
    if show:
        transpiled_qc.draw(output='mpl')
    json_data = assemble(transpiled_qc).to_dict()
    if outputformat == "json":
        save_file = open(jsonpath, "w")
        json.dump(json_data, save_file, indent = 6)
        save_file.close()
        return
    if outputformat == "string":
        json_str = json.dumps(json_data)
        return json_str
    if outputformat == "dict":
        return json_data
    
def optimize():
    # Transpile has optimization parameters to reduce gate count in itself, Kevin still looking into it.
    return    
