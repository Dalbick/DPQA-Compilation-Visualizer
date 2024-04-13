# Atomique Solution for QuEra's Challenge -- QRISE 2024

Key files:

- `MasterRunner.py` compiles all the following files from a single class.
- `solve.py` contains the class `DPQA` where we encode the compilation problem to SMT, and use `z3-solver` to solve it.
- `animation.py` contains the class `CodeGen` that generates DPQA instructions (five types `Init`, `Rydberg`, `Raman`, `Activate`, `Deactivate`, and `Move`), and the class `Animator` that generates animations from DPQA instructions.
- `transpiler.py` takes in a qiskit QuantumCircuit object and lists the gates and associated parameters in a readable format
- `circuit_figure.py` generates a drawing of the qiskit circuit while maintaining SMT order
- `steane.py` turns the qubits in a generic circuit into logical bits ()

The `qc_example.py` file includes our example of animating a circuit which generates a w state. If you want to make your own animation of a qiskit circuit, `import Runner` from `MasterRunner`, define your circuit and the number of qubits in it, and create a Runner initialization.
