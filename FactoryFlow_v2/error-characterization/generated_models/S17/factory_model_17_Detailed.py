"""
ModelDescription:
A node named parallel_mac_3 has 3 machines in parallel. 2 such nodes are interconnected in a series and this is in parallel with a node named parallel_mac_2 which has 2 machines in parallel. The system has 2 sources but a common_sink. Name machine IDs as M1,M2 and buffers IDs as B1, B2,.. in every node. source as Src_1 and Src_2. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The sources have a interarrival time of 0.5

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. Defined a class `ParallelMac3` for the repeated node pattern containing 3 machines and `ParallelMac2` for the node pattern containing 2 machines.
3. Named the two instances of the 3-machine nodes connected in series as `parallel_mac_3_1` and `parallel_mac_3_2`.
4. Assumed `Src_1` connects to the input of the first 3-machine node (`parallel_mac_3_1`) and `Src_2` connects to the input of the 2-machine node (`parallel_mac_2`) to satisfy the parallel system structure with two sources.
5. Inferred that "machines in parallel" implies the preceding source or node connects to all machines within that node via separate buffers.
6. Inferred that the series connection between the two `parallel_mac_3` nodes implies connecting corresponding machines (M1 to M1, M2 to M2, M3 to M3) via buffers.
7. Assumed all machines in the final 3-machine node (`parallel_mac_3_2`) and all machines in the 2-machine node (`parallel_mac_2`) connect to the `common_sink` via separate buffers.
8. Used a single buffer for every connection between components where the number of buffers was not specified.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Class for the node with 3 machines in parallel
class ParallelMac3(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # 3 machines in parallel with IDs M1, M2, M3
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(3)]
        self.add_child_node(self.machines)

# Class for the node with 2 machines in parallel
class ParallelMac2(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # 2 machines in parallel with IDs M1, M2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.machines)

# Main System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating sources
        self.src1 = Source(env, id="Src_1", inter_arrival_time=0.5)
        self.src2 = Source(env, id="Src_2", inter_arrival_time=0.5)
        self.add_child_node([self.src1, self.src2])
        
        # Creating common sink
        self.sink = Sink(env, id="common_sink")
        self.add_child_node(self.sink)
        
        # Creating nodes
        self.pm3_1 = ParallelMac3(env, id="parallel_mac_3_1")
        self.pm3_2 = ParallelMac3(env, id="parallel_mac_3_2")
        self.pm2 = ParallelMac2(env, id="parallel_mac_2")
        self.add_child_node([self.pm3_1, self.pm3_2, self.pm2])
        
        # Creating edges
        self.edges = []
        edge_idx = 0
        
        # Connect Src_1 to parallel_mac_3_1 (fan-out to 3 machines)
        for i in range(3):
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.src1, self.pm3_1.machines[i])
            self.edges.append(buf)
            edge_idx += 1
            
        # Connect parallel_mac_3_1 to parallel_mac_3_2 (series connection of corresponding machines)
        for i in range(3):
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.pm3_1.machines[i], self.pm3_2.machines[i])
            self.edges.append(buf)
            edge_idx += 1
            
        # Connect parallel_mac_3_2 to common_sink (fan-in from 3 machines)
        for i in range(3):
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.pm3_2.machines[i], self.sink)
            self.edges.append(buf)
            edge_idx += 1
            
        # Connect Src_2 to parallel_mac_2 (fan-out to 2 machines)
        for i in range(2):
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.src2, self.pm2.machines[i])
            self.edges.append(buf)
            edge_idx += 1
            
        # Connect parallel_mac_2 to common_sink (fan-in from 2 machines)
        for i in range(2):
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.pm2.machines[i], self.sink)
            self.edges.append(buf)
            edge_idx += 1

# Initializing simpy environment
env = simpy.Environment()
# Creating system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)