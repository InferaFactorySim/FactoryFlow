"""
ModelDescription:
3 machines each with a delay of 4,3,2 connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them. Stage is a subsystem with a Machine ID stage_i_M1 and a buffer Stage_1_B1 where i=1,2,3. It is repeated thrice in every row.


 MODEL ASSUMPTIONS:
1.  Node names and types are chosen strictly according to the user's description.
2.  A `Stage` class is created to represent the repeated subsystem pattern of a Machine followed by a Buffer.
3.  A `Line` class is created to represent the repeated sequence of a Source, a Source Buffer, and the three sequential Stages and a sink
4.  The system consists of 4 parallel `Line` instances (Rows 1 through 4) and a separate Sinks node named `SINK`for every row
5.  Each `Line` instance contains its own local Source node named `SRC` and a buffer named `B_src_1`.
6.  The specific processing delays (4.0, 3, 2) and machine capacities (2, 3, 4) provided for Stages 1, 2, and 3 respectively 
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

# Defining the Stage subsystem
class Stage(Node):
    def __init__(self, env, id, i, delay, capacity):
        super().__init__(env, id)
        # Machine with ID stage_i_M1
        self.machine = Machine(env, id=f"stage_{i}_M1", processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.machine)
        
        # Buffer with ID Stage_i_B1
        self.buffer = Buffer(env, id=f"Stage_{i}_B1", capacity=2)
        self.add_child_edge(self.buffer)

# Defining the Line class representing a row
class Line(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)
        
        # Source Buffer
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # Stages
        # Stage 1: delay 4, capacity 2
        # Stage 2: delay 3, capacity 3
        # Stage 3: delay 2, capacity 4
        stage_configs = [(1, 4.0, 2), (2, 3.0, 3), (3, 2.0, 4)]
        self.stages = []
        for i, delay, cap in stage_configs:
            stage = Stage(env, id=f"Stage_{i}", i=i, delay=delay, capacity=cap)
            self.stages.append(stage)
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Extra Buffers between Stage 2 and Stage 3
        self.extra_buffers = []
        for k in range(1, 3):
            buf = Buffer(env, id=f"B_2_3_{k}", capacity=2)
            self.extra_buffers.append(buf)
        self.add_child_edge(self.extra_buffers)
        
        # Connections
        
        # Connect Source to Stage 1 Machine via Source Buffer
        self.b_src.connect(self.source, self.stages[0].machine)
        
        # Connect Stage 1 Machine to Stage 2 Machine via Stage 1 Buffer
        self.stages[0].buffer.connect(self.stages[0].machine, self.stages[1].machine)
        
        # Connect Stage 2 Machine to Stage 3 Machine via Stage 2 Buffer
        self.stages[1].buffer.connect(self.stages[1].machine, self.stages[2].machine)
        
        # Connect Stage 2 Machine to Stage 3 Machine via Extra Buffers
        for buf in self.extra_buffers:
            buf.connect(self.stages[1].machine, self.stages[2].machine)
            
        # Connect Stage 3 Machine to Sink via Stage 3 Buffer
        self.stages[2].buffer.connect(self.stages[2].machine, self.sink)

# Defining the overall System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 parallel Lines (Rows)
        self.rows = [Line(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Cross Buffer 1: Connects Row 1 Stage 1 Machine to Row 2 Stage 1 Machine
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        self.cb1.connect(self.rows[0].stages[0].machine, self.rows[1].stages[0].machine)
        
        # Cross Buffer 2: Connects Row 2 Stage 3 Machine to Row 4 Stage 3 Machine
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        self.cb2.connect(self.rows[1].stages[2].machine, self.rows[3].stages[2].machine)

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