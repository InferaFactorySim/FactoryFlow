"""
ModelDescription:
A production line begins with a Source named SRC generating items every 2.5 seconds.  Every sequence has a SRC followed by a buffer ID=B_src_1.Then a line consists of 3 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem containing a Machine, followed by a Buffer. Machine in each stage has a processing delay of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is connected to a Sink named SINK.  Every line or sequence is a class. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. .. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them.And extra buffers in multiedge as B_2_3_1, B_2_3_2

 MODEL ASSUMPTIONS:
1.  Node names and types are chosen strictly according to the user's description.
2.  A `Stage` class is created to represent the repeated subsystem pattern of a Machine followed by a Buffer.
3.  A `Line` class is created to represent the repeated sequence of a Source, a Source Buffer, and the three sequential Stages.
4.  The system consists of 4 parallel `Line` instances (Rows 1 through 4) and a single common Sink node named `SINK`.
5.  Each `Line` instance contains its own local Source node named `SRC` and a buffer named `B_src_1`.
6.  The specific processing delays (4.0, 3, 2) and machine capacities (2, 3, 4) provided for Stages 1, 2, and 3 respectively override the general statement "All machines have a processing_Delay of 2".
7.  All buffers (including Stage buffers, Source buffers, Cross buffers, and Extra buffers) have a capacity of 2.
8.  The connection between the Machine in Stage 2 and the Machine in Stage 3 within every row consists of 3 parallel buffers: the standard buffer of Stage 2 (`Stage_2_B1`) and two extra buffers named `B_2_3_1` and `B_2_3_2`.
9.  `Cross_Buffer_1` connects the Machine in Row 1, Stage 1 to the Machine in Row 2, Stage 1. The flow direction is assumed to be from Row 1 to Row 2.
10. `Cross_Buffer_2` connects the Machine in Row 2, Stage 3 to the Machine in Row 4, Stage 3. The flow direction is assumed to be from Row 2 to Row 4.
11. The common Sink node collects parts from the output buffer of Stage 3 from all 4 parallel lines.
12. Used default values for any parameters not explicitly specified or inferred above.
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
        # Machine
        self.M = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.M)
        # Buffer
        self.B = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B)

class Line(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.src)
        
        # Buffer after Source
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # Stages
        self.stages = []
        # Parameters: (Stage Index, Delay, Capacity)
        stage_params = [
            (1, 4.0, 2),
            (2, 3.0, 3),
            (3, 2.0, 4)
        ]
        
        for idx, delay, cap in stage_params:
            stage = Stage(env, id=f"Stage_{idx}", stage_num=idx, delay=delay, capacity=cap)
            self.stages.append(stage)
        self.add_child_node(self.stages)
        
        # Connect Source -> B_src -> Stage 1 Machine
        self.b_src.connect(self.src, self.stages[0].M)
        
        # Connect Stage 1 Buffer -> Stage 2 Machine
        self.stages[0].B.connect(self.stages[0].M, self.stages[1].M)
        
        # Connect Stage 2 to Stage 3
        # 1. Standard Stage 2 Buffer
        self.stages[1].B.connect(self.stages[1].M, self.stages[2].M)
        
        # 2. Extra Buffers
        self.extra_buffers = []
        for k in range(1, 3):
            buf = Buffer(env, id=f"B_2_3_{k}", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.stages[1].M, self.stages[2].M)
            self.extra_buffers.append(buf)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create 4 Parallel Lines (Rows)
        self.lines = [Line(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.lines)
        
        # Common Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Connect Lines to Sink
        # The output of Stage 3 (Stage_3_B1) connects to Sink
        for line in self.lines:
            line.stages[2].B.connect(line.stages[2].M, self.sink)
            
        # Cross Connections
        # Cross_Buffer_1: Row 1 (M1) -> Row 2 (M1)
        # M1 is in Stage 1
        self.cross_b1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross_b1)
        self.cross_b1.connect(self.lines[0].stages[0].M, self.lines[1].stages[0].M)
        
        # Cross_Buffer_2: Row 2 (M3) -> Row 4 (M3)
        # M3 is in Stage 3
        self.cross_b2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cross_b2)
        self.cross_b2.connect(self.lines[1].stages[2].M, self.lines[3].stages[2].M)

# Simulation Run
env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)