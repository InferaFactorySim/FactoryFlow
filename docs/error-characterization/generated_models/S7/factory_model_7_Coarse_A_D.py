"""
ModelDescription:
A sequence of 5 heterogeneous machines with parameters M1(delay 1.0, cap 1), M2(2.0, 2), M3(0.5, 5), M4(3.0, 1), M5(1.5, 3).

 MODEL ASSUMPTIONS:
1. Added a Source node at the beginning and a Sink node at the end of the sequence to form a complete flow.
2. Used the `Machine` node type for the 5 heterogeneous machines.
3. Used the `Buffer` edge type with capacity=2 for all connections between nodes. Buffer IDs are B1, B2, B3, B4, etc.
4. Connected the nodes in a linear series (Source → Machine 0 → ... → Machine 4 → Sink) with a single buffer between each adjacent pair.
5. Inferred node IDs: 'SRC' for the Source, 'SINK' for the Sink, and 'M1' through 'M5' for the machines.
6. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
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

        # Initializing source
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)

        # Initializing machines with heterogeneous parameters
        # Params: (processing_delay, work_capacity)
        machine_params = [
            (1.0, 1), # M1
            (2.0, 2), # M2
            (0.5, 5), # M3
            (3.0, 1), # M4
            (1.5, 3)  # M5
        ]
        
        self.machines = []
        for i, (delay, cap) in enumerate(machine_params):
            # IDs M1 through M5
            m = Machine(env, id=f"M{i+1}", processing_delay=delay, work_capacity=cap)
            self.machines.append(m)
        self.add_child_node(self.machines)

        # Initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Creating edges (Buffers)
        # Connecting Source -> M1 -> M2 -> M3 -> M4 -> M5 -> Sink
        # Buffer capacity is 2 for all connections
        nodes_sequence = [self.source] + self.machines + [self.sink]
        self.edges = []
        
        for i in range(len(nodes_sequence) - 1):
            edge = Buffer(env, id=f"edge[{i}]", capacity=2)
            self.add_child_edge(edge)
            edge.connect(nodes_sequence[i], nodes_sequence[i+1])
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