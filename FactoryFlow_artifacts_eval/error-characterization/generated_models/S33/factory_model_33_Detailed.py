"""
ModelDescription:
5 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. Name machines  M00,M01,.. ,   Buffers ID are B_src_00, B_01_02,B_02_03,.
There are 5 such series. 4 such complete 5*5 systems are present in the system model. there are cross buffers between  M23 of all 5*5_sys_i are interconnected using buffers i=1,2,3,4.  Buffer used for crossconnection will have ID  B_x_1, B_x_2, and so on 
"

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed the "5 such series" are arranged in parallel to form the "5*5 system".
3. Assumed the naming convention for machines within the 5 parallel rows follows the pattern `M{row_index}{col_index}` (e.g., Row 0 has machines M00-M04, Row 2 has machines M20-M24) to logically resolve the reference to machine "M23".
4. Assumed "M23" refers to the machine at row index 2 and column index 3 within each 5*5 system.
5. Assumed the 4 "5*5 systems" are instantiated as independent blocks, interconnected only by the specified cross-buffers.
6. Assumed the cross-connections form a linear chain from System 0 to System 3 (Sys0.M23 -> Sys1.M23 -> Sys2.M23 -> Sys3.M23).
7. Assumed Buffer `B_x_i` connects the M23 of System `i-1` to the M23 of System `i` (e.g., B_x_1 connects Sys0 to Sys1).
8. Assumed the 4th buffer (`B_x_4`) connects the M23 of the last system (Sys3) to a Sink to utilize all 4 specified buffers and complete the flow.
9. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
10. Assumed a single buffer is used for all connections where the count is not explicitly specified.
11. Assumed the buffer naming convention `B_{upstream_id}_{downstream_id}` applies to all internal series connections (e.g., B_00_01 connects M00 and M01) based on the provided examples.
12. Assumed each of the 5 parallel series has its own Source and Sink nodes as implied by the instruction to use 'src' and 'sink' IDs within the series definition.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the row model (5 machines in series)
class SeriesRow(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        self.row_idx = row_idx
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines M{row}0 to M{row}4
        self.machines = [Machine(env, id=f"M{self.row_idx}{j}") for j in range(5)]
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing buffers
        self.buffers = []
        
        # Buffer from source to first machine: B_src_{row}0
        b_src = Buffer(env, id=f"B_src_{self.row_idx}0")
        self.buffers.append(b_src)
        b_src.connect(self.src, self.machines[0])
        
        # Buffers between machines: B_{row}{j}_{row}{j+1}
        for j in range(4):
            b = Buffer(env, id=f"B_{self.row_idx}{j}_{self.row_idx}{j+1}")
            self.buffers.append(b)
            b.connect(self.machines[j], self.machines[j+1])
            
        # Buffer from last machine to sink: B_{row}4_sink
        b_sink = Buffer(env, id=f"B_{self.row_idx}4_sink")
        self.buffers.append(b_sink)
        b_sink.connect(self.machines[4], self.sink)
        
        self.add_child_edge(self.buffers)

# Defining the block model (5 rows in parallel)
class SystemBlock(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 5 parallel rows
        self.rows = [SeriesRow(env, id=f"Row_{i}", row_idx=i) for i in range(5)]
        self.add_child_node(self.rows)

# Defining the top level system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 blocks
        self.blocks = [SystemBlock(env, id=f"Block_{i}") for i in range(4)]
        self.add_child_node(self.blocks)
        
        # Creating sink for cross connections (Assumption 8)
        self.cross_sink = Sink(env, id="cross_sink")
        self.add_child_node(self.cross_sink)
        
        # Creating cross buffers
        self.cross_buffers = []
        
        # Connecting M23 of each block in a chain
        # B_x_1 connects Block0.M23 to Block1.M23
        # ...
        # B_x_4 connects Block3.M23 to cross_sink
        for i in range(1, 5):
            buf = Buffer(env, id=f"B_x_{i}")
            self.cross_buffers.append(buf)
            
            # Source is M23 of block i-1 (Row 2, Machine 3)
            src_node = self.blocks[i-1].rows[2].machines[3]
            
            if i < 4:
                # Destination is M23 of block i
                dest_node = self.blocks[i].rows[2].machines[3]
                buf.connect(src_node, dest_node)
            else:
                # Destination is cross_sink
                buf.connect(src_node, self.cross_sink)
                
        self.add_child_edge(self.cross_buffers)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)