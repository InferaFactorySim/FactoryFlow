"""
ModelDescription:
A production line begins with a Source named Src generating items every 5 seconds. Src connects to first Machine via B_src_1 The line consists of 3 sequential stages. Each stage Stage_1 through Stage_3 is modeled as a subsystem containing a Machine with a processing delay of 4.0 seconds, followed by a Buffer with capacity 2. The output of Stage_3 is connected to a Sink named Sink. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. In every row and the 2nd and 3rd machines have 3 buffers in between them.Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1. And extra buffers in multiedge as B_2_3_1, B_2_3_2

 MODEL ASSUMPTIONS:
1.  Node names and Types are chosen according to the user's description.
2.  A `Stage` class is assumed to be created to model the repeated subsystem pattern of one Machine followed by one Buffer.
3.  The global statement "All machines have a processing_Delay of 2" is assumed to override the specific processing delay of 4.0 seconds mentioned for the machines inside the stages.
4.  Separate Sources `SRC` is assumed to connect to the first machine (`Stage_1_M1`) in the linear sequence. The buffer connecting `SRC` to Row 1 is named `B_src_1`, and  buffers for the subsequent rows are assumed to exist with inferred names (e.g., `B_src_1`, etc.).
5.  The connection between "M1 in r1 and M1 in row2" is assumed to be a Buffer named `Cross_Buffer_1`, with flow direction assumed from Row 1 to Row 2.
6.  The connection between "M3 in row2 and M3 in row4" is assumed to be a Buffer named `Cross_Buffer_2`, with flow direction assumed from Row 2 to Row 4.
7.  The "3 buffers in between" the 2nd machine (`Stage_2_M1`) and 3rd machine (`Stage_3_M1`) in every row are assumed to be connected in parallel.
8.  These 3 parallel buffers are assumed to consist of the standard buffer from Stage 2 (`Stage_2_B1`) and the two extra buffers explicitly named `B_2_3_1` and `B_2_3_2` (with row-specific hierarchical naming).
9.  The output of `Stage_3` from all 4 rows is assumed to connect to separate sinks with ID `SINK` using separate buffers with inferred names.
10. All buffers, including cross-connecting buffers and extra parallel buffers, are assumed to have a capacity of 2 based on the global description.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Stage(Node):
    def __init__(self, env, id, stage_num):
        super().__init__(env, id)
        # Machine with processing delay 2 (overridden by global assumption)
        self.M = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=2.0)
        self.add_child_node(self.M)
        # Buffer with capacity 2
        self.B = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B)

class Row(Node):
    def __init__(self, env, id, row_num):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="Src", inter_arrival_time=5.0)
        self.add_child_node(self.src)
        
        # Stages 1 to 3
        self.stages = [Stage(env, id=f"Stage_{i}", stage_num=i) for i in range(1, 4)]
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Buffer from Source to Stage 1
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        self.b_src.connect(self.src, self.stages[0].M)
        
        # Connect Stage 1 to Stage 2
        # Stage 1 Buffer connects Stage 1 Machine to Stage 2 Machine
        self.stages[0].B.connect(self.stages[0].M, self.stages[1].M)
        
        # Connect Stage 2 to Stage 3 (3 parallel buffers)
        # 1. The buffer belonging to Stage 2
        self.stages[1].B.connect(self.stages[1].M, self.stages[2].M)
        
        # 2. Extra buffers B_2_3_1 and B_2_3_2
        self.extra_buffers = []
        for k in range(1, 3):
            buf = Buffer(env, id=f"B_2_3_{k}", capacity=2)
            self.extra_buffers.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.stages[1].M, self.stages[2].M)
            
        # Connect Stage 3 to Sink
        # Stage 3 Buffer connects Stage 3 Machine to Sink
        self.stages[2].B.connect(self.stages[2].M, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # 4 Parallel Rows
        self.rows = [Row(env, id=f"Row_{i}", row_num=i) for i in range(1, 5)]
        self.add_child_node(self.rows)
        
        # Cross Connection 1: Row 1 M1 to Row 2 M1
        # Row 1 is index 0, Row 2 is index 1. M1 is stages[0].M
        self.cross_buffer_1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross_buffer_1)
        self.cross_buffer_1.connect(self.rows[0].stages[0].M, self.rows[1].stages[0].M)
        
        # Cross Connection 2: Row 2 M3 to Row 4 M3
        # Row 2 is index 1, Row 4 is index 3. M3 is stages[2].M
        self.cross_buffer_2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cross_buffer_2)
        self.cross_buffer_2.connect(self.rows[1].stages[2].M, self.rows[3].stages[2].M)

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