"""
ModelDescription:
M1 feeds M2. M2 feeds SINK. A return path exists from M2 back to M1, but it consists of 3 parallel buffers (B_ret1, B_ret2, B_ret3). M2 uses "ROUND_ROBIN" to distribute the feedback items across these 3 buffers. Let Source ID be "SRC". If buffer IDs are not available name them as B_srcnodeID_destnodeID

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Assumed SRC connects to M1 to initiate the flow.
3. Assumed M1 and M2 are of type Machine and SINK is of type Sink.
4. Used default edge type Buffer for connections between SRC and M1, M1 and M2, and M2 and SINK.
5. Used a single buffer for the forward connections (SRC to M1, M1 to M2, and M2 to SINK).
6. Named the inferred forward buffers as B_SRC_M1, B_M1_M2, and B_M2_SINK based on the requested naming convention.
7. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
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

        # Creating nodes
        # Source
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)

        # Machines
        self.M1 = Machine(env, id="M1")
        self.add_child_node(self.M1)

        # M2 with Round Robin output selection
        self.M2 = Machine(env, id="M2", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.M2)

        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Creating edges
        
        # Forward path buffers
        self.b_src_m1 = Buffer(env, id="B_SRC_M1")
        self.add_child_edge(self.b_src_m1)
        
        self.b_m1_m2 = Buffer(env, id="B_M1_M2")
        self.add_child_edge(self.b_m1_m2)
        
        self.b_m2_sink = Buffer(env, id="B_M2_SINK")
        self.add_child_edge(self.b_m2_sink)

        # Return path buffers (3 parallel buffers)
        self.return_buffers = [Buffer(env, id=f"B_ret{i+1}") for i in range(3)]
        self.add_child_edge(self.return_buffers)

        # Connecting nodes
        
        # SRC -> M1
        self.b_src_m1.connect(self.src, self.M1)
        
        # M1 -> M2
        self.b_m1_m2.connect(self.M1, self.M2)
        
        # M2 -> SINK
        self.b_m2_sink.connect(self.M2, self.sink)
        
        # M2 -> M1 (Feedback via 3 parallel buffers)
        for i in range(3):
            self.return_buffers[i].connect(self.M2, self.M1)

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