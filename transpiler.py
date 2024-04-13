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

#User may define a quantum circuit in this block
#Example of one as follows:

def DPQAtranspile(qc, outputformat, num_qubits, backend=None, basis_gates=['rx', 'ry', 'cz'], show=False, jsonpath=None, optimization_level=2):
    if (outputformat != "string" and outputformat != "json" and outputformat != "dict"):
        print("outputformat must be strong, json, or dict")
        return
    
    #Declaring general backend off qiskit backend function, for custom neutral systems users will need to create one via qiskit.transpiler.target
    #Allows for custom gate fidelities, durations, etc, however requires a fixed qubit count for the system
    if backend == None:
        backend = GenericBackendV2(num_qubits)
        
    #Using IBM Transpiler on given basis gates and optimization level -> Skipping preset and custom pass managers
    transpiled_qc = transpile(qc, backend, basis_gates, optimization_level = optimization_level)
    
    
    if show:
        transpiled_qc.draw(output='mpl')
        
    # Assembling transpiled circuit, and converting to a dict, to be json-ed.
    json_data = assemble(transpiled_qc).to_dict()
    
    # Outputing desired format
    if outputformat == "json":
        save_file = open(jsonpath, "w")
        json.dump(json_data, save_file, indent = 6)
        save_file.close()
        return transpiled_qc
    if outputformat == "string":
        json_str = json.dumps(json_data)
        return json_str, transpiled_qc
    if outputformat == "dict":
        return json_data, transpiled_qc

