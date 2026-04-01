"""
ModelDescription:
A production line begins with a Source named SRC generating items every 2.5 seconds.  Every sequence of SRC is followed by a buffer ID=B_src_1.Then a line consists of 3 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem containing a Machine, followed by a Buffer. Machine in each stage has a processing delay of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is connected to a Sink named SINK. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1, and Buffers as Stage_i_B1,for i from 1 to 3. .. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. A repeated pattern class named `Stage` is inferred, consisting of one Machine (`Stage_i_M1`) followed by one Buffer (`Stage_i_B1`).
3. A repeated pattern class named `Sequence` (or `Row`) is inferred, consisting of 3 sequential `Stage` subsystems.
4. The specific processing delays (4.0, 3, 2) and capacities (2, 3, 4) specified for the three stages are used, overriding the later generic statement "All machines have a processing_Delay of 2 and buffers have a capacity of 2", which is assumed to apply only to components where specific values were not provided (like cross-buffers).
5. The single buffer `B_src_1` connects the Source `SRC` to the first machine (`Stage_1_M1`) . Every sequence has a separate SRC and a S_src_1
6. The output buffer of the last stage (`Stage_3_B1`) in all 4 parallel sequences connects to the separate Sinks `SINK`.
7. Cross-connections are assumed to flow from the lower row index to the higher row index (Row 1 to Row 2, and Row 2 to Row 4).
8. The reference to "M3" in the cross-connection description is assumed to refer to the Machine located in Stage 3 (`Stage_3_M1`).
9. `Cross_Buffer_1` connects Row 1's Stage 1 Machine to Row 2's Stage 1 Machine.
10. `Cross_Buffer_2` connects Row 2's Stage 3 Machine to Row 4's Stage 3 Machine.
11. Cross-connecting buffers are assumed to have a capacity of 2, based on the generic text provided.
12. Used a single buffer for any connection where the specific buffer was not named or the count was not specified.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Stage class representing a Machine followed by a Buffer
class Stage(Node):
    def __init__(self, env, id, stage_num, delay, capacity):
        super().__init__(env, id)
        # Machine with specific delay and capacity
        self.machine = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.machine)
        
        # Buffer with generic capacity of 2
        self.buffer = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.buffer)

# Sequence class representing a row with Source, 3 Stages, and Sink
class Sequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.source)
        
        # Source Buffer
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # 3 Sequential Stages
        self.stages = []
        # Parameters for each stage: (processing_delay, machine_capacity)
        params = [(4.0, 2), (3.0, 3), (2.0, 4)]
        for i in range(3):
            stage_num = i + 1
            delay, cap = params[i]
            stage = Stage(env, id=f"Stage_{stage_num}", stage_num=stage_num, delay=delay, capacity=cap)
            self.stages.append(stage)
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Connections
        # Connect Source to Stage 1 Machine via B_src_1
        self.b_src.connect(self.source, self.stages[0].machine)
        
        # Connect Stage 1 Buffer to Stage 2 Machine
        self.stages[0].buffer.connect(self.stages[0].machine, self.stages[1].machine)
        
        # Connect Stage 2 Buffer to Stage 3 Machine
        self.stages[1].buffer.connect(self.stages[1].machine, self.stages[2].machine)
        
        # Connect Stage 3 Buffer to Sink
        self.stages[2].buffer.connect(self.stages[2].machine, self.sink)

# SystemModel class representing 4 parallel sequences with cross-connections
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 parallel sequences (Rows)
        self.rows = [Sequence(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Cross Connections
        
        # Connection 1: Row 1 Stage 1 Machine -> Row 2 Stage 1 Machine
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        # Row 1 is index 0, Row 2 is index 1. Stage 1 is index 0.
        self.cb1.connect(self.rows[0].stages[0].machine, self.rows[1].stages[0].machine)
        
        # Connection 2: Row 2 Stage 3 Machine -> Row 4 Stage 3 Machine
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        # Row 2 is index 1, Row 4 is index 3. Stage 3 is index 2.
        self.cb2.connect(self.rows[1].stages[2].machine, self.rows[3].stages[2].machine)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)