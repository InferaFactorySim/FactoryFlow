"""
ModelDescription:
A linear sequence of 3 machines connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. MAchines have delay 2 and buffers have capacity=2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source: SRC, Sink: SINK, Machines: Stage_i_M1, Buffers: Stage_i_B1, Cross Buffers: Cross_Buffer_x).
2. Assumed the statement "All machines have a processing_Delay of 2" overrides the earlier description of "processing delay of 4.0 seconds" for the machines in the stages.
3. Assumed the system consists of 4 parallel rows, where each row contains 3 sequential "Stage" subsystems.  "Stage_i" subsystem has a machine `Stage_i_M1` and  a buffer`Stage_i_B1`.  Every subsystem Ri has a separate Source with ID=SRC and sink with ID=SINK. Src is followed by a buffer B_src_1 in every subsystem and three Stage_i i=1,2,3 subsystems in series and a sink at the end
4. Assumed the naming convention `Stage_i_M1` and `Stage_i_B1` applies within the context of each stage subsystem, and unique hierarchical IDs are generated for the 4 parallel rows (e.g., Row_x_Stage_y_M1)., i=1,2,3
5. Assumed the separate Sources connects to the input (Machine) of Stage 1 in all 4 parallel rows via separate buffers.
6. Assumed the output (Buffer) of Stage 3 in all 4 parallel rows connects to the separate Sink via separate buffers.
7. Assumed the reference to "M1" in the cross-connection instruction refers to the machine inside Stage 1, and "M3" refers to the machine inside Stage 3.
8. Assumed the direction of flow for cross-connections is from the lower row index to the higher row index (Row 1 Stage 1 Machine -> Row 2 Stage 1 Machine, and Row 2 Stage 3 Machine -> Row 4 Stage 3 Machine).  Row index starts from 1
9. Used default Buffer type with capacity 2 for all connections not explicitly defined (including Source-to-Row, Row-to-Sink, and Cross-Buffers), based on the general instruction "buffers have a capacity of 2".
10. Used a single buffer for all connections where the number of buffers was not specified.
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
        # Machine with delay 2
        self.M1 = Machine(env, id=f"Stage_{stage_num}_M1", processing_delay=2)
        self.add_child_node(self.M1)
        
        # Buffer with capacity 2
        self.B1 = Buffer(env, id=f"Stage_{stage_num}_B1", capacity=2)
        self.add_child_edge(self.B1)

class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)
        
        # Buffer after Source
        self.B_src_1 = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.B_src_1)
        
        # 3 Stages
        self.stages = [Stage(env, id=f"Stage_{i+1}", stage_num=i+1) for i in range(3)]
        self.add_child_node(self.stages)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Connect Source -> B_src_1 -> Stage 1 M1
        self.B_src_1.connect(self.source, self.stages[0].M1)
        
        # Connect Stage i -> Stage i+1
        for i in range(2):
            self.stages[i].B1.connect(self.stages[i].M1, self.stages[i+1].M1)
            
        # Connect Last Stage -> Sink
        self.stages[2].B1.connect(self.stages[2].M1, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # 4 Parallel Rows
        self.rows = [Row(env, id=f"Row_{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Cross Connections
        # M1 in r1 (Row 1) -> M1 in row2 (Row 2)
        self.cross_buffer_0 = Buffer(env, id="Cross_Buffer_0", capacity=2)
        self.add_child_edge(self.cross_buffer_0)
        self.cross_buffer_0.connect(self.rows[0].stages[0].M1, self.rows[1].stages[0].M1)
        
        # M3 in row2 (Row 2) -> M3 in row4 (Row 4)
        self.cross_buffer_1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross_buffer_1)
        self.cross_buffer_1.connect(self.rows[1].stages[2].M1, self.rows[3].stages[2].M1)

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