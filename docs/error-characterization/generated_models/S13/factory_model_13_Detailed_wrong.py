"""
ModelDescription:
A production line begins with a Source named SRC generating items every 2.5 seconds.  Every sequence of SRC is followed by a buffer ID=B_src_1.Then a line consists of 3 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem containing a Machine, followed by a Buffer. Machine in each stage has a processing delay of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is connected to a Sink named SINK. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. .. All machines have a processing_Delay of 2 and buffers have a capacity of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.Row index starts from 1

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. A repeated pattern class named `Stage` is inferred, consisting of one Machine (`Stage_i_M1`) followed by one Buffer (`Stage_i_B1`).
3. A repeated pattern class named `Sequence` (or `Row`) is inferred, consisting of 3 sequential `Stage` subsystems.
4. The specific processing delays (4.0, 3, 2) and capacities (2, 3, 4) specified for the three stages are used, overriding the later generic statement "All machines have a processing_Delay of 2 and buffers have a capacity of 2", which is assumed to apply only to components where specific values were not provided (like cross-buffers).
5. The single buffer `B_src_1` connects the Source `SRC` to the first machine (`Stage_1_M1`) of all 4 parallel sequences (one-to-many connection).
6. The output buffer of the last stage (`Stage_3_B1`) in all 4 parallel sequences connects to the common Sink `SINK`.
7. Cross-connections are assumed to flow from the lower row index to the higher row index (Row 1 to Row 2, and Row 2 to Row 4).
8. The reference to "M3" in the cross-connection description is assumed to refer to the Machine located in Stage 3 (`Stage_3_M1`).
9. `Cross_Buffer_1` connects Row 1's Stage 1 Machine to Row 2's Stage 1 Machine.
10. `Cross_Buffer_2` connects Row 2's Stage 3 Machine to Row 4's Stage 3 Machine.
11. Cross-connecting buffers are assumed to have a capacity of 2, based on the generic text provided.
12. Used a single buffer for any connection where the specific buffer was not named or the count was not specified.
"""

# importing required libraries
import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Stage class representing a subsystem with one Machine and one Buffer
class Stage(Node):
    def __init__(self, env, id, stage_num, delay, capacity):
        super().__init__(env, id)
        # Machine
        self.m1 = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.m1)
        # Buffer
        self.b1 = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.b1)

# Sequence class representing 3 sequential stages
class Sequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Stage 1: Delay 4.0, Capacity 2
        self.s1 = Stage(env, id="Stage_1", stage_num=1, delay=4.0, capacity=2)
        # Stage 2: Delay 3.0, Capacity 3
        self.s2 = Stage(env, id="Stage_2", stage_num=2, delay=3.0, capacity=3)
        # Stage 3: Delay 2.0, Capacity 4
        self.s3 = Stage(env, id="Stage_3", stage_num=3, delay=2.0, capacity=4)
        
        self.stages = [self.s1, self.s2, self.s3]
        self.add_child_node(self.stages)
        
        # Connect Stage 1 Buffer to Stage 2 Machine
        self.s1.b1.connect(self.s1.m1, self.s2.m1)
        
        # Connect Stage 2 Buffer to Stage 3 Machine
        self.s2.b1.connect(self.s2.m1, self.s3.m1)

# SystemModel class representing the full production line
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.src)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # 4 Parallel Sequences (Rows)
        self.rows = [Sequence(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Buffer B_src_1 connecting Source to the first machine of all 4 parallel sequences
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        self.b_src.connect(self.src, [row.s1.m1 for row in self.rows])
        
        # Connect output of each row (Stage 3 Buffer) to Sink
        for row in self.rows:
            row.s3.b1.connect(row.s3.m1, self.sink)
            
        # Cross Connections
        # Cross_Buffer_1: Row 1 (Stage 1 M1) -> Row 2 (Stage 1 M1)
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        self.cb1.connect(self.rows[0].s1.m1, self.rows[1].s1.m1)
        
        # Cross_Buffer_2: Row 2 (Stage 3 M1) -> Row 4 (Stage 3 M1)
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        self.cb2.connect(self.rows[1].s3.m1, self.rows[3].s3.m1)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()

from factorysimpy.utils.utils import draw_blockdiagram
fig = draw_blockdiagram(TOP)
# displaying the block diagram
path =fig.render(filename="factory_model_13_Detailed_wrong", format="png")
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)