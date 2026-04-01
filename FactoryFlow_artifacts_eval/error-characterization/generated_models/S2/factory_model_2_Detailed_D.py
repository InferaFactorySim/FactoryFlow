"""
ModelDescription:
System has two machines M1and M2 with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to M1 and M1 to M2 and M2 to Sink via Buffers, B_src_1, B_1_2, B_2_3,... All buffers have a capacity of 2.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Assumed the ID of the Sink node is "sink" as it was not specified.
3. Assumed the buffer connecting SRC to M1 is named "B_src_1", the buffer connecting M1 to M2 is named "B_1_2", and the buffer connecting M2 to Sink is named "B_2_sink" based on the naming pattern provided in the description.
4. Assumed a single buffer is used between each pair of connected nodes.
5. Assumed the top-level system node is named "TOP".
6. Assumed a simulation time of 25 units.
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
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # Initializing machines M1 and M2
        self.M = [Machine(env, id=f"M{i}", processing_delay=2) for i in range(1, 3)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing buffers with specific IDs
        buffer_ids = ["B_src_1", "B_1_2", "B_2_sink"]
        self.buffers = [Buffer(env, id=bid, capacity=2) for bid in buffer_ids]
        self.add_child_edge(self.buffers)
        
        # Connecting nodes with edges
        # Sequence: Source -> M1 -> M2 -> Sink
        nodes_sequence = [self.source] + self.M + [self.sink]
        
        for i in range(len(self.buffers)):
            self.buffers[i].connect(nodes_sequence[i], nodes_sequence[i+1])

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