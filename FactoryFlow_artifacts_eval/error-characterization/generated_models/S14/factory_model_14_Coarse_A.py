"""
ModelDescription:
3 machines connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the Stage_1_M1 in r1 and Stage_1_M1 in row2 and a connection between Stage_3_M1 in row2 and Stage_3_M1 in row4. In every row and the 2nd and 3rd machines have 3 buffers in between them

 MODEL ASSUMPTIONS:
1.  Node names and Types are chosen according to the user's description.
  A repeated pattern class is created for the linear sequence containing a Source, 3 Machines, and a Sink. IDs of nodes and edges as mentioned in quotes ('')
  The system is assumed to consist of 4 instances of this sequence class instantiated in parallel.
2.  A `Stage` class is assumed to be created to model the repeated subsystem pattern of one Machine followed by one Buffer.
3.  All machines have a processing_Delay of 2.
4.  Separate Sources `SRC` is assumed to connect to the first machine (`Stage_1_M1`) in the linear sequence. The buffer connecting `SRC` to Row 1 is named `B_src_1`, and  buffers for the subsequent rows are assumed to exist with inferred names (e.g., `B_src_1`, etc.).
5.  The connection between "Stage_1_M1 in r1 and Stage_1_M1 in row2" is assumed to be a Buffer named `Cross_Buffer_1`, with flow direction assumed from Row 1 to Row 2.
6.  The connection between "Stage_3_M1 in row2 and Stage_3_M1 in row4" is assumed to be a Buffer named `Cross_Buffer_2`, with flow direction assumed from Row 2 to Row 4.
7.  The "3 buffers in between" the 2nd machine (`Stage_2_M1`) and 3rd machine (`Stage_3_M1`) in every row are assumed to be connected in parallel.
8.  These 3 parallel buffers are assumed to consist of the standard buffer from Stage 2 (`Stage_2_B1`) and the two extra buffers explicitly named `B_2_3_1` and `B_2_3_2` (with row-specific hierarchical naming).
9.  The output of `Stage_3` from all 4 rows is assumed to connect to separate sinks with ID `SINK` using separate buffers with inferred names.
10.All buffers, including cross-connecting buffers and extra parallel buffers, are assumed to have a capacity of 2 based on the global description.
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class RowSequence(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # Creating Source
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)
        
        # Creating Machines with processing delay of 2
        self.m1 = Machine(env, id="Stage_1_M1", processing_delay=2)
        self.m2 = Machine(env, id="Stage_2_M1", processing_delay=2)
        self.m3 = Machine(env, id="Stage_3_M1", processing_delay=2)
        self.add_child_node([self.m1, self.m2, self.m3])
        
        # Creating Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Creating Buffers with capacity 2
        # Buffer from Source to first machine (Stage_1_M1)
        self.b_src = Buffer(env, id=f"B_src_{row_idx}", capacity=2)
        
        # Buffer between Stage_1_M1 and Stage_2_M1
        self.b1 = Buffer(env, id="Stage_1_B1", capacity=2)
        
        # 3 Parallel Buffers between Stage_2_M1 and Stage_3_M1
        self.b2_main = Buffer(env, id="Stage_2_B1", capacity=2)
        self.b2_p1 = Buffer(env, id="B_2_3_1", capacity=2)
        self.b2_p2 = Buffer(env, id="B_2_3_2", capacity=2)
        
        # Buffer from Stage_3_M1 to Sink
        self.b_sink = Buffer(env, id="B_sink", capacity=2)
        
        self.add_child_edge([self.b_src, self.b1, self.b2_main, self.b2_p1, self.b2_p2, self.b_sink])
        
        # Connecting nodes
        self.b_src.connect(self.src, self.m1)
        self.b1.connect(self.m1, self.m2)
        
        # Connecting parallel buffers
        self.b2_main.connect(self.m2, self.m3)
        self.b2_p1.connect(self.m2, self.m3)
        self.b2_p2.connect(self.m2, self.m3)
        
        self.b_sink.connect(self.m3, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 parallel row sequences
        self.rows = [RowSequence(env, id=f"row{i+1}", row_idx=i+1) for i in range(4)]
        self.add_child_node(self.rows)
        
        # Creating Cross Buffers with capacity 2
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge([self.cb1, self.cb2])
        
        # Connecting Cross Buffers
        # Connection between Stage_1_M1 in r1 (row 1) and Stage_1_M1 in row2
        self.cb1.connect(self.rows[0].m1, self.rows[1].m1)
        
        # Connection between Stage_3_M1 in row2 and Stage_3_M1 in row4
        self.cb2.connect(self.rows[1].m3, self.rows[3].m3)

# Initializing simpy environment
env = simpy.Environment()

# Defining the top level system
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)