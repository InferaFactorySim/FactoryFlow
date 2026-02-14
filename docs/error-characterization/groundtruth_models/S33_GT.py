"""
ModelDescription:
5 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. 
Name machines  M00,M01,.. ,   Buffers ID are B_src_00, B_01_02,B_02_03,.
There are 5 such series. 4 such complete 5*5 systems are present in the system model. 
There are cross buffers between  M23 of all 5*5_sys_i are interconnected using buffers i=1,2,3,4.  
Buffer used for crossconnection will have ID  B_x_1, B_x_2, and so on

"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining a single row of 5 machines connected in series
class SeriesRow(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines M{row}0 to M{row}4
        self.M = [Machine(env, id=f"M{row_idx}{col}") for col in range(5)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing buffers
        self.buffers = []
        
        # Buffer from source to first machine (M{row}0)
        # ID pattern: B_src_{row}0
        b_src = Buffer(env, id=f"B_src_{row_idx}0")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.M[0])
        self.buffers.append(b_src)
        
        # Buffers between machines
        # ID pattern: B_{row}{col}_{row}{col+1}
        for col in range(4):
            b = Buffer(env, id=f"B_{row_idx}{col}_{row_idx}{col+1}")
            self.add_child_edge(b)
            b.connect(self.M[col], self.M[col+1])
            self.buffers.append(b)
            
        # Buffer from last machine (M{row}4) to sink
        # ID pattern: B_{row}4_sink
        b_sink = Buffer(env, id=f"B_{row_idx}4_sink")
        self.add_child_edge(b_sink)
        b_sink.connect(self.M[4], self.sink)
        self.buffers.append(b_sink)

# Defining the 5*5 system containing 5 parallel SeriesRows
class System5x5(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 5 parallel rows
        self.rows = [SeriesRow(env, id=f"Row[{i}]", row_idx=i) for i in range(5)]
        self.add_child_node(self.rows)

# Defining the global system containing 4 System5x5 blocks
class GlobalSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 systems of 5x5
        self.systems = [System5x5(env, id=f"Sys[{i}]") for i in range(4)]
        self.add_child_node(self.systems)
        
        # Cross buffers connecting M23 of Sys[i-1] to M23 of Sys[i]
        # M23 is located at row index 2, column index 3 within each 5x5 system
        self.cross_buffers = []
        
        # Connecting Sys0 -> Sys1 -> Sys2 -> Sys3
        # Using buffers B_x_1, B_x_2, B_x_3
        for i in range(1, 4):
            # Source machine: Sys[i-1].Row[2].M[3] (which is M23)
            src_node = self.systems[i-1].rows[2].M[3]
            # Destination machine: Sys[i].Row[2].M[3] (which is M23)
            dst_node = self.systems[i].rows[2].M[3]
            
            buf = Buffer(env, id=f"B_x_{i}")
            self.add_child_edge(buf)
            buf.connect(src_node, dst_node)
            self.cross_buffers.append(buf)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = GlobalSystem(env, "TOP")

# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)