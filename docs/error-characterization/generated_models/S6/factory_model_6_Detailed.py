"""
ModelDescription:
System has 5 machines each with delay 2. 
 All machines are connected in parallel. SRC is connected to M1 and M1  to Sink via Buffers, B_SRC_1, B_1_SINK. 
 M2 is connected parallel to M1 using Buffer B_SRC_2 and B_2_SINK. and so on.All buffers have a capacity of 2.  
 System has a common source (ID= SRC) with inter arrival time of 0.2. and a common sink "SINK". All machines have a processing_Delay of 1.1

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred Machine IDs as M3, M4, and M5 following the pattern of M1 and M2.
3. Inferred Buffer IDs as B_SRC_3, B_3_SINK, B_SRC_4, B_4_SINK, B_SRC_5, and B_5_SINK following the pattern of B_SRC_1 and B_1_SINK.
4. Assumed processing_delay is 1.1 for all machines, overriding the conflicting earlier statement "delay 2".
5. Assumed the Source distributes entities to the 5 parallel branches using default routing logic.
6. Assumed the Sink collects entities from the 5 parallel branches using default logic.
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
        
        # creating nodes
        
        # initializing source
        self.source = Source(env, id="SRC", inter_arrival_time=0.2)
        self.add_child_node(self.source)
        
        # initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # initializing machines M1 to M5 with processing_delay 1.1
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.1) for i in range(5)]
        self.add_child_node(self.machines)
        
        # creating edges
        
        # initializing buffers from source to machines (B_SRC_1 to B_SRC_5)
        self.buffers_src = [Buffer(env, id=f"B_SRC_{i+1}", capacity=2) for i in range(5)]
        self.add_child_edge(self.buffers_src)
        
        # initializing buffers from machines to sink (B_1_SINK to B_5_SINK)
        self.buffers_sink = [Buffer(env, id=f"B_{i+1}_SINK", capacity=2) for i in range(5)]
        self.add_child_edge(self.buffers_sink)
        
        # connecting nodes with edges
        for i in range(5):
            # connect source to machine via buffer
            self.buffers_src[i].connect(self.source, self.machines[i])
            # connect machine to sink via buffer
            self.buffers_sink[i].connect(self.machines[i], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)