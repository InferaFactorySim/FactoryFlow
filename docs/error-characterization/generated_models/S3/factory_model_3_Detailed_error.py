"""
ModelDescription:
System has two machines M1and M2 with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to M1 and M1  to Sink via Buffers, B1, B2. M2 is connected parallel to M1 using Buffer B3 and B4. All buffers have a capacity of 2. Source and sink are common. All machines have a processing_Delay of 1.4

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description. Inferred Sink name as 'sink'.
2. Assumed the system topology consists of two parallel branches sharing the common Source 'SRC' and Sink 'sink'.
3. Assumed the connection sequence for the first branch is Source -> Buffer B1 -> Machine M1 -> Buffer B2 -> Sink.
4. Assumed the connection sequence for the second branch is Source -> Buffer B3 -> Machine M2 -> Buffer B4 -> Sink.
5. Assumed processing delay is 1.4 for all machines, overriding the conflicting value of 2 mentioned earlier in the description.
6. Used default values for any other missing parameters.
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
        
        # initializing source
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing machines M1 and M2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.4) for i in range(2)]
        self.add_child_node(self.machines)
        
        # initializing buffers
        # 2 branches * 2 buffers per branch = 4 buffers
        self.edges = [Buffer(env, id=f"edge[{i}]", capacity=2) for i in range(4)]
        self.add_child_edge(self.edges)
        
        # connecting nodes with edges
        for i in range(2):
            # Connect Source -> Buffer -> Machine
            # Branch 1 (i=0): edge[0] connects SRC to M1
            # Branch 2 (i=1): edge[2] connects SRC to M2
            self.edges[2*i].connect(self.source, self.machines[i])
            
            # Connect Machine -> Buffer -> Sink
            # Branch 1 (i=0): edge[1] connects M1 to Sink
            # Branch 2 (i=1): edge[3] connects M2 to Sink
            self.edges[2*i+1].connect(self.machines[i], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)