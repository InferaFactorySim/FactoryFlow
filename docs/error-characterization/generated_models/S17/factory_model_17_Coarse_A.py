"""
ModelDescription:
A system with two nodes interconnected each with 3 machines in parallel. This is in parallel with another node with 2 machines in parallel. The system has 2 sources but a common_sink

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Machine, Sink, Buffer).
2. Inferred names `Src_1` and `Src_2` for the two sources, and `Common_Sink` for the sink.
3. Inferred a reusable class structure (e.g., `Parallel_mac_n`) for the "node with machines in parallel" pattern, which will be instantiated three times: twice with 3 machines (for the first interconnected branch) and once with 2 machines (for the parallel branch) where n=no. of machines in parallel. use ID also as Parallel_mac_n where n is no.of machines and if more than one node with ID Parallel_mac_n- use Parallel_mac_n_1 and Parallel_mac_n_2,....as ID for the nodes
4. Assumed the "two nodes interconnected" implies a series connection where the first node (3 machines) feeds into the second node (3 machines).
5. Assumed `Src_1` feeds the first node of the 3-machine series branch, and the second node of that branch feeds the `Common_Sink`.
6. Assumed `Src_2` feeds the single node of the 2-machine branch, which then feeds the `Common_Sink`.
7. Used `Buffer` for all edges as the default edge type.For all buffers inside class SystemModel use ID as B1, B2, B3 etc.
8. Used a single buffer for every connection between components (e.g., between Source and Machines, or Machines and Machines) where the number of buffers was not specified.
9. Assumed connections involving parallel machines distribute/collect flow via buffers connected to each machine individually (e.g., Source connects to all 3 machines via 3 buffers).
10. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Reusable class for a node with n machines in parallel
class Parallel_mac_n(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        # adding machines to child nodes
        self.add_child_node(self.M)

# Defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing sources
        self.Src_1 = Source(env, id="Src_1")
        self.Src_2 = Source(env, id="Src_2")
        self.source = [self.Src_1, self.Src_2]
        self.add_child_node(self.source)
        
        # initializing common sink
        self.Common_Sink = Sink(env, id="Common_Sink")
        self.sink = self.Common_Sink
        self.add_child_node(self.sink)
        
        # initializing parallel machine nodes
        # Branch 1: Two nodes interconnected (3 machines each)
        self.Parallel_mac_3_1 = Parallel_mac_n(env, id="Parallel_mac_3_1", n=3)
        self.Parallel_mac_3_2 = Parallel_mac_n(env, id="Parallel_mac_3_2", n=3)
        # Branch 2: One node (2 machines)
        self.Parallel_mac_2 = Parallel_mac_n(env, id="Parallel_mac_2", n=2)
        
        self.add_child_node([self.Parallel_mac_3_1, self.Parallel_mac_3_2, self.Parallel_mac_2])
        
        # creating edges (Buffers)
        self.buffers = []
        
        # Connecting Src_1 to Parallel_mac_3_1 (3 buffers)
        for i in range(3):
            b = Buffer(env, id=f"B{len(self.buffers)+1}")
            self.buffers.append(b)
            b.connect(self.Src_1, self.Parallel_mac_3_1.M[i])
            
        # Connecting Parallel_mac_3_1 to Parallel_mac_3_2 (3 buffers)
        for i in range(3):
            b = Buffer(env, id=f"B{len(self.buffers)+1}")
            self.buffers.append(b)
            b.connect(self.Parallel_mac_3_1.M[i], self.Parallel_mac_3_2.M[i])
            
        # Connecting Parallel_mac_3_2 to Common_Sink (3 buffers)
        for i in range(3):
            b = Buffer(env, id=f"B{len(self.buffers)+1}")
            self.buffers.append(b)
            b.connect(self.Parallel_mac_3_2.M[i], self.Common_Sink)
            
        # Connecting Src_2 to Parallel_mac_2 (2 buffers)
        for i in range(2):
            b = Buffer(env, id=f"B{len(self.buffers)+1}")
            self.buffers.append(b)
            b.connect(self.Src_2, self.Parallel_mac_2.M[i])
            
        # Connecting Parallel_mac_2 to Common_Sink (2 buffers)
        for i in range(2):
            b = Buffer(env, id=f"B{len(self.buffers)+1}")
            self.buffers.append(b)
            b.connect(self.Parallel_mac_2.M[i], self.Common_Sink)
            
        self.add_child_edge(self.buffers)

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)