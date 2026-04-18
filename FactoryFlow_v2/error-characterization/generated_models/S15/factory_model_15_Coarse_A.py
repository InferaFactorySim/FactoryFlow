"""
ModelDescription:
3 machines each with a delay of 4,3,2 connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them


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

class Stage(Node):
    def __init__(self, env, id, machine_name, delay, capacity, is_stage_2=False):
        super().__init__(env, id)
        # Machine
        self.M = Machine(env, id=machine_name, processing_delay=delay, work_capacity=capacity)
        self.add_child_node(self.M)
        
        # Buffer
        # Assumption 8: Standard buffer of Stage 2 is named 'Stage_2_B1'
        buf_name = "Stage_2_B1" if is_stage_2 else "B1"
        self.B = Buffer(env, id=buf_name, capacity=2)
        self.add_child_edge(self.B)
        
        # Extra Buffers for Stage 2
        self.extras = []
        if is_stage_2:
            self.extras = [Buffer(env, id=f"B_2_3_{k+1}", capacity=2) for k in range(2)]
            self.add_child_edge(self.extras)

class Line(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)
        
        # Source Buffer
        self.b_src = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.b_src)
        
        # Stages
        self.stages = []
        delays = [4.0, 3.0, 2.0]
        caps = [2, 3, 4]
        machine_names = ["M1", "M2", "M3"]
        
        for i in range(3):
            is_s2 = (i == 1)
            s = Stage(env, id=f"Stage_{i+1}", machine_name=machine_names[i], delay=delays[i], capacity=caps[i], is_stage_2=is_s2)
            self.stages.append(s)
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Connections
        # SRC -> B_src -> Stage 1 M
        self.b_src.connect(self.src, self.stages[0].M)
        
        # Stage 1 M -> Stage 1 B -> Stage 2 M
        self.stages[0].B.connect(self.stages[0].M, self.stages[1].M)
        
        # Stage 2 M -> [B, extras] -> Stage 3 M
        self.stages[1].B.connect(self.stages[1].M, self.stages[2].M)
        for eb in self.stages[1].extras:
            eb.connect(self.stages[1].M, self.stages[2].M)
            
        # Stage 3 M -> Stage 3 B -> Sink
        self.stages[2].B.connect(self.stages[2].M, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # 4 Parallel Lines (Rows)
        self.rows = [Line(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Cross Buffer 1: Row 1 Stage 1 M -> Row 2 Stage 1 M
        self.cb1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cb1)
        self.cb1.connect(self.rows[0].stages[0].M, self.rows[1].stages[0].M)
        
        # Cross Buffer 2: Row 2 Stage 3 M -> Row 4 Stage 3 M
        self.cb2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cb2)
        self.cb2.connect(self.rows[1].stages[2].M, self.rows[3].stages[2].M)

# Simulation Setup
env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)