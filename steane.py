import json
import copy
import itertools

# if qubits start at same position (within R_b) Steane code encoding will not be successful
# we move one of the qubits from any such pair to the right and add this layer to be deleted later
def resolve_duplicates(qubits):
    # sort the list by 'c' value so that order is preserved in the SMT solution
    sorted_qubits = sorted(qubits, key=lambda x: x['c'])

    # use a hash table to track seen coordinates
    seen_coords = {}

    while True:
        updates_made = False
        for q in sorted_qubits:
            coord = (q['x'], q['y'])

            if coord in seen_coords:
                q['x'] += 1
                updates_made = True
            else:
                seen_coords[coord] = True

        if not updates_made:
            break

        # Reset seen coordinates for the next pass
        seen_coords = {}

    return sorted_qubits

def initialize_steane(dir: str, name: str):
    """
    Non-fault tolerantly produce two Steane codes for every given physical qubit.
    Move the ancilla logical bit to the storage or readout zone.
    """
    with open(dir + name, 'r') as f:
        smt = json.load(f)

    # modify coordinates in first layer to take care of duplicates
    first_layer_copy = copy.deepcopy(smt['layers'][0]) # ensure that dictionary entries are also copied
    resolved_qubits = resolve_duplicates(first_layer_copy['qubits'])
    first_layer_copy['qubits'] = resolved_qubits
    smt['layers'].insert(0, first_layer_copy)

    # add padding to every layer
    padding = lambda x : (x + 1) * 5 # We need two rows by four columns for each Steane code initialization (four by four for two steane codes)
    for layer in smt['layers']:
        for q in layer['qubits']:
            q['x'], q['c'], q['y'], q['r'] = padding(q['x']), padding(q['c']), padding(q['y']), padding(q['r'])

    id_padding = lambda x : 14 * x
    for q in smt['layers'][0]['qubits']:
       q['id'] = id_padding(q['id'])

    # check if this is runnable on Aquila
    if any(q['x'] + q['c'] + q['y'] + q['r'] > 302 for q in smt['layers'][0]['qubits']):
        print("WARNING: the dimensions required to implement error correction are too large to run on Aquila") # should we raise an error here?

    # Produce all 4 layers for Steane code generation + 1 layer for movement to readout zone.
    # Is there some better way to identify these physical Qs besides 'steane_id' and 'ancilla'?
    # create a gate and qubit array to be inserted at the top of the SMT output
    steane_layer_gates = [ [] for _ in range(5) ]
    steane_layer_qubits = [ [] for _ in range(5) ]

    for i, q in enumerate(smt['layers'][0]['qubits']):
      for ancilla in range(2):
        for i_q in range(7):
            # get all info from current logical qubit
            for k in range(5):
              steane_layer_qubits[k].insert(0,copy.deepcopy(q))

            # create and move physical qubits to Layer 1 coordinates
            steane_layer_qubits[0][0]['id'] += i_q * (ancilla + 1)
            steane_layer_qubits[0][0]['x'] -= 4 if i_q in [1, 3, 4, 5] else 3
            steane_layer_qubits[0][0]['y'] -= 1 + 2*ancilla if i_q in [2, 1, 3] else 2*ancilla
            steane_layer_qubits[0][0]['c'] -= 4 if i_q in [1, 3, 4, 5] else 3
            steane_layer_qubits[0][0]['r'] -= i_q + 2*ancilla if i_q in [2, 1, 3] else 2*ancilla

            # move physical qubits to Layer 2 coordinates
            steane_layer_qubits[1][0]['id'] += i_q * (ancilla + 1)
            steane_layer_qubits[1][0]['x'] -= 3 if i_q in [3, 5, 6] else 2
            steane_layer_qubits[1][0]['y'] -= 1 + 2*ancilla if i_q in [2, 1, 3] else 2*ancilla
            steane_layer_qubits[1][0]['c'] -= 3 if i_q in [3, 5, 6] else 2
            steane_layer_qubits[1][0]['r'] -= i_q + 2*ancilla if i_q in [2, 1, 3] else 2*ancilla

            # move physical qubits to Layer 3 coordinates
            steane_layer_qubits[2][0]['id'] += i_q * (ancilla + 1)
            steane_layer_qubits[2][0]['x'] -= 1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            steane_layer_qubits[2][0]['y'] -= 2*ancilla
            steane_layer_qubits[2][0]['c'] -= 1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            steane_layer_qubits[2][0]['r'] -= 2*ancilla

            # fault-tolerantly entangle ancilla logical bits with reversible bits
            steane_layer_qubits[3][0]['id'] += i_q * (ancilla + 1)
            steane_layer_qubits[3][0]['x'] -= 1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            steane_layer_qubits[3][0]['y'] -= 2
            steane_layer_qubits[3][0]['c'] -= 1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            steane_layer_qubits[3][0]['r'] -= 2

            # move Ancilla qubits to readout zone (Layer 3 + 1)
            steane_layer_qubits[4][0]['id'] += i_q * (ancilla + 1)
            steane_layer_qubits[4][0]['x'] = steane_layer_qubits[2][0]['x'] - 1
            steane_layer_qubits[4][0]['y'] = {'R': 75-steane_layer_qubits[2][0]['y']} # we indicate qubit in readout zone with a 'R' key in coordinate dict
            steane_layer_qubits[4][0]['c'] = steane_layer_qubits[2][0]['c'] - 1 # so that ancillas are transferred to different AOD than reversible bits
            steane_layer_qubits[4][0]['r'] = {'R': 75-steane_layer_qubits[2][0]['r']}

            # initialize all physical qubits in the steane to |+>
            steane_layer_gates[0].append({
               'id': i_q*(ancilla+1)*i,
               'q0': i_q*(ancilla+1)*i,
               'q1': -1,
               'op': 'ry',
               'angle': 0.5
            })

    # create entangling gates for relevant qubits in Layer 1
    i_g = [0,1,4]
    for i_g_0 in ([num + 7 * i for num in i_g for i in range(0, len(smt['layers'][0]['qubits'])*2)]):
        steane_layer_gates[0].append({
            'id': 0,
            'q0': i_g_0,
            'q1': i_g_0 + 6 if i_g_0 % 7 == 0 else i_g_0 + 2 if i_g_0 % 7 == 1 else i_g_0 + 1,
            'op': 'cz',
            'angle': 0
        })

    # create entangling gates for relevant qubits in Layer 2
    i_g = [1,4,5]
    for i_g_1 in ([num + 7 * i for num in i_g for i in range(0, len(smt['layers'][0]['qubits'])*2)]):
        steane_layer_gates[1].append({
            'id': 0,
            'q0': i_g_1,
            'q1': i_g_1 + 1 if i_g_1 % 7 == 5 else i_g_1 - 4 if i_g_1 % 7 == 4 else i_g_1 + 1,
            'op': 'cz',
            'angle': 0
        })

    # create entangling and single qubit gates for relevant qubits in Layer 3
    # CZs
    i_g = [1,2,3]
    for i_g_2 in ([num + 7 * i for num in i_g for i in range(0, len(smt['layers'][0]['qubits'])*2)]):
        steane_layer_gates[2].append({
            'id': 0,
            'q0': i_g_2,
            'q1': i_g_2 + 3 if i_g_2 % 7 == 1 else i_g_2 - 2 if i_g_2 % 7 == 2 else i_g_2 + 2,
            'op': 'cz',
            'angle': 0
        })
    # Hadamards
    i_g = [2,3,4,6]
    for i_g_single_2 in ([num + 7 * i for num in i_g for i in range(0, len(smt['layers'][0]['qubits'])*2)]):
        steane_layer_gates[2].append({
            'id': 0,
            'q0': i_g_2,
            'q1': -1,
            'op': 'ry',
            'angle': 0.5,
        })
    
    # fault-tolerantly CNOT the ancillas with the reversible logical bits
    # positions are set. should play global rydberg pulse in this stage.
    for i_g_3 in [num + 7 * i for num in range(7) for i in range(0, len(smt['layers'][0]['qubits'])*2)]:
        steane_layer_gates[3].append({
            'id': 0,
            'q0': i_g_3,
            'q1': i_g_3 + 7,
            'op': 'cz',
            'angle': 0
        })

    steane = {"name": f"{smt['name']}_steane", "layers": []}

    # dump to steane output for animation processing on initialization stages
    for layer in range(4,-1,-1):
      steane['layers'].insert(0, {'qubits': steane_layer_qubits[layer], 'gates': steane_layer_gates[layer]})
    with open(dir + "steane_" + name, 'w') as f:
        json.dump(steane, f)

    """
    TODO: add padding for the qubits at starting positions
    Two Steane codes for each qubit in initial set-up
    Non-fault tolerantly make Steane codes
    CNOT the pairs.
    Move the ancilla Steane code of each pair to readout zone
    Pad each additional layer
    """

initialize_steane('./', 'smt_QRISE.json')