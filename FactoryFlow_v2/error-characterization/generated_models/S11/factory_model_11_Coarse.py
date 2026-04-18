"""
ModelDescription:
Parts flow from two machines and merge to one path and enters a  machine

 MODEL ASSUMPTIONS:
1. Inferred node names: `Source` for the input, `M1` and `M2` for the two initial machines, `M3` for the final machine, and `Sink` for the output.
2. Added `Source` and `Sink` nodes to complete the simulation flow as they were not specified.
3. Used `Machine` node type for all processing units.
4. Used `Buffer` edge type for all connections.
5. Assumed the `Source` connects to both `M1` and `M2` to initiate the flow.
6. Assumed `M1` and `M2` both connect to `M3` to represent the merging of paths into the final machine.
7. Assumed `M3` connects to `Sink`.
8. Used a single buffer for each connection between nodes.
9. Used default values for all missing parameters (processing delays, inter-arrival times, capacities).
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # Creating Source
        self.source = Source(env, id="Source", inter_arrival_time=1.0)
        self.add_child_node(self.source)

        # Creating Initial Machines (M1, M2)
        self.initial_machines = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.initial_machines)

        # Creating Final Machine (M3)
        self.final_machine = Machine(env, id="M3")
        self.add_child_node(self.final_machine)

        # Creating Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)

        # Creating Edges
        self.edges = []
        edge_idx = 0

        # Connecting Source to M1 and M2
        for i in range(2):
            edge = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(edge)
            edge.connect(self.source, self.initial_machines[i])
            self.edges.append(edge)
            edge_idx += 1

        # Connecting M1 and M2 to M3
        for i in range(2):
            edge = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(edge)
            edge.connect(self.initial_machines[i], self.final_machine)
            self.edges.append(edge)
            edge_idx += 1

        # Connecting M3 to Sink
        edge = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(edge)
        edge.connect(self.final_machine, self.sink)
        self.edges.append(edge)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system model
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)