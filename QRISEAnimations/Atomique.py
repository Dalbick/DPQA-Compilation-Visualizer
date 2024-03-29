import numpy as np
from AnimationUtils import gates_animation, multiple_shuttle_animation
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import shutil
import json


def load_json(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def create_circuit_from_json(json_data):
    blocks = []
    for layer in json_data['layers']:
        atoms = [Atom(coords=(q['x'], q['y']), column=q['c'], row=q['r'], name=str(q['id'])) for q in layer['qubits']]
        if 'gates' in layer:
            for gate in layer['gates']:
                q0 = next(atom for atom in atoms if atom.name == str(gate['q0']))
                q1 = next(atom for atom in atoms if atom.name == str(gate['q1']))
                # assuming gate represents ent
                block = Block(atoms=[q0, q1], attribute='ent')
                block.entangle([q0], [q1])
                blocks.append(block)
        else:
            #case with no gates or smth else
            pass
        return QCircuit(blocks)


class Atom():
    def __init__(self, coords, name=None):
        self.coords = np.array(coords)
        self.init_coords = np.array(coords)
        self.x = coords[0]
        self.y = coords[1]
        self.row = row
        self.column = column
        self.name = name

    def distance(self, other):
        return np.linalg.norm(self.coords - other.coords)

    def distances(self, others):
        return [self.distance(other) for other in others]

def atomic_grid(x_width, y_length, spacing=10):
    atoms = []
    for x in range(x_width):
        for y in range(y_length):
            atoms.append(Atom(coords=(x * spacing, y * spacing)))
    return atoms

class Operation():
    def __init__(self, atoms, attribute):
        self.atoms = atoms
        self.attribute = attribute

class Block():
    def __init__(self, atoms=None, attribute=None):
        if atoms is not None:
            self.num_qubits = len(atoms)
        self.atoms = atoms
        self.operations = []
        self.attribute = attribute

    def rotate(self, atoms):
        if type(atoms) == Atom:
            self.operations.append(Operation([atoms], 'rot'))
        else:
            for atom in atoms:
                self.operations.append(Operation([atom], 'rot'))
        assert self.attribute == 'rot', 'this block must contain only rotations'

    def entangle(self, atoms1, atoms2):
        for i, atom in enumerate(atoms1):
            self.operations.append(Operation([atom, atoms2[i]], 'ent'))
        assert self.attribute == 'ent', 'this block must contain only entangling operations'

    def from_qiskit(self, qc, atoms):
        '''
        atoms[i] correspond to qubit with index i in qc
        '''
        self.__init__(atoms, attribute=None)
        for instruction in qc.data:
            if instruction.operation.num_qubits == 1:
                if self.attribute == 'ent':
                    raise Exception('this block contains only entangling operations')
                self.attribute = 'rot'
                self.rotate(atoms=atoms[instruction.qubits[0]._index])
            elif instruction.operation.num_qubits == 2:
                if self.attribute == 'rot':
                    raise Exception('this block contains only rotating operations')
                self.attribute = 'ent'
                self.entangle(atoms1=[atoms[instruction.qubits[0]._index]], atoms2=[atoms[instruction.qubits[1]._index]])

        assert qc.depth() == 1, 'block must be of depth 1'
        return self

    def organize_for_visualization(self):
        if self.attribute == 'ent':
            atoms1 = []
            atoms2 = []
            standby_atoms = []
            for i, operation in enumerate(self.operations):
                atoms1.append(operation.atoms[0])
                atoms2.append(operation.atoms[1])
            for atom in self.atoms:
                if atom not in atoms1 + atoms2:
                    standby_atoms.append(atom)
            return [a.coords for a in atoms1], [a.coords for a in atoms2], [a.coords for a in standby_atoms]

        if self.attribute == 'rot':
            atoms = []
            standby_atoms = []
            for i, operation in enumerate(self.operations):
                atoms.append(operation.atoms[0])
            for atom in self.atoms:
                if atom not in atoms:
                    standby_atoms.append(atom)
            return [a.coords for a in atoms], [a.coords for a in standby_atoms]

class QCircuit():
    def __init__(self, blocks):
        self.blocks = blocks

def combine_videos(folder_path):
    video_files = [f for f in os.listdir(folder_path)]
    video_files.sort()  # Sort files if order is important
    clips = [VideoFileClip(os.path.join(folder_path, f)) for f in video_files]
    final_clip = concatenate_videoclips(clips)  # Concatenate the videos
    output_file = os.path.join(folder_path, "circuit.mp4")  # Generate the output file path
    final_clip.write_videofile(output_file, codec="libx264", fps=30)  # Write the result to a new file

class Animation():
    def __init__(self, name=None):
        self.name = name

    def create_animation(self, qcircuit, folder_name="circuit_videos"):
        if os.path.exists(folder_name):
            shutil.rmtree(folder_name)
        os.makedirs(folder_name)

        shuttle_time = 2
        stop_time = 1
        distance = 2
        pulse_duration = 3
        for block_number, block in enumerate(qcircuit.blocks):
            if block.attribute == 'ent':
                atoms1, atoms2, standby_atoms = block.organize_for_visualization()
                multiple_shuttle_animation(atoms1=atoms1, atoms2=atoms2,
                                           shuttle_time=shuttle_time, distance=distance,
                                           include_reverse=True, stop_time=stop_time,
                                           standby_atoms=standby_atoms,
                                           path=f'./{folder_name}', name=f'block{block_number + 1}.mp4')

            if block.attribute == 'rot':
                atoms, standby_atoms = block.organize_for_visualization()
                gates_animation(atoms=atoms,
                                pulse_duration=pulse_duration,
                                standby_atoms=standby_atoms,
                                path=f'./{folder_name}', name=f'block{block_number + 1}.mp4')

        combine_videos(folder_name)
