import json
import copy

NUM_STEANE_LAYERS = 5
NUM_PHYSICAL_QUBITS = 7


# if qubits start at same position (within atomic separation R_b) Steane code encoding will not be successful
# we move one of the qubits from any such pair to the right and add this layer to be deleted later
def resolve_duplicates(qubits):
    # sort the list by 'c' value so that order is preserved in the SMT solution
    sorted_qubits = sorted(qubits, key=lambda x: x["c"])

    # use a hash table to track seen coordinates
    seen_coords = {}

    while True:
        updates_made = False
        for q in sorted_qubits:
            coord = (q["x"], q["y"])

            if coord in seen_coords:
                q["x"] += 1
                q["y"] += 1
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
    with open(dir + name, "r") as f:
        smt = json.load(f)

    # modify coordinates in first layer to take care of duplicates
    first_layer_copy = copy.deepcopy(
        smt["layers"][0]
    )  # ensure that dictionary entries are also copied
    resolved_qubits = resolve_duplicates(first_layer_copy["qubits"])
    first_layer_copy["qubits"] = resolved_qubits
    smt["layers"].insert(0, first_layer_copy)

    # add padding to first layer
    padding = (
        lambda x: (x + 1) * 5
    )  # We need two rows by four columns for each Steane code initialization (four by four for two steane codes [one ancilla])
    for q in smt["layers"][0]["qubits"]:
        q["x"], q["c"], q["y"], q["r"] = (
            padding(q["x"]),
            padding(q["c"]),
            padding(q["y"]),
            padding(q["r"]),
        )

    id_padding = lambda x: 14 * x
    for q in smt["layers"][0]["qubits"]:
        q["id"] = id_padding(q["id"])
    # print(q["id"] for q in smt["layers"][0]["qubits"])

    # check if this is runnable on Aquila
    if any(q["x"] + q["c"] + q["y"] + q["r"] > 302 for q in smt["layers"][0]["qubits"]):
        print(
            "WARNING: the dimensions required to implement error correction are too large to run on Aquila"
        )

    # Produce all 5 layers for Steane code generation + 1 layer for movement to readout zone.

    # create a gate and qubit array to be inserted at the top of the SMT output
    steane_layer_gates = [[] for _ in range(NUM_STEANE_LAYERS)]
    steane_layer_qubits = [[] for _ in range(NUM_STEANE_LAYERS)]

    for logical_num, q in enumerate(smt["layers"][0]["qubits"]):
        for i in range(NUM_PHYSICAL_QUBITS * 2 - 1, -1, -1):
            # get all info from current logical qubit
            for k in range(NUM_STEANE_LAYERS):
                steane_layer_qubits[k].insert(0, copy.deepcopy(q))

            ancilla = 0 if i < 7 else 1
            i_q = i % 7

            #  Layer 1: preparation to Hadamard and CZ relevant qubits
            steane_layer_qubits[0][0]["id"] += i
            steane_layer_qubits[0][0]["x"] -= (
                4 if i_q in [1, 3, 4, 5] else 3 if i_q in [6, 0] else 2
            )
            steane_layer_qubits[0][0]["y"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[0][0]["c"] -= (
                4
                if i_q in [5, 3]
                else 3 if i_q in [4, 1] else 2 if i_q in [6, 0] else 1
            )
            steane_layer_qubits[0][0]["r"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[0][0]["a"] = 0 if i_q in [6, 3, 2] else 1

            # Layer 2: CZs
            steane_layer_qubits[1][0]["id"] += i
            steane_layer_qubits[1][0]["x"] -= 3 if i_q in [3, 5, 6] else 2
            steane_layer_qubits[1][0]["y"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[1][0]["c"] -= (
                4 if i_q in [5, 3] else 3 if i_q in [4, 1] else 2 if i_q == 6 else 1
            )
            steane_layer_qubits[1][0]["r"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[1][0]["a"] = 0 if i_q in [6, 3] else 1

            # Layer 3: CZs
            steane_layer_qubits[2][0]["id"] += i
            steane_layer_qubits[2][0]["x"] -= (
                1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            )
            steane_layer_qubits[2][0]["y"] -= (
                2 * ancilla if i_q == 6 else 1 + 2 * ancilla
            )
            steane_layer_qubits[2][0]["c"] -= (
                4 if i_q in [5, 3] else 2 if i_q in [4, 1] else 3 if i_q == 6 else 1
            )
            steane_layer_qubits[2][0]["r"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[2][0]["a"] = 0 if i_q in [6, 3, 2, 1] else 1

            # Layer 3: Hadamards
            steane_layer_qubits[3][0]["id"] += i
            steane_layer_qubits[3][0]["x"] -= (
                1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            )
            steane_layer_qubits[3][0]["y"] -= (
                1 + 2 * ancilla if i_q in [3, 2, 1] else 2 * ancilla
            )
            steane_layer_qubits[3][0]["c"] -= (
                1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            )
            steane_layer_qubits[3][0]["r"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[3][0]["a"] = 0 if ancilla else 1

            # fault-tolerantly entangle ancilla logical bits with reversible bits
            steane_layer_qubits[4][0]["id"] += i
            steane_layer_qubits[4][0]["x"] -= (
                1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            )
            steane_layer_qubits[4][0]["y"] -= 3 if i_q in [3, 1, 2] else 2
            steane_layer_qubits[4][0]["c"] -= (
                1 if i_q in [0, 2] else 2 if i_q in [1, 4] else 3 if i_q == 6 else 4
            )
            steane_layer_qubits[4][0]["r"] -= (
                1 + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            )
            steane_layer_qubits[4][0]["a"] = 0 if not ancilla else 1

            # # move Ancilla qubits to readout zone (Layer 3 + 1)
            # steane_layer_qubits[4][0]["id"] += i_q * (ancilla + 1)
            # steane_layer_qubits[4][0]["x"] = steane_layer_qubits[2][0]["x"] + (ancilla - 1)
            # steane_layer_qubits[4][0]["y"] = -1 # Can we enable -1 value in animation constraints?
            # steane_layer_qubits[0][0]["c"] -= 4 if i_q in [5,3] else 3 if i_q in [4,1] else 2 if i_q == 6 else 1
            # steane_layer_qubits[0][0]["r"] -= (
            #     i_q + 2 * ancilla if i_q in [2, 1, 3] else 2 * ancilla
            # )
            # steane_layer_qubits[0][0]["a"] = 0 if ancilla == 1 else 1 # want to move the non-ancillas to readout

    # create gates for relevant qubits in Steane Layer 1
    # Hadamards
    for i_g_single_1 in [
        num + 7 * i
        for num in range(7)
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[0].append(
            {
                "id": 0,
                "q0": i_g_single_1,
                "q1": -1,
                "op": "ry",
                "angle": 0.5,
            }
        )
    # CZs
    i_g = [0, 1, 4]
    for i_g_0 in [
        num + 7 * i
        for num in i_g
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[0].append(
            {
                "id": 0,
                "q0": i_g_0,
                "q1": (
                    i_g_0 + 6
                    if i_g_0 % 7 == 0
                    else i_g_0 + 2 if i_g_0 % 7 == 1 else i_g_0 + 1
                ),
                "op": "cz",
                "angle": 0,
            }
        )

    # create entangling gates for relevant qubits in Layer 2
    i_g = [1, 4, 5]
    for i_g_1 in [
        num + 7 * i
        for num in i_g
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[1].append(
            {
                "id": 0,
                "q0": i_g_1,
                "q1": (
                    i_g_1 + 1
                    if i_g_1 % 7 == 5
                    else i_g_1 - 4 if i_g_1 % 7 == 4 else i_g_1 + 1
                ),
                "op": "cz",
                "angle": 0,
            }
        )

    # create entangling and single qubit gates for relevant qubits in Steane Layer 3
    # CZs
    i_g = [1, 2, 3]
    for i_g_2 in [
        num + 7 * i
        for num in i_g
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[2].append(
            {
                "id": 0,
                "q0": i_g_2,
                "q1": (
                    i_g_2 + 3
                    if i_g_2 % 7 == 1
                    else i_g_2 - 2 if i_g_2 % 7 == 2 else i_g_2 + 2
                ),
                "op": "cz",
                "angle": 0,
            }
        )

    # Hadamards are in a separate layer to satisfy SLM constraints
    i_g = [2, 3, 4, 6]
    for i_g_single_2 in [
        num + 7 * i
        for num in i_g
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[3].append(
            {
                "id": 0,
                "q0": i_g_single_2,
                "q1": -1,
                "op": "ry",
                "angle": 0.5,
            }
        )

    # fault-tolerantly CNOT the ancillas with the reversible logical bits. Ancilla bits in SLM.
    for i_g_3 in [
        num
        for num in range(14 * i, (14 * i) + 7)
        for i in range(0, len(smt["layers"][0]["qubits"]) * 2)
    ]:
        steane_layer_gates[4].append(
            {
                "id": 0,
                "q0": i_g_3,
                "q1": i_g_3 + 7,
                "op": "cz",
                "angle": 0,
            }
        )

    steane = {"name": f"{smt['name']}_steane", "layers": []}

    # dump to steane output for animation processing on initialization stages
    for layer in range(NUM_STEANE_LAYERS - 1, -1, -1):
        steane["layers"].insert(
            0,
            {"qubits": steane_layer_qubits[layer], "gates": steane_layer_gates[layer]},
        )

    steane = smt | steane
    steane["n_q"] *= 14
    with open(dir + "steane_" + name, "w") as f:
        json.dump(steane, f)

    """
    TODO: add padding for the qubits at starting positions
    Two Steane codes for each qubit in initial set-up
    Non-fault tolerantly make Steane codes
    CNOT the pairs.
    Move the ancilla Steane code of each pair to readout zone
    Pad each additional layer
    """


if __name__ == "__main__":
    initialize_steane("./", "smt_QRISE.json")
