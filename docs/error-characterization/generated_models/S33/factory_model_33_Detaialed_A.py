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

class SeriesRow(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines M00 to M04 (for row 0)
        self.machines = [Machine(env, id=f"M{row_idx}{j}") for j in range(5)]
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        self.edges = []
        
        # Buffer from Source to first machine: B_src_{row}0
        b_src = Buffer(env, id=f"B_src_{row_idx}0")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.machines[0])
        self.edges.append(b_src)
        
        # Buffers between machines: B_{row}{j}_{row}{j+1}
        for j in range(4):
            b = Buffer(env, id=f"B_{row_idx}{j}_{row_idx}{j+1}")
            self.add_child_edge(b)
            b.connect(self.machines[j], self.machines[j+1])
            self.edges.append(b)
            
        # Buffer from last machine to Sink: B_{row}4_sink
        b_sink = Buffer(env, id=f"B_{row_idx}4_sink")
        self.add_child_edge(b_sink)
        b_sink.connect(self.machines[4], self.sink)
        self.edges.append(b_sink)

class System5x5(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 5 parallel rows
        self.rows = [SeriesRow(env, id=f"Row{r}", row_idx=r) for r in range(5)]
        self.add_child_node(self.rows)

class TopSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 complete 5*5 systems
        self.systems = [System5x5(env, id=f"Sys{i}") for i in range(4)]
        self.add_child_node(self.systems)
        
        # Creating cross buffers between M23 of adjacent systems
        # M23 corresponds to row index 2, machine index 3
        self.cross_buffers = []
        for i in range(3):
            # Buffer ID: B_x_{i+1} (B_x_1, B_x_2, B_x_3)
            buf = Buffer(env, id=f"B_x_{i+1}")
            self.add_child_edge(buf)
            
            # Source: Sys[i].Row2.M23
            src_node = self.systems[i].rows[2].machines[3]
            # Destination: Sys[i+1].Row2.M23
            dst_node = self.systems[i+1].rows[2].machines[3]
            
            buf.connect(src_node, dst_node)
            self.cross_buffers.append(buf)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = TopSystem(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)