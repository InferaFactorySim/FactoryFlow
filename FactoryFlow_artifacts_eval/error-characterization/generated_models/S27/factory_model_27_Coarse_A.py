"""
ModelDescription:
A series with 2 machines. There is a feedback loop that uses multiple parallel buffers( B_ret1, B_ret2, B_ret3) for the return path from M2 to M1. Let Source and sink ID be "SRC" and "SINK". If buffer IDs are not available name them as B_srcnodeID_destnodeID

 MODEL ASSUMPTIONS:
1. Inferred the presence of a Source node named 'src' connected to M1 and a Sink node named 'sink' connected to M2 to complete the manufacturing flow.
2. Assumed the machine identifiers are 'M1' and 'M2' based on the feedback path description.
3. Assumed the "multiple parallel buffers" in the feedback loop consists of exactly 3 buffers connecting M2 back to M1.
4. Used default edge type 'Buffer' for all connections (Source to M1, M1 to M2, M2 to Sink, and feedback paths) as edge types were not specified.
5. Assumed single buffers are used for the forward connections (Source to M1, M1 to M2, M2 to Sink).
6. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
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

        # initializing source with ID "SRC"
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)
       
        # initializing machines M1 and M2
        # Assumption 2: Machine identifiers are 'M1' and 'M2'
        self.machines = [Machine(env, id=f"M{i}") for i in range(1, 3)]
        self.add_child_node(self.machines)
       
        # initializing sink with ID "SINK"
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # creating forward edges
        # Naming convention: B_srcnodeID_destnodeID
        
        # Buffer from Source to M1
        self.b_src_m1 = Buffer(env, id="B_SRC_M1")
        self.add_child_edge(self.b_src_m1)
        
        # Buffer from M1 to M2
        self.b_m1_m2 = Buffer(env, id="B_M1_M2")
        self.add_child_edge(self.b_m1_m2)
        
        # Buffer from M2 to Sink
        self.b_m2_sink = Buffer(env, id="B_M2_SINK")
        self.add_child_edge(self.b_m2_sink)

        # creating feedback edges (B_ret1, B_ret2, B_ret3)
        # Assumption 3: Exactly 3 buffers for the return path
        self.feedback_buffers = [Buffer(env, id=f"B_ret{i}") for i in range(1, 4)]
        self.add_child_edge(self.feedback_buffers)
    
        # connecting nodes with edges
        
        # Forward connections
        # Connect Source to M1
        self.b_src_m1.connect(self.source, self.machines[0])
        # Connect M1 to M2
        self.b_m1_m2.connect(self.machines[0], self.machines[1])
        # Connect M2 to Sink
        self.b_m2_sink.connect(self.machines[1], self.sink)
        
        # Feedback connections: M2 to M1 via parallel buffers
        for b in self.feedback_buffers:
            b.connect(self.machines[1], self.machines[0])

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