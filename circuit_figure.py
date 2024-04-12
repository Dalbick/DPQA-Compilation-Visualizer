"""
This must be called before steane.py. This is to ensure the smt output is preserved without error correciton.
"""

from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
import matplotlib.pyplot as plt
from pylatexenc import *
import numpy as np
import json

def generate_figure(dir: str, name: str, num_qubits):
    with open(dir + name, 'r') as f:
        smt = json.load(f)

    qc = QuantumCircuit(num_qubits, num_qubits)
    for layer in smt['layers']:
        for g in layer['gates']:
            if g['op'] == 'rx':
                qc.rx(g['angle'] * np.pi, g['q0'])
                qc.barrier()
            if g['op'] == 'ry':
                qc.ry(g['angle'] * np.pi, g['q0'])
                qc.barrier()
            if g['op'] == 'rz':
                qc.rz(g['angle'] * np.pi, g['q0'])
                qc.barrier()
            if g['op'] == 'cz':
                qc.cx(g['q0'], g['q1'])
                qc.barrier()
            if g['op'] == 'm':
                qc.measure(g['q0'])

    qc.draw(output='mpl')
    plt.subplots_adjust(left=0.8, right=0.9, top=0.2, bottom=0.1)
    plt.savefig(dir + 'circuit_' + name[:-5] + '.jpg')

generate_figure('./', 'smt_QRISE.json', 2)
