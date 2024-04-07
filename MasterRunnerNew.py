import json
import math
from solve import DPQA
from typing import Any

# from QRISEAnimations.Atomique import Block, QCircuit, Animation


class Runner:
    """
    Master runner for compiling gate deconstruction, two-qubit gate filtering, SMT solver, and animation

    Note: Two-qubit gate filtering is supported by the methods in Tan, Daniel et. al. (Appendix F).
    We note that arbitrary single-qubit gate execution may cause crosstalk in the real hardware case
    where single-qubit gate pulses play on adjacent qubits which is not currently constrained by the SMT solver.
    """
    def __init__(self, name: str, dir: str):
        self.dir = dir
        self.name = name

    def decompose(self):
        # TODO: run Kevin's function
        pass

    def parse_json(self):
        """
        Separate the single-qubit and two-qubit gates while preserving order
        """
        # load Kevin's .json circuit, the file path will likely change !!!
        with open(self.dir + self.name, "r") as f:
            data = json.load(f)

        # find single and two-qubit gates
        twos = [
            (i, q['qubits'])
            for i, q in enumerate(data['experiments'][0]['instructions'])
            if len(q['qubits']) == 2 and isinstance(q['qubits'][1], int)
        ]

        gates = [
            [
                q['qubits'][0], 
                q['name'], 
                round(q['params'][0] / math.pi, 5) # get multiple of pi rotation for clean animation representation
                ] 
            if len(q['qubits']) == 1 and q['name'] != 'measure'
            else [q['qubits'][0], 'm', 0.0] if q['name'] == 'measure'
            else q['qubits'] 
            for q in data['experiments'][0]['instructions']
        ]

        # dump 'em
        with open(self.dir + "twos_" + self.name, "w") as f:
            json.dump(twos, f)

        with open(self.dir + "all_" + self.name, "w") as f:
            json.dump(gates, f)

    def SMT(self):
        """
        Runs the SMT on Kevin's deconstructed and two-qubit gate filtered .json
        TODO: remove argparse and just run the damn thing
        """
        twos_json = self.dir + "twos_" + self.name

        with open(twos_json, "r") as f:
            graphs = json.load(f)

        twos_unindexed = [q[1] for q in graphs]

        input_name = "smt_" + self.name[:-5]

        tmp = DPQA(
            name=input_name,
            dir=self.dir if self.dir else "./results/smt/",
            print_detail=False,
        )
        tmp.setArchitecture([16, 16, 16, 16])
        tmp.setProgram(twos_unindexed)
        tmp.hybrid_strategy()
        tmp.solve(save_file=True)

    def singles_reinsert(self):
        """
        Reinserts the single-qubit gates at the beginning of the ['gates'] key per each layer
        of the SMT output .json
        TODO: check to see if this actually works.
        """

        all_json = self.dir + "all_" + self.name
        with open(all_json, "r") as f:
            gates: list[tuple[int, str, float] | tuple[int, int]] = json.load(f)

        # load the json output from SMT solver
        smt_json = self.dir + "smt_" + self.name
        with open(smt_json, "r") as f:
            smt = json.load(f)

        # get a mapping from double gate ids to initial ids
        id_mapping: dict[int, int] = dict()
        double_id = 0
        for i, gate in enumerate(gates):
            if isinstance(gate[1], int):
                id_mapping[double_id] = i
                double_id += 1

        # get the layer of each double gate for quick lookup
        double_layers: dict[int, int] = {}
        for i in range(len(smt["layers"])):
            for j, gate in enumerate(smt["layers"][i]["gates"]):
                smt["layers"][i]["gates"][j]["id"] = id_mapping[gate["id"]]
                double_layers[gate["id"]] = i

        # Keep track of which layer each qubid was last seen in as a part of a two-qubit gate
        # and insert each single gate as early as possible
        last_seen: dict[int, int] = {}
        additional_layer: list[dict[str, Any]] = []
        for i, gate in enumerate(gates):
            if isinstance(gate[1], str):
                layer = last_seen.get(gate[0], -1) + 1
                new_gate = {"id": i, "q": gate[0], "op": gate[1], "angle": gate[2]}
                if layer < len(smt["layers"]):
                    smt["layers"][layer]["gates"].insert(0, new_gate)
                else:
                    additional_layer.append(new_gate)
            else:
                if last_seen.get(gate[0], -1) < double_layers[i]:
                    last_seen[gate[0]] = double_layers[i]
                if last_seen.get(gate[1], -1) < double_layers[i]:
                    last_seen[gate[1]] = double_layers[i]

        # add a new layer only for single gates if needed
        if additional_layer:
            smt["layers"].append(
                {
                    "qubits": smt["layers"][-1]["qubits"],
                    "gates": additional_layer,
                }
            )

        # dump to smt_json
        with open(smt_json, "w") as f:
            json.dump(smt, f)

    def animate(self):
        # TODO: Run Dmitrii and David's animation
        pass


run = Runner(name="QRISE.json", dir="./")

run.parse_json()
run.SMT()
run.singles_reinsert()
