"""
ModelDescription:
System has two machines M1and M2 with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to M1 and M1  to Sink via Buffers, B1, B2. M2 is connected parallel to M1 using Buffer B3 and B4. All buffers have a capacity of 2. Source and sink are common. All machines have a processing_Delay of 1.4

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description (Source: SRC, Machines: M1, M2, Sink: Sink).
2. Inferred a connection from Source (SRC) to M2 to satisfy the parallel configuration described, as M2 is stated to be parallel to M1.
3. Used default edge type 'Buffer' with default names for the connections from Source to M1 and Source to M2, as these specific edges were not named in the description.
4. Assumed B1 and B2 are parallel buffers connecting M1 to Sink, and B3 and B4 are parallel buffers connecting M2 to Sink, because connecting buffers directly in series without intermediate nodes is not supported.
5. Used processing_delay of 1.4 for M1 and M2, prioritizing the final statement "All machines have a processing_Delay of 1.4" over the initial mention of delay 2.
6. Applied capacity of 2 to all buffers, including the inferred input buffers from the Source, based on the statement "All buffers have a capacity of 2".
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
        self.src = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.src)
        
        # Initializing machines M1 and M2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.4) for i in range(2)]
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Creating edges from Source to Machines (inferred names)
        self.src_edges = [Buffer(env, id=f"edge[{i}]", capacity=2) for i in range(2)]
        self.add_child_edge(self.src_edges)
        
        # Connecting Source to M1 and M2
        for i in range(2):
            self.src_edges[i].connect(self.src, self.machines[i])
            
        # Creating edges from M1 to Sink (B1, B2)
        self.m1_edges = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.m1_edges)
        
        # Connecting M1 to Sink via B1, B2
        for edge in self.m1_edges:
            edge.connect(self.machines[0], self.sink)
            
        # Creating edges from M2 to Sink (B3, B4)
        self.m2_edges = [Buffer(env, id=f"B{i+3}", capacity=2) for i in range(2)]
        self.add_child_edge(self.m2_edges)
        
        # Connecting M2 to Sink via B3, B4
        for edge in self.m2_edges:
            edge.connect(self.machines[1], self.sink)

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