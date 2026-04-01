"""
ModelDescription:
A system with two nodes interconnected each with 3 machines in parallel. This is in parallel with another node with 2 machines in parallel. The system has 2 sources but a common_sink.All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The sources have a interarrival time of 0.5. Sink ID is "SINK"

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Machine, Sink, Buffer).
2. Inferred names `Src_1` and `Src_2` for the two sources, and `Common_Sink` for the sink.
3. Inferred a reusable class structure (e.g., `Parallel_mac_n`) for the "node with machines in parallel" pattern, which will be instantiated three times: twice with 3 machines (for the first interconnected branch) and once with 2 machines (for the parallel branch) where n=no. of machines in parallel. use ID also as Parallel_mac_n where n is no.of machines and if more than one node with ID Parallel_mac_n- use Parallel_mac_n_1 and Parallel_mac_n_2,....as ID for the nodes
4. Assumed the "two nodes interconnected" implies a series connection where the first node (3 machines) feeds into the second node (3 machines).
5. Assumed `Src_1` feeds the first node of the 3-machine series branch, and the second node of that branch feeds the `SINK`.
6. Assumed `Src_2` feeds the single node of the 2-machine branch, which then feeds the `SINK`.
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

# Reusable class for parallel machines
class Parallel_mac_n(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        # Creating n machines in parallel with processing delay 2
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=2) for i in range(n)]
        self.add_child_node(self.M)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Sources with interarrival time 0.5
        self.Src_1 = Source(env, id="Src_1", inter_arrival_time=0.5)
        self.add_child_node(self.Src_1)
        
        self.Src_2 = Source(env, id="Src_2", inter_arrival_time=0.5)
        self.add_child_node(self.Src_2)
        
        self.sources = [self.Src_1, self.Src_2]
        
        # Creating Common Sink
        self.Common_Sink = Sink(env, id="SINK")
        self.add_child_node(self.Common_Sink)
        self.sink = self.Common_Sink
        
        # Creating Parallel Nodes
        # Branch 1: Two nodes with 3 machines each
        self.Parallel_mac_3_1 = Parallel_mac_n(env, id="Parallel_mac_3_1", n=3)
        self.add_child_node(self.Parallel_mac_3_1)
        
        self.Parallel_mac_3_2 = Parallel_mac_n(env, id="Parallel_mac_3_2", n=3)
        self.add_child_node(self.Parallel_mac_3_2)
        
        # Branch 2: One node with 2 machines
        self.Parallel_mac_2 = Parallel_mac_n(env, id="Parallel_mac_2", n=2)
        self.add_child_node(self.Parallel_mac_2)
        
        # Creating Edges (Buffers) with capacity 2
        # Total buffers: 
        # Src_1 -> Parallel_mac_3_1 (3 buffers)
        # Parallel_mac_3_1 -> Parallel_mac_3_2 (3 buffers)
        # Parallel_mac_3_2 -> Common_Sink (3 buffers)
        # Src_2 -> Parallel_mac_2 (2 buffers)
        # Parallel_mac_2 -> Common_Sink (2 buffers)
        # Total = 13
        
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(13)]
        self.add_child_edge(self.B)
        
        idx = 0
        
        # Connecting Branch 1
        # Src_1 to Parallel_mac_3_1
        for i in range(3):
            self.B[idx].connect(self.Src_1, self.Parallel_mac_3_1.M[i])
            idx += 1
            
        # Parallel_mac_3_1 to Parallel_mac_3_2
        for i in range(3):
            self.B[idx].connect(self.Parallel_mac_3_1.M[i], self.Parallel_mac_3_2.M[i])
            idx += 1
            
        # Parallel_mac_3_2 to Common_Sink
        for i in range(3):
            self.B[idx].connect(self.Parallel_mac_3_2.M[i], self.Common_Sink)
            idx += 1
            
        # Connecting Branch 2
        # Src_2 to Parallel_mac_2
        for i in range(2):
            self.B[idx].connect(self.Src_2, self.Parallel_mac_2.M[i])
            idx += 1
            
        # Parallel_mac_2 to Common_Sink
        for i in range(2):
            self.B[idx].connect(self.Parallel_mac_2.M[i], self.Common_Sink)
            idx += 1

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