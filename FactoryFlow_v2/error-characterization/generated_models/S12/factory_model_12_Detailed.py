"""
ModelDescription:
A production line begins with a Source named SRC generating items every 5 seconds. The line consists of 3 sequential stages. Each stage Stage_1 through Stage_3 is modeled as a subsystem containing a Machine with a processing delay of 2.0 seconds, followed by a Buffer with capacity 2. The output of Stage_3 is connected to a Sink named SINK. There are 4 such sequences in parallel. Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i from 1 to 3. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, Cross_Buffer_2, etc.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source: SRC, Sink: SINK, Machines: Stage_i_M1, Buffers: Stage_i_B1, Cross Buffers: Cross_Buffer_x).
2. All machines have a processing_Delay of 2.
3. Assumed the system consists of 4 parallel rows, where each row contains 3 sequential "Stage" subsystems.
4. Assumed the naming convention `Stage_i_M1` and `Stage_i_B1` applies within the context of each stage subsystem, and unique hierarchical IDs are generated for the 4 parallel rows (e.g., Row_x_Stage_y_M1).
5. Assumed the Source connects to the input (Machine) of Stage 1 in all 4 parallel rows via separate buffers.
6. Assumed the output (Buffer) of Stage 3 in all 4 parallel rows connects to the common Sink via separate buffers.
7. Assumed the reference to "M1" in the cross-connection instruction refers to the machine inside Stage 1, and "M3" refers to the machine inside Stage 3.
8. Assumed the direction of flow for cross-connections is from the lower row index to the higher row index (Row 1 Stage 1 Machine -> Row 2 Stage 1 Machine, and Row 2 Stage 3 Machine -> Row 4 Stage 3 Machine).
9. Used default Buffer type with capacity 2 for all connections not explicitly defined (including Source-to-Row, Row-to-Sink, and Cross-Buffers), based on the general instruction "buffers have a capacity of 2".
10. Used a single buffer for all connections where the number of buffers was not specified.
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=5.0)
        self.add_child_node(self.src)
        
        # initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # initializing 4 parallel rows
        self.rows = [Row(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # initializing buffers from source to rows
        self.source_edges = [Buffer(env, id=f"edge[{i}]", capacity=2) for i in range(4)]
        self.add_child_edge(self.source_edges)
        
        # connecting source to rows and rows to sink
        for i in range(4):
            # connect source to first machine of each row
            self.source_edges[i].connect(self.src, self.rows[i].stages[0].m)
            # connect last buffer of each row to sink
            self.rows[i].stages[-1].b.connect(self.rows[i].stages[-1].m, self.sink)
            
        # initializing cross connections
        # (source_row_idx, source_stage_idx, dest_row_idx, dest_stage_idx)
        # M1 is in Stage 1 (index 0), M3 is in Stage 3 (index 2)
        cross_configs = [
            (0, 0, 1, 0), # Row 1 M1 -> Row 2 M1
            (1, 2, 3, 2)  # Row 2 M3 -> Row 4 M3
        ]
        
        self.cross_buffers = []
        for i, (sr, ss, dr, ds) in enumerate(cross_configs):
            cb = Buffer(env, id=f"Cross_Buffer_{i+1}", capacity=2)
            self.add_child_edge(cb)
            cb.connect(self.rows[sr].stages[ss].m, self.rows[dr].stages[ds].m)
            self.cross_buffers.append(cb)

class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # initializing 3 sequential stages
        self.stages = [Stage(env, id=f"Stage_{i+1}", stage_num=i+1) for i in range(3)]
        self.add_child_node(self.stages)
        
        # connecting stages sequentially
        for i in range(2):
            self.stages[i].b.connect(self.stages[i].m, self.stages[i+1].m)

class Stage(Node):
    def __init__(self, env, id, stage_num):
        super().__init__(env, id)
        # initializing machine
        self.m = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=2.0)
        self.add_child_node(self.m)
        
        # initializing buffer
        self.b = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.b)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)