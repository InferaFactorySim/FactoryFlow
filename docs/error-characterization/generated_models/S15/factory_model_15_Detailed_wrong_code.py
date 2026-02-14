"""
ModelDescription:
A production line begins with a Source named SRC generating items every 2.5 seconds.  Every sequence of SRC is followed by a buffer ID=B_src_1.Then a line consists of 3 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem containing a Machine, followed by a Buffer. Machine in each stage has a processing delay of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is connected to a Sink named SINK. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. .. All buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them.And extra buffers in multiedge as B_2_3_1, B_2_3_2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. A `Stage` class is inferred to model the repeated subsystem containing a Machine followed by a Buffer, and a `Row` class is inferred to model the sequence of 3 Stages.
3. The single buffer `B_src_1` is assumed to connect the Source `SRC` to the input of the first machine (`Stage_1_M1`) in all 4 parallel rows.
4. The output of the last stage (`Stage_3`) in all 4 rows is assumed to connect to the common Sink `SINK`.
5. The 3 buffers between the 2nd and 3rd machines in every row are assumed to be connected in series in the order: `Stage_2_B1` (the standard buffer of Stage 2), followed by `B_2_3_1`, followed by `B_2_3_2`.
6. Cross connections are assumed to be unidirectional, flowing from the row with the lower index to the row with the higher index.
7. `Cross_Buffer_1` is assumed to connect the output of Row 1's Stage 1 Machine to the input of Row 2's Stage 1 Machine.
8. `Cross_Buffer_2` is assumed to connect the output of Row 2's Stage 3 Machine to the input of Row 4's Stage 3 Machine.
9. Used default values for all missing parameters for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Stage(Node):
    def __init__(self, env, id, stage_num, delay, capacity):
        super().__init__(env, id)
        # Machine in each stage
        self.M = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.M)
        # Buffer in each stage
        self.B = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B)

class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 3 sequential stages
        # Stage 1: Delay 4.0, Capacity 2
        self.stage_1 = Stage(env, id="Stage_1", stage_num=1, delay=4.0, capacity=2)
        self.add_child_node(self.stage_1)
        
        # Stage 2: Delay 3.0, Capacity 3
        self.stage_2 = Stage(env, id="Stage_2", stage_num=2, delay=3.0, capacity=3)
        self.add_child_node(self.stage_2)
        
        # Stage 3: Delay 2.0, Capacity 4
        self.stage_3 = Stage(env, id="Stage_3", stage_num=3, delay=2.0, capacity=4)
        self.add_child_node(self.stage_3)
        
        # Extra buffers between Stage 2 and Stage 3
        self.b_2_3_1 = Buffer(env, id="B_2_3_1", capacity=2)
        self.b_2_3_2 = Buffer(env, id="B_2_3_2", capacity=2)
        self.add_child_edge([self.b_2_3_1, self.b_2_3_2])
        
        # Connecting Stage 1 to Stage 2
        # Stage 1 Buffer connects Stage 1 Machine to Stage 2 Machine
        self.stage_1.B.connect(self.stage_1.M, self.stage_2.M)
        
        # Connecting Stage 2 to Stage 3 with 3 buffers in series
        # Path: Stage 2 Machine -> Stage 2 Buffer -> B_2_3_1 -> B_2_3_2 -> Stage 3 Machine
        self.stage_2.B.connect(self.stage_2.M, self.b_2_3_1)
        self.b_2_3_1.connect(self.stage_2.B, self.b_2_3_2)
        self.b_2_3_2.connect(self.b_2_3_1, self.stage_3.M)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.src)
        
        # Buffer connecting Source to Rows
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # 4 Parallel Rows
        self.rows = [Row(env, id=f"Row[{i}]") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Connect Source to the first machine of all rows
        for r in self.rows:
            self.b_src.connect(self.src, r.stage_1.M)
            
        # Connect the last machine of all rows to Sink
        # Stage 3 Buffer connects Stage 3 Machine to Sink
        for r in self.rows:
            r.stage_3.B.connect(r.stage_3.M, self.sink)
            
        # Cross Connections
        # Connection between M1 in Row 1 and M1 in Row 2
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        self.cb1.connect(self.rows[0].stage_1.M, self.rows[1].stage_1.M)
        
        # Connection between M3 in Row 2 and M3 in Row 4
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        self.cb2.connect(self.rows[1].stage_3.M, self.rows[3].stage_3.M)

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