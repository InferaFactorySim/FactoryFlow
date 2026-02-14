"""
ModelDescription:
A series with 2 machines. There is a feedback loop that uses multiple parallel buffers( B_ret1, B_ret2, B_ret3) for the return path from M2 to M1. Let Source and sink ID be "SRC" and "SINK". If buffer IDs are not available name them as B_srcnodeID_destnodeID

 MODEL ASSUMPTIONS:
1. Inferred the presence of a Source node named 'src' connected to M1 and a Sink node named 'sink' connected to M2 to complete the manufacturing flow.
2. Assumed the machine identifiers are 'M1' and 'M2' based on the feedback path description.
3. Assumed the "multiple parallel buffers" in the feedback loop consists of exactly 3 buffers connecting M2 back to M1.
4. Used default edge type 'Buffer' for all connections (Source to M1, M1 to M2, M2 to Sink, and feedback paths) as edge types were not specified. M2's out_edge_policy is "ROUND_ROBIN"
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

        # Initializing Source
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)

        # Initializing Machines
        self.M1 = Machine(env, id="M1")
        # M2 with Round Robin out edge selection as per assumptions
        self.M2 = Machine(env, id="M2", out_edge_selection="ROUND_ROBIN")
        self.machines = [self.M1, self.M2]
        self.add_child_node(self.machines)

        # Initializing Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Creating Edges
        
        # Buffer from Source to M1
        self.b_src_m1 = Buffer(env, id="B_SRC_M1")
        self.add_child_edge(self.b_src_m1)
        self.b_src_m1.connect(self.source, self.M1)

        # Buffer from M1 to M2
        self.b_m1_m2 = Buffer(env, id="B_M1_M2")
        self.add_child_edge(self.b_m1_m2)
        self.b_m1_m2.connect(self.M1, self.M2)

        # Buffer from M2 to Sink
        self.b_m2_sink = Buffer(env, id="B_M2_SINK")
        self.add_child_edge(self.b_m2_sink)
        self.b_m2_sink.connect(self.M2, self.sink)

        # Feedback Buffers from M2 to M1 (B_ret1, B_ret2, B_ret3)
        self.feedback_buffers = []
        for i in range(1, 4):
            buf = Buffer(env, id=f"B_ret{i}")
            self.add_child_edge(buf)
            buf.connect(self.M2, self.M1)
            self.feedback_buffers.append(buf)

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