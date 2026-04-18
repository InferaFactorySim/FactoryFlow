"""
ModelDescription:
 There’s a subsytem A where a single machine is connected to 3.
machines in parallel which are then connected to another common machine. 
This subsytem is connected to another subsystem B having 2 machines in series. 
B is again connected to A. Now this whole ABA thing is repeated 3 times and is 
connected in series.Name machines as M1,M2, and Buffers as B1,B2,.. 
All machines have a processing_Delay of 2 and buffers have a capacity of 2. 
THE work_capacity of the machine following the multi-edge be 4 with in_edge_selction as "ROUND_ROBIN.
The system has a source with ID="SRC and sink with ID=SINK. Machine ID with in a subsystemA are M_1 M1,M2,M3 and M_2 and 
Buffer IDs are B_M1_1, B_M1_2, B_M1_3 and B_1_M2, B_2_M2, B_3_M2 and subsystem B are M1, M2 and B1, 
B2,etc. The buffers with IDs  Binter1 and Binter2  for joining A, B, A together and to add 
multiple ABA together buffers with ID B1, B2, B3,.. are used

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Source inter_arrival_time is assumed to be default.
3. In Subsystem A, M_1 is the split node connecting to M1, M2, M3 via buffers B_M1_1, B_M1_2, and B_M1_3 respectively.
4. In Subsystem A, M1, M2, M3 connect to the merge node M_2 via buffers B_1_M2, B_2_M2, and B_3_M2 respectively.
5. The machine M_2 in Subsystem A is identified as the machine following the multi-edge, having work_capacity=4 and in_edge_selection="ROUND_ROBIN".
6. In Subsystem B, M1 connects to M2 via buffer B1.
7. The ABA sequence is constructed as: Subsystem A (1) -> Buffer Binter1 -> Subsystem B -> Buffer Binter2 -> Subsystem A (2).
8. Three such ABA blocks are connected in series. Block 1 connects to Block 2 via Buffer B1 (global context), and Block 2 connects to Block 3 via Buffer B2 (global context).
9. The Source connects to the first machine (M_1) of the first ABA block via a default buffer.
10. The last machine (M_2) of the last ABA block connects to the Sink via a default buffer.
11. Used default values for all missing parameters (such as out_edge_selection for split nodes) for all components.
12. A single buffer is used for every connection between nodes where the number of buffers is not explicitly specified.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Subsystem A: M_1 -> (M1, M2, M3) -> M_2
class SubsystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Split Node M_1
        self.M_1 = Machine(env, id="M_1", processing_delay=2)
        self.add_child_node(self.M_1)
        
        # Parallel Machines M1, M2, M3
        self.parallel_M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(3)]
        self.add_child_node(self.parallel_M)
        
        # Merge Node M_2
        # work_capacity=4 and in_edge_selection="ROUND_ROBIN" as per description
        self.M_2 = Machine(env, id="M_2", processing_delay=2, work_capacity=4, in_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.M_2)
        
        # Buffers from M_1 to Parallel Machines: B_M1_1, B_M1_2, B_M1_3
        self.buffers_split = [Buffer(env, id=f"B_M1_{i+1}", capacity=2) for i in range(3)]
        self.add_child_edge(self.buffers_split)
        
        # Buffers from Parallel Machines to M_2: B_1_M2, B_2_M2, B_3_M2
        self.buffers_merge = [Buffer(env, id=f"B_{i+1}_M2", capacity=2) for i in range(3)]
        self.add_child_edge(self.buffers_merge)
        
        # Connecting M_1 -> Parallel -> M_2
        for i in range(3):
            self.buffers_split[i].connect(self.M_1, self.parallel_M[i])
            self.buffers_merge[i].connect(self.parallel_M[i], self.M_2)
            
        self.entry = self.M_1
        self.exit = self.M_2

# Subsystem B: M1 -> B1 -> M2
class SubsystemB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Machines M1, M2
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        # Buffer B1
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        # Connection
        self.B1.connect(self.M[0], self.M[1])
        
        self.entry = self.M[0]
        self.exit = self.M[1]

# ABA Block: A -> Binter1 -> B -> Binter2 -> A
class ABABlock(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Subsystems
        self.A1 = SubsystemA(env, id="A_1")
        self.B = SubsystemB(env, id="B")
        self.A2 = SubsystemA(env, id="A_2")
        self.add_child_node([self.A1, self.B, self.A2])
        
        # Inter-subsystem buffers
        self.Binter1 = Buffer(env, id="Binter1", capacity=2)
        self.Binter2 = Buffer(env, id="Binter2", capacity=2)
        self.add_child_edge([self.Binter1, self.Binter2])
        
        # Connections
        self.Binter1.connect(self.A1.exit, self.B.entry)
        self.Binter2.connect(self.B.exit, self.A2.entry)
        
        self.entry = self.A1.entry
        self.exit = self.A2.exit

# Top Level System
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # 3 ABA Blocks
        self.blocks = [ABABlock(env, id=f"Block[{i}]") for i in range(3)]
        self.add_child_node(self.blocks)
        
        # Global Buffers B1, B2 connecting blocks
        self.global_buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.global_buffers)
        
        # Source to Block 0
        self.src_edge = Buffer(env, id="src_edge", capacity=2)
        self.add_child_edge(self.src_edge)
        self.src_edge.connect(self.src, self.blocks[0].entry)
        
        # Connect Blocks: Block0 -> B1 -> Block1 -> B2 -> Block2
        for i in range(2):
            self.global_buffers[i].connect(self.blocks[i].exit, self.blocks[i+1].entry)
            
        # Block 2 to Sink
        self.sink_edge = Buffer(env, id="sink_edge", capacity=2)
        self.add_child_edge(self.sink_edge)
        self.sink_edge.connect(self.blocks[-1].exit, self.sink)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)