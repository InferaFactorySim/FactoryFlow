"""
ModelDescription:
A system with two machines.

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
        
        # Initializing source with ID 'SRC' and delay 1.2
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # Initializing machines M1 and M2
        self.machines = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.machines)
        
        # Initializing sink with ID 'sink'
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges (Buffers) with capacity 2
        self.edges = []
        
        # Buffer from Source to M1
        b_src = Buffer(env, id="B_src_1", capacity=2)
        b_src.connect(self.source, self.machines[0])
        self.edges.append(b_src)
        
        # Buffer from M1 to M2
        b_mid = Buffer(env, id="B_1_2", capacity=2)
        b_mid.connect(self.machines[0], self.machines[1])
        self.edges.append(b_mid)
        
        # Buffer from M2 to Sink
        b_sink = Buffer(env, id="B_2_sink", capacity=2)
        b_sink.connect(self.machines[1], self.sink)
        self.edges.append(b_sink)
        
        # Adding edges to child edges
        self.add_child_edge(self.edges)

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