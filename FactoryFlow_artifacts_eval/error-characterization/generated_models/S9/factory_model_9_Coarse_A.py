"""
ModelDescription:
There’s a subsytem with ID "A" where a single machine is connected to 3 machines in parallel which are then connected to another common machine. this subsytem is connected to another subsystem with ID "B"  having 2 machines in series. B is again connected to A. Now this whole ABA thing is repeated 3 times and is connected in series.  all machines have delay 2 and buffers have capacity=2

 MODEL ASSUMPTIONS:
1. Added a Source "SRC" node at the beginning of the system and a Sink "SINK" node at the end of the system to ensure a complete flow, as they were not specified in the description.
2. Created specific classes for Subsystem "A" and Subsystem "B" to handle the repeated patterns described.
3. In Subsystem A, M_1 is the split node connecting to M1, M2, M3 via buffers B_M1_1, and so on.
4. In Subsystem A, M1, M2, M3 connect to the merge node M_2 via buffers B_1_M2, B_2_M2, and so on
5. The machine M_2 in Subsystem A is identified as the machine following the multi-edge, having work_capacity=4 and in_edge_selection="ROUND_ROBIN".
6. In Subsystem B, M1 connects to M2 via buffer B1.
7. The ABA sequence is constructed as:  Buffer Binter1 and Buffer Binter2 are used to connect SubsystemsA1, B and A2.
8. Three such ABA blocks are connected in series. Block 1 connects to Block 2 via Buffer B1 , and Block 2 connects to Block 3 via Buffer B2 .
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

# Subsystem A: Single machine connected to 3 parallel machines, then to a common machine
class SubsystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # M_1: Split node
        self.M_1 = Machine(env, id="M_1", processing_delay=2)
        self.add_child_node(self.M_1)
        
        # Parallel machines M1, M2, M3
        self.parallel_machines = [Machine(env, id=f"M[{i+1}]", processing_delay=2) for i in range(3)]
        self.add_child_node(self.parallel_machines)
        
        # M_2: Merge node with specific capacity and selection rule
        self.M_2 = Machine(env, id="M_2", processing_delay=2, work_capacity=4, in_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.M_2)
        
        # Buffers from M_1 to parallel machines
        self.buffers_split = [Buffer(env, id=f"B_M1_{i+1}", capacity=2) for i in range(3)]
        self.add_child_edge(self.buffers_split)
        
        # Buffers from parallel machines to M_2
        self.buffers_merge = [Buffer(env, id=f"B_{i+1}_M2", capacity=2) for i in range(3)]
        self.add_child_edge(self.buffers_merge)
        
        # Connecting nodes
        for i in range(3):
            self.buffers_split[i].connect(self.M_1, self.parallel_machines[i])
            self.buffers_merge[i].connect(self.parallel_machines[i], self.M_2)
            
        # Expose entry and exit points
        self.entry = self.M_1
        self.exit = self.M_2

# Subsystem B: 2 machines in series
class SubsystemB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.M1 = Machine(env, id="M1", processing_delay=2)
        self.M2 = Machine(env, id="M2", processing_delay=2)
        self.add_child_node([self.M1, self.M2])
        
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        self.B1.connect(self.M1, self.M2)
        
        self.entry = self.M1
        self.exit = self.M2

# ABA Block: Subsystem A -> Subsystem B -> Subsystem A
class ABABlock(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.A1 = SubsystemA(env, id="A1")
        self.B = SubsystemB(env, id="B")
        self.A2 = SubsystemA(env, id="A2")
        self.add_child_node([self.A1, self.B, self.A2])
        
        self.Binter1 = Buffer(env, id="Binter1", capacity=2)
        self.Binter2 = Buffer(env, id="Binter2", capacity=2)
        self.add_child_edge([self.Binter1, self.Binter2])
        
        self.Binter1.connect(self.A1.exit, self.B.entry)
        self.Binter2.connect(self.B.exit, self.A2.entry)
        
        self.entry = self.A1.entry
        self.exit = self.A2.exit

# Overall System: 3 ABA Blocks in series
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)
        
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        self.blocks = [ABABlock(env, id=f"Block[{i}]") for i in range(3)]
        self.add_child_node(self.blocks)
        
        # Connect Source to first block
        self.e_src = Buffer(env, id="e_src", capacity=2)
        self.add_child_edge(self.e_src)
        self.e_src.connect(self.source, self.blocks[0].entry)
        
        # Connect blocks in series
        self.inter_block_edges = []
        for i in range(2):
            buf = Buffer(env, id=f"B{i+1}", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.blocks[i].exit, self.blocks[i+1].entry)
            self.inter_block_edges.append(buf)
            
        # Connect last block to Sink
        self.e_sink = Buffer(env, id="e_sink", capacity=2)
        self.add_child_edge(self.e_sink)
        self.e_sink.connect(self.blocks[-1].exit, self.sink)

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