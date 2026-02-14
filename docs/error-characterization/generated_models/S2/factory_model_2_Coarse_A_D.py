"""
ModelDescription:
A system with two machine with delay 2

 MODEL ASSUMPTIONS:
1. Inferred the addition of a Source node at the beginning and a Sink node at the end to create a functional flow.
2. Assumed the two machines are connected in a linear series configuration (Source -> Machine 1 -> Machine 2 -> Sink).
3. Inferred node IDs as 'SRC' with delay 1.2 for the source, 'M1' and 'M2' for the machines, and 'sink' for the sink.
4. Assumed a single Buffer(capacity=2) connects each pair of adjacent nodes (Source to M1, M1 to M2, and M2 to Sink). Put Buffer IDs as B_src_1, B_1_2, and so on.
5. Used default values for all missing parameters (inter-arrival times, processing delays, and buffer capacities) for all components.
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

        # Initializing source based on Assumption 3
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)

        # Initializing machines based on Assumption 3 and Description
        # Two machines with delay 2, IDs M1 and M2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.machines)

        # Initializing sink based on Assumption 3
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # Creating sequence of nodes for linear connection
        nodes_seq = [self.source] + self.machines + [self.sink]

        # Initializing buffers based on Assumption 4
        # IDs: B_src_1, B_1_2, and inferred B_2_sink
        buffer_ids = ["B_src_1", "B_1_2", "B_2_sink"]
        self.buffers = []
        
        for i in range(len(nodes_seq) - 1):
            buf = Buffer(env, id=buffer_ids[i], capacity=2)
            self.buffers.append(buf)
            buf.connect(nodes_seq[i], nodes_seq[i+1])
            
        self.add_child_edge(self.buffers)

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