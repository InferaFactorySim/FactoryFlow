"""
ModelDescription:
SRC(0.3)-M1-M2-Sink. one output of M2 goes back to M1 also. All connections are via single buffers. Name buffers B1, B2,..  All machines have a processing_Delay of 2 and buffers have a capacity of 2. 

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Buffers are named B1, B2, B3, and B4 sequentially for the connections: SRC to M1, M1 to M2, M2 to Sink, and the feedback loop M2 to M1.
3. Assumed a uniform split ratio for Machine M2 to distribute parts between the Sink and the feedback loop to M1.
4. Assumed default merge logic for Machine M1 to handle incoming parts from both the Source and the feedback loop.
"""

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
        self.src = Source(env, id="SRC", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines
        # M1 and M2 with processing_delay=2
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # initializing buffers with capacity 2
        # B1: SRC -> M1
        # B2: M1 -> M2
        # B3: M2 -> Sink
        # B4: M2 -> M1 (Feedback)
        self.buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.buffers)
        
        # connecting nodes with edges
        # SRC to M1
        self.buffers[0].connect(self.src, self.M[0])
        # M1 to M2
        self.buffers[1].connect(self.M[0], self.M[1])
        # M2 to Sink
        self.buffers[2].connect(self.M[1], self.sink)
        # M2 to M1 (feedback)
        self.buffers[3].connect(self.M[1], self.M[0])

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)