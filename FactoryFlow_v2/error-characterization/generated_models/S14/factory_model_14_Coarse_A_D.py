"""
ModelDescription:
3 machines connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the Stage_1_M1 in r1 and Stage_1_M1 in row2 and a connection between Stage_3_M1 in row2 and Stage_3_M1 in row4. In every row and the 2nd and 3rd machines have 3 buffers in between them.  Stage is a subsystem with a Machine ID stage_i_M1 and a buffer Stage_1_B1 where i=1,2,3. It is repeated thrice in every row.

 MODEL ASSUMPTIONS:
1.  Node names and Types are chosen according to the user's description.
  A repeated pattern class is created for the linear sequence containing a Source, 3 Machines, and a Sink. IDs of nodes and edges as mentioned in quotes ('')
  The system is assumed to consist of 4 instances of this sequence class instantiated in parallel.
2.  Every `Stage` class is a subsystem pattern of one Machine followed by one Buffer.
3.  All machines have a processing_Delay of 2.
4.  Separate Sources `SRC` is assumed to connect to the first machine (`Stage_1_M1`) in the linear sequence. The buffer connecting `SRC` to Row 1 is named `B_src_1`, and  buffers for the subsequent rows are assumed to exist with inferred names (e.g., `B_src_1`, etc.).
5.  The connection between "Stage_1_M1 in r1 and Stage_1_M1 in row2" is assumed to be a Buffer named `Cross_Buffer_1`, with flow direction assumed from Row 1 to Row 2.
6.  The connection between "Stage_3_M1 in row2 and Stage_3_M1 in row4" is assumed to be a Buffer named `Cross_Buffer_2`, with flow direction assumed from Row 2 to Row 4.
7.  The "3 buffers in between" the 2nd machine (`Stage_2_M1`) and 3rd machine (`Stage_3_M1`) in every row are assumed to be connected in parallel.
8.  These 3 parallel buffers are assumed to consist of the standard buffer from Stage 2 (`Stage_2_B1`) and the three extra buffers explicitly named `B_2_3_1` and `B_2_3_2`, (with row-specific hierarchical naming).
9.  The output of `Stage_3` from all 4 rows is assumed to connect to separate sinks with ID `SINK` using separate buffers with inferred names.
10.All buffers, including cross-connecting buffers and extra parallel buffers, are assumed to have a capacity of 2 based on the global description.
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
        # Machine ID stage_i_M1
        self.M = Machine(env, id=f"stage_{stage_num}_M1", processing_delay=2)
        self.add_child_node(self.M)
        # Buffer ID Stage_i_B1
        self.B = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B)

class Row(Node):
    def __init__(self, env, id, row_num):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)
        
        # Stages
        self.stages = [Stage(env, id=f"Stage_{i}", stage_num=i) for i in range(1, 4)]
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Buffer from Source to Stage 1
        self.b_src = Buffer(env, id=f"B_src_{row_num}", capacity=2)
        self.add_child_edge(self.b_src)
        self.b_src.connect(self.src, self.stages[0].M)
        
        # Connect Stage 1 to Stage 2 (1 buffer)
        self.stages[0].B.connect(self.stages[0].M, self.stages[1].M)
        
        # Connect Stage 2 to Stage 3 (3 buffers: 1 standard + 2 extra)
        # Standard
        self.stages[1].B.connect(self.stages[1].M, self.stages[2].M)
        # Extra
        self.extra_buffers = [Buffer(env, id=f"B_2_3_{k}", capacity=2) for k in range(1, 3)]
        self.add_child_edge(self.extra_buffers)
        for b in self.extra_buffers:
            b.connect(self.stages[1].M, self.stages[2].M)
            
        # Connect Stage 3 to Sink
        self.stages[2].B.connect(self.stages[2].M, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # 4 Rows in parallel
        self.rows = [Row(env, id=f"Row[{i}]", row_num=i+1) for i in range(4)]
        self.add_child_node(self.rows)
        
        # Cross connections
        # Stage_1_M1 in r1 (row 0) -> Stage_1_M1 in row2 (row 1)
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        self.cb1.connect(self.rows[0].stages[0].M, self.rows[1].stages[0].M)
        
        # Stage_3_M1 in row2 (row 1) -> Stage_3_M1 in row4 (row 3)
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        self.cb2.connect(self.rows[1].stages[2].M, self.rows[3].stages[2].M)

# initializing simpy environment
env = simpy.Environment()

# defining the top level system
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)