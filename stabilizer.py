import json
import copy


def stabilize(dir: str, name: str):
    """
    Compiles 6 stabilizer measurements on the ancilla bits to deduce the source of at MOST one error in the logical entangled bit.
    These measurements along the X or Z axis occur after each stage of gates to correct for errors.
    """
    with open(dir + name, 'r') as f:
        smt = json.load(f)

    steane_layer_qubits = []

    for i, q in enumerate(smt['layers'][0]['qubits']):
        for ancilla in range(2):
            for i_q in range(7):
                steane_layer_qubits.insert(0,copy.deepcopy(q))
                steane_layer_qubits[0]['id'] += i_q * (ancilla + 1)
                steane_layer_qubits[0]['x'] = steane_layer_qubits[2][0]['x'] - 1
                steane_layer_qubits[0]['y'] = {'R': 75-steane_layer_qubits[2][0]['y']} # we indicate qubit in readout zone with a 'R' key in coordinate dict
                steane_layer_qubits[0]['c'] = steane_layer_qubits[2][0]['c'] - 1 # so that ancillas are transferred to different AOD than reversible bits
                steane_layer_qubits[0]['r'] = {'R': 75-steane_layer_qubits[2][0]['r']}

    ancilla_layer_qubits = [ [] for _ in range(7)]
    ancilla_layer_gates = [ [] for _ in range(7)]
    for layer in range(len(smt['layers']),0,-1):
        for i, physical in enumerate(steane_layer_qubits):
            ancilla_layer_qubits[i].append(physical.copy())
            if i < 6:
                ancilla_layer_gates[i].append({
                    'id': 'S',  # change this notation to match Daniil
                    'logical_q': physical['id'],
                    'op': f'S{i+1}',
                    'rotation': 0,
                    'q0': 0 if i in [0,3] else 2 if i in [1,4] else 1,
                    'q1': 1 if i in [0,3] else 4 if i in [1,4] else 2,
                    'q2': 2 if i in [0,3] else 5 if i in [1,4] else 3,
                    'q3': 6 if i in [0,1,3,4] else 5,
                    'ancilla': 1
                })

        # insert the stabilizer measurements in separate stages between each SMT stage
        for stabilizer in range(7):
            for i in range(6)
                smt['layers'].insert(layer,{'qubits': ancilla_layer_qubits[stabilizer], 'gates': ancilla_layer_gates[i]})
    print(len(smt['layers'][1]['gates']))
    with open(dir + "stabilize_" + name, 'w') as f:
        json.dump(smt, f)