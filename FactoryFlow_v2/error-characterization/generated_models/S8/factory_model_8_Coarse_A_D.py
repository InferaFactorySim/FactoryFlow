"""
ModelDescription:
A linear sequence of 8 machines with delay 2 connected with a sink and a source. There are 4 buffers between 2 and 3rd machines and 6th and 7th machine.  Buffer IDs are inferred as B1, B2,.. the extra buffers as B3_1, B3_2, B3_3 and B7_1, B7_2, B7_3. add parameters later as TOP.M3.in_edge_selection="ROUND_ROBIN"

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Machine IDs are inferred as M1 through M8 to represent the sequence of 8 machines and Buffer IDs are  as B1, B2,.. the extra buffers IDs as B3_1, B3_2, B3_3 and B7_1, B7_2, B7_3.
3. Source ID is inferred as "SRC" and SINK ID as "sink".
4. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
5. Flow is assumed to be linear from Source to M[0], through the sequence to M[7], and finally to Sink.
6. Used a single buffer for all connections where the number of buffers was not explicitly specified (Source to M[0], M[0] to M[1], M[2] to M[3], M[3] to M[4], M[4] to M[5], M[6] to M[7], and M[7] to Sink).
7. The specified 4 buffers are placed between M[1] (2nd machine) and M[2] (3rd machine), and between M[5] (6th machine) and M[6] (7th machine).
8. in_edge_selection of M3 and M7 are "ROUND_ROBIN"
"""

import simpy, sys, os
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
        
        # Initializing machines M1 to M8
        self.machines = []
        for i in range(8):
            # M3 (index 2) and M7 (index 6) have ROUND_ROBIN in_edge_selection
            # All machines have processing_delay=2
            if i == 2 or i == 6:
                m = Machine(env, id=f"M{i+1}", processing_delay=2, in_edge_selection="ROUND_ROBIN")
            else:
                m = Machine(env, id=f"M{i+1}", processing_delay=2)
            self.machines.append(m)
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # List of nodes in sequence for easy connection
        nodes = [self.source] + self.machines + [self.sink]
        
        # Creating edges
        self.edges = []
        # Loop through the sequence to connect nodes
        # Connections: Src->M1 (0), M1->M2 (1), ..., M8->Sink (8)
        for i in range(len(nodes) - 1):
            u = nodes[i]
            v = nodes[i+1]
            
            # Primary buffer ID: B1, B2, ...
            b_id = f"B{i+1}"
            b = Buffer(env, id=b_id)
            self.add_child_edge(b)
            b.connect(u, v)
            self.edges.append(b)
            
            # Extra buffers for M2->M3 (index 2) and M6->M7 (index 6)
            if i == 2 or i == 6:
                for k in range(1, 4):
                    b_extra = Buffer(env, id=f"{b_id}_{k}")
                    self.add_child_edge(b_extra)
                    b_extra.connect(u, v)
                    self.edges.append(b_extra)

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