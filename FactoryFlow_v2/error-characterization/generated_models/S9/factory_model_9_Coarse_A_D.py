"""
ModelDescription:
There’s a subsytem with ID "A" where a single machine is connected to 3 machines in parallel which are then connected to another common machine. this subsytem is connected to another subsystem with ID "B"  having 2 machines in series. B is again connected to A. Now this whole ABA thing is repeated 3 times and is connected in series.  all machines have delay 2 and buffers have capacity=2

 MODEL ASSUMPTIONS:
1. Added a Source "SRC" node at the beginning of the system and a Sink "SINK" node at the end of the system to ensure a complete flow, as they were not specified in the description.
2. Created specific classes for Subsystem "A" and Subsystem "B" to handle the repeated patterns described.
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

class SubsystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # M_1 is the split node
        self.M_1 = Machine(env, id="M_1", processing_delay=2)
        
        # 3 machines in parallel
        self.M_parallel = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(3)]
        
        # M_2 is the merge node with specific parameters
        self.M_2 = Machine(env, id="M_2", processing_delay=2, work_capacity=4, in_edge_selection="ROUND_ROBIN")
        
        self.add_child_node([self.M_1, self.M_2])
        self.add_child_node(self.M_parallel)
        
        # Buffers from M_1 to parallel machines
        self.split_buffers = []
        for i in range(3):
            buf = Buffer(env, id=f"B_M1_{i+1}", capacity=2)
            self.split_buffers.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.M_1, self.M_parallel[i])
            
        # Buffers from parallel machines to M_2
        self.merge_buffers = []
        for i in range(3):
            buf = Buffer(env, id=f"B_{i+1}_M2", capacity=2)
            self.merge_buffers.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.M_parallel[i], self.M_2)
            
        self.entry = self.M_1
        self.exit = self.M_2

class SubsystemB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        self.B1.connect(self.M[0], self.M[1])
        
        self.entry = self.M[0]
        self.exit = self.M[1]

class ABABlock(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.A1 = SubsystemA(env, id="A_1")
        self.B = SubsystemB(env, id="B")
        self.A2 = SubsystemA(env, id="A_2")
        
        self.add_child_node([self.A1, self.B, self.A2])
        
        self.Binter1 = Buffer(env, id="Binter1", capacity=2)
        self.Binter2 = Buffer(env, id="Binter2", capacity=2)
        
        self.add_child_edge([self.Binter1, self.Binter2])
        
        self.Binter1.connect(self.A1.exit, self.B.entry)
        self.Binter2.connect(self.B.exit, self.A2.entry)
        
        self.entry = self.A1.entry
        self.exit = self.A2.exit

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.source = Source(env, id="SRC", inter_arrival_time=1.0)
        self.sink = Sink(env, id="SINK")
        self.add_child_node([self.source, self.sink])
        
        self.blocks = [ABABlock(env, id=f"Block_{i+1}") for i in range(3)]
        self.add_child_node(self.blocks)
        
        # Source to Block 1
        self.src_edge = Buffer(env, id="src_edge", capacity=2)
        self.add_child_edge(self.src_edge)
        self.src_edge.connect(self.source, self.blocks[0].entry)
        
        # Between blocks
        self.inter_block_edges = []
        for i in range(2):
            buf = Buffer(env, id=f"B{i+1}", capacity=2)
            self.inter_block_edges.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.blocks[i].exit, self.blocks[i+1].entry)
            
        # Block 3 to Sink
        self.sink_edge = Buffer(env, id="sink_edge", capacity=2)
        self.add_child_edge(self.sink_edge)
        self.sink_edge.connect(self.blocks[-1].exit, self.sink)

env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)