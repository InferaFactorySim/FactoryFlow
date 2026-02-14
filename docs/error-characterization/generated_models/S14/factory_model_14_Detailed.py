"""
ModelDescription:
A production line begins with a Source named Src generating items every 5 seconds. Src connects to first Machine via B_src_1 The line consists of 3 sequential stages. Each stage Stage_1 through Stage_3 is modeled as a subsystem containing a Machine with a processing delay of 4.0 seconds, followed by a Buffer with capacity 2. The output of Stage_3 is connected to a Sink named Sink. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. In every row and the 2nd and 3rd machines have 3 buffers in between them.Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1. And extra buffers in multiedge as B_2_3_1, B_2_3_2

 MODEL ASSUMPTIONS:
1.  Node names and Types are chosen according to the user's description.
2.  A `Stage` class is assumed to be created to model the repeated subsystem pattern of one Machine followed by one Buffer.
3.  The global statement "All machines have a processing_Delay of 2" is assumed to override the specific processing delay of 4.0 seconds mentioned for the machines inside the stages.
4.  The Source `Src` is assumed to connect to the first machine (`Stage_1_M1`) of *each* of the 4 parallel rows. The buffer connecting `Src` to Row 1 is named `B_src_1`, and buffers for the subsequent rows are assumed to exist with inferred names (e.g., `B_src_2`, etc.).
5.  The connection between "M1 in r1 and M1 in row2" is assumed to be a Buffer named `Cross_Buffer_1`, with flow direction assumed from Row 1 to Row 2.
6.  The connection between "M3 in row2 and M3 in row4" is assumed to be a Buffer named `Cross_Buffer_2`, with flow direction assumed from Row 2 to Row 4.
7.  The "3 buffers in between" the 2nd machine (`Stage_2_M1`) and 3rd machine (`Stage_3_M1`) in every row are assumed to be connected in parallel.
8.  These 3 parallel buffers are assumed to consist of the standard buffer from Stage 2 (`Stage_2_B1`) and the two extra buffers explicitly named `B_2_3_1` and `B_2_3_2` (with row-specific hierarchical naming).
9.  The output of `Stage_3` from all 4 rows is assumed to connect to the common `Sink` using separate buffers with inferred names.
10. All buffers, including cross-connecting buffers and extra parallel buffers, are assumed to have a capacity of 2 based on the global description.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Stage class modeling the subsystem of Machine -> Buffer
class Stage(Node):
    def __init__(self, env, id, stage_num):
        super().__init__(env, id)
        # Machine with processing delay 2.0 (overrides 4.0 from description based on global assumption)
        self.M1 = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=2.0)
        self.add_child_node(self.M1)
        
        # Buffer with capacity 2
        self.B1 = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B1)

# Row class modeling the sequence of 3 stages
class Row(Node):
    def __init__(self, env, id, row_num):
        super().__init__(env, id)
        
        # Creating 3 sequential stages
        self.stages = []
        for i in range(1, 4):
            self.stages.append(Stage(env, id=f"Stage_{i}", stage_num=i))
        self.add_child_node(self.stages)
        
        # Creating extra buffers between Stage 2 and Stage 3
        self.extra_buffers = []
        for k in range(1, 3):
            self.extra_buffers.append(Buffer(env, id=f"B_2_3_{k}", capacity=2))
        self.add_child_edge(self.extra_buffers)
        
        # Connecting Stage 1 to Stage 2
        # Stage_1.B1 connects Stage_1.M1 -> Stage_2.M1
        self.stages[0].B1.connect(self.stages[0].M1, self.stages[1].M1)
        
        # Connecting Stage 2 to Stage 3 with 3 parallel buffers
        # 1. The standard buffer in Stage 2
        self.stages[1].B1.connect(self.stages[1].M1, self.stages[2].M1)
        # 2. The extra buffers
        for b in self.extra_buffers:
            b.connect(self.stages[1].M1, self.stages[2].M1)

# SystemModel class containing 4 parallel rows, source, sink, and cross connections
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing Source
        self.src = Source(env, id="Src", inter_arrival_time=5.0)
        self.add_child_node(self.src)
        
        # Initializing Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Creating 4 parallel rows
        self.rows = []
        for i in range(1, 5):
            self.rows.append(Row(env, id=f"Row_{i}", row_num=i))
        self.add_child_node(self.rows)
        
        # Connecting Source to the first machine of each row
        self.src_buffers = []
        for i in range(4):
            # Buffer naming: B_src_1, B_src_2, etc.
            self.src_buffers.append(Buffer(env, id=f"B_src_{i+1}", capacity=2))
        self.add_child_edge(self.src_buffers)
        
        for i in range(4):
            self.src_buffers[i].connect(self.src, self.rows[i].stages[0].M1)
            
        # Connecting the last machine of each row to Sink
        # Using the buffer from Stage 3 (Stage_3_B1)
        for i in range(4):
            self.rows[i].stages[2].B1.connect(self.rows[i].stages[2].M1, self.sink)
            
        # Cross Connections
        # Connection between M1 in Row 1 and M1 in Row 2
        self.cross1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross1)
        self.cross1.connect(self.rows[0].stages[0].M1, self.rows[1].stages[0].M1)
        
        # Connection between M3 in Row 2 and M3 in Row 4
        self.cross2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cross2)
        self.cross2.connect(self.rows[1].stages[2].M1, self.rows[3].stages[2].M1)

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