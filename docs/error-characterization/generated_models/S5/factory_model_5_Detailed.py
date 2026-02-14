"""
ModelDescription:
System has 5 machines each with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. All machines are interconnected via buffers. Name buffers as B1, B2, B3,.. and Machines as M1,M2,... All buffers have a capacity of 2. The sequence ends in a sink (ID=SINK). All machines have a processing_Delay of 2 and buffers have a capacity of 2. 

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Inferred a linear topology where the Source connects to M1, M1 connects to M2, M2 to M3, M3 to M4, M4 to M5, and M5 connects to the Sink.
3. Assumed a single buffer connects each pair of adjacent nodes in the sequence.
4. Assumed Buffer IDs (B1 to B6) are assigned sequentially along the flow: B1 connects Source to M1, B2 connects M1 to M2, B3 connects M2 to M3, B4 connects M3 to M4, B5 connects M4 to M5, and B6 connects M5 to Sink.
5. Assumed Machine IDs (M1 to M5) are assigned in ascending order corresponding to their position in the sequence from Source to Sink.
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
        
        # System Parameters based on description
        num_machines = 5
        processing_delay = 2
        buffer_capacity = 2
        inter_arrival_time = 1.2

        # Initializing Source
        self.source = Source(env, id="SRC", inter_arrival_time=inter_arrival_time)
        self.add_child_node(self.source)

        # Initializing Machines M1 to M5
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=processing_delay) for i in range(num_machines)]
        self.add_child_node(self.machines)

        # Initializing Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Defining the linear sequence of nodes for connection
        # Sequence: Source -> M1 -> M2 -> M3 -> M4 -> M5 -> Sink
        nodes_sequence = [self.source] + self.machines + [self.sink]

        # Creating Buffers and connecting nodes
        # Buffers B1 to B6 connect the 7 nodes in sequence
        self.buffers = []
        for i in range(len(nodes_sequence) - 1):
            buf = Buffer(env, id=f"B{i+1}", capacity=buffer_capacity)
            self.add_child_edge(buf)
            buf.connect(nodes_sequence[i], nodes_sequence[i+1])
            self.buffers.append(buf)

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)