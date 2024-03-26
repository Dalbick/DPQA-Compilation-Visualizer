from Atomique import Block, QCircuit, Animation, atomic_grid
from qiskit import QuantumCircuit

if __name__ == "__main__":
    # animating QCircuit
    atoms = atomic_grid(20, 4)  # creates a 20x4 grid of atoms
    block1 = Block(atoms, 'rot')
    block1.rotate(atoms[:40])  # perform some rotation on the first 40 atoms
    block2 = Block(atoms, 'ent')
    block2.entangle(atoms[:40], atoms[40:])  # perform some rotation on the second 40 atoms
    block3 = Block(atoms, 'ent')
    block3.entangle(atoms[40:], atoms[:40])  # entangle first 40 atoms with the other 40
    circ = QCircuit([block1, block2, block3])  # create a circuit with these three blocks
    Animation().create_animation(circ, folder_name="circuit_videos")  # animate the circuit

    # animating qiskit circuit
    qc = QuantumCircuit(4)
    qc.h([0, 1, 2, 3])
    atoms = atomic_grid(4, 1)
    block_from_qiskit = Block().from_qiskit(qc=qc, atoms=atoms)
    circ_from_qiskit = QCircuit(blocks=[block_from_qiskit])
    Animation().create_animation(circ_from_qiskit, folder_name="circuit_from_qiskit_videos")
