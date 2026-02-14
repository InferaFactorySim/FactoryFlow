"""
ModelDescription:
System has two machines M1and M2 with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to M1 and M1  to Sink via Buffers, B1, B2. M2 is connected parallel to M1 using Buffer B3 and B4. All buffers have a capacity of 2. Source and sink are common. All machines have a processing_Delay of 1.4

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description (Source: SRC, Machines: M1, M2, Sink: Sink).
2. Inferred a connection from Source (SRC) to M2 to satisfy the parallel configuration described, as M2 is stated to be parallel to M1.
3. Used default edge type 'Buffer' with default names for the connections from Source to M1 and Source to M2. Its IDs are B1 and B3
4. connection flow and ID are SRC-B1-M1-B2-Sink and SRC-B2-M2-B4-Sink. common src and sink.
5. Used processing_delay of 1.4 for M1 and M2, prioritizing the final statement "All machines have a processing_Delay of 1.4" over the initial mention of delay 2.
6. Applied capacity of 2 to all buffers, including the inferred input buffers from the Source, based on the statement "All buffers have a capacity of 2".
"""

# importing required libraries
import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # initializing machines
        # M1 and M2 with processing_delay 1.4
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.4) for i in range(2)]
        self.add_child_node(self.machines)
        
        # initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # initializing buffers
        # B1, B2, B3, B4 with capacity 2
        self.buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.buffers)
        
        # connecting nodes with edges
        # Branch 1: SRC -> B1 -> M1 -> B2 -> Sink
        # Branch 2: SRC -> B3 -> M2 -> B4 -> Sink
        for i in range(2):
            # Input buffers are B1 (idx 0) and B3 (idx 2)
            self.buffers[2*i].connect(self.source, self.machines[i])
            # Output buffers are B2 (idx 1) and B4 (idx 3)
            self.buffers[2*i+1].connect(self.machines[i], self.sink)

# initiliating simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)