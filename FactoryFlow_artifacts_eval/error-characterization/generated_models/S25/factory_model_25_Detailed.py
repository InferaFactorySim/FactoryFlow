"""
ModelDescription:
SRC -> M1 -> M2 -> M3 -> M4 -> SINK. Inner Loop: 30% of M2 output goes back to M1. Outer Loop: 10% of M4 output goes back to M1. All machines delay 2, all buffers capacity 2. Name buffer IDs as B_srcnodeID_destinationnodeID

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Default inter-arrival time (1.0) assumed for Source 'SRC'.
3. Used 'Buffer' class for all edges with a single buffer between connected nodes.
4. M2 output routing assumed to be probabilistic: 30% to M1, remaining 70% to M3.
5. M4 output routing assumed to be probabilistic: 10% to M1, remaining 90% to SINK.
6. No repeated patterns detected, so a single SystemModel class will be used.
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
        self.src = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.src)
        
        # Initializing machines M1 to M4 with processing delay 2
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(4)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Initializing edges
        self.edges = []
        
        # Defining connections based on description
        # Format: (Source Node, Destination Node, Buffer ID)
        # M1 is M[0], M2 is M[1], M3 is M[2], M4 is M[3]
        connections = [
            (self.src, self.M[0], "B_SRC_M1"),       # SRC -> M1
            (self.M[0], self.M[1], "B_M1_M2"),       # M1 -> M2
            (self.M[1], self.M[2], "B_M2_M3"),       # M2 -> M3 (70%)
            (self.M[1], self.M[0], "B_M2_M1"),       # M2 -> M1 (30%)
            (self.M[2], self.M[3], "B_M3_M4"),       # M3 -> M4
            (self.M[3], self.sink, "B_M4_SINK"),     # M4 -> SINK (90%)
            (self.M[3], self.M[0], "B_M4_M1")        # M4 -> M1 (10%)
        ]
        
        # Creating and connecting buffers
        for src_node, dst_node, buf_id in connections:
            buf = Buffer(env, id=buf_id, capacity=2)
            self.edges.append(buf)
            buf.connect(src_node, dst_node)
            
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