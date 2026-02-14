"""
ModelDescription:
A production line begins with a Source named SRC generating items every 2.5 seconds.  Every sequence has a SRC followed by a buffer ID=B_src_1.Then a line consists of 3 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem containing a Machine, followed by a Buffer .Machine in each stage has a processing delay of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is connected to a Sink named SINK.  Every line has a source and a sink.  Every line or sequence is a class. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. .. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them.And extra buffers in multiedge as B_2_3_1, B_2_3_2

 MODEL ASSUMPTIONS:
1.  Node names and types are chosen strictly according to the user's description.
2.  A `Stage` class is created to represent the repeated subsystem pattern of a Machine followed by a Buffer.
3.  A `Line` class is created to represent the repeated sequence of a Source, a Source Buffer, and the three sequential Stages and a sink
4.  The system consists of 4 parallel `Line` instances (Rows 1 through 4) and a separate Sinks node named `SINK`for every row
5.  Each `Line` instance contains its own local Source node named `SRC` and a buffer named `B_src_1`.
6.  The specific processing delays (4.0, 3, 2) and machine capacities (2, 3, 4) provided for Stages 1, 2, and 3 respectively override the general statement "All machines have a processing_Delay of 2".
7.  All buffers (including Stage buffers, Source buffers, Cross buffers, and Extra buffers) have a capacity of 2.
8.  The connection between the Machine in Stage 2 and the Machine in Stage 3 within every row consists of 3 parallel buffers: the standard buffer of Stage 2 (`Stage_2_B1`) and two extra buffers named `B_2_3_1` and `B_2_3_2`.
9.  `Cross_Buffer_1` connects the Machine in Row 1, Stage 1 to the Machine in Row 2, Stage 1. The flow direction is assumed to be from Row 1 to Row 2.
10. `Cross_Buffer_2` connects the Machine in Row 2, Stage 3 to the Machine in Row 4, Stage 3. The flow direction is assumed to be from Row 2 to Row 4.
11. It has separate Sink nodes collects parts from the output buffer of Stage 3 from all 4 parallel lines.
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
    def __init__(self, env, id, stage_num):
        super().__init__(env, id)
        
        # Determine parameters based on stage number
        if stage_num == 1:
            proc_delay = 4.0
            mach_cap = 2
        elif stage_num == 2:
            proc_delay = 3.0
            mach_cap = 3
        elif stage_num == 3:
            proc_delay = 2.0
            mach_cap = 4
        else:
            proc_delay = 2.0
            mach_cap = 2
            
        # Create Machine
        self.machine = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=proc_delay, work_capacity=mach_cap)
        self.add_child_node(self.machine)
        
        # Create Buffer
        self.buffer = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.buffer)

class Line(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.source)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Source Buffer
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # Stages
        self.stages = []
        for i in range(1, 4):
            stage = Stage(env, id=f"Stage_{i}", stage_num=i)
            self.stages.append(stage)
        self.add_child_node(self.stages)
        
        # Extra Buffers between Stage 2 and 3
        self.b_2_3_1 = Buffer(env, id="B_2_3_1", capacity=2)
        self.add_child_edge(self.b_2_3_1)
        
        self.b_2_3_2 = Buffer(env, id="B_2_3_2", capacity=2)
        self.add_child_edge(self.b_2_3_2)
        
        # Connections
        # SRC -> B_src -> Stage 1 Machine
        self.b_src.connect(self.source, self.stages[0].machine)
        
        # Stage 1 Machine -> Stage 1 Buffer -> Stage 2 Machine
        self.stages[0].buffer.connect(self.stages[0].machine, self.stages[1].machine)
        
        # Stage 2 Machine -> Stage 2 Buffer -> Stage 3 Machine
        self.stages[1].buffer.connect(self.stages[1].machine, self.stages[2].machine)
        
        # Stage 2 Machine -> Extra Buffers -> Stage 3 Machine
        self.b_2_3_1.connect(self.stages[1].machine, self.stages[2].machine)
        self.b_2_3_2.connect(self.stages[1].machine, self.stages[2].machine)
        
        # Stage 3 Machine -> Stage 3 Buffer -> Sink
        self.stages[2].buffer.connect(self.stages[2].machine, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create 4 Rows
        self.rows = [Line(env, id=f"Row_{i}") for i in range(1, 5)]
        self.add_child_node(self.rows)
        
        # Cross Buffers
        self.cross_buffer_1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross_buffer_1)
        
        self.cross_buffer_2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cross_buffer_2)
        
        # Connection: Row 1 M1 -> Row 2 M1
        # M1 is in Stage 1 (index 0)
        self.cross_buffer_1.connect(self.rows[0].stages[0].machine, self.rows[1].stages[0].machine)
        
        # Connection: Row 2 M3 -> Row 4 M3
        # M3 is in Stage 3 (index 2)
        # Row 2 is index 1, Row 4 is index 3
        self.cross_buffer_2.connect(self.rows[1].stages[2].machine, self.rows[3].stages[2].machine)

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