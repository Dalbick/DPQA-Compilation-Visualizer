from MasterRunner import Runner
from qiskit import QuantumCircuit

num_qubits = 5
qc = QuantumCircuit(5, 5)

qc.h(range(num_qubits))

qc.cz(0,1)
qc.cz(3,2)
qc.cz(3,4)
qc.h(3)
qc.cz(0,2)
qc.h(2)

run = Runner(name="QRISE.json", dir="./", qc=qc, num_qubits=num_qubits)

run.decompose()
run.parse_json()
run.SMT()
run.singles_reinsert()
run.animate()