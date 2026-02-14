"""
ModelDescription:
There are five linear homogenous serial systems in parallel. First and fourth series have 5 machines each, 2nd and 5th have 4. 3rd have 3 machine. There is interconnection between row1.M2 to row2.m2  , row3.m3 to row4.m4. row4.m1 to row5.m2. All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. all rows are named as rowi i=1,2,3,4. Use ID Bi i=1,2,3 for all buffers outside LinearRow class.


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. A `LinearRow` class is created to represent the repeated pattern of linear serial systems, parameterized by the number of machines `n`.
3. A single Sink node named "sink" is added to the system to collect processed parts, as it is not explicitly mentioned but required for flow termination.
4. The common Source ("src") is connected to the first machine (M[0]) id 'M[1]' of all five parallel rows using buffers.
5. The last machine of each of the five parallel rows is connected to the common Sink using buffers.
6. Within each `LinearRow`, machines are connected in a linear series (M[i] to M[i+1]) using a single buffer between them.
7.  Used default edge type 'Buffer' for all connections ( intra-row) as edge types were not specified. Buffer ID used is "B[i+1]" and default edge type 'Buffer' for all connections ( intra-row) as edge types were not specified. Buffer ID is "Bi" where i=1,2,3 for buffers connecting src to machine in linear row and last machine in row to sink.

8. A single buffer is used for every connection between nodes.
9. The specific interconnections described (e.g., "row1.M2") are mapped to 0-based indices for implementation (e.g., Row 1 Machine 2 becomes `rows[0].M[1]`, Row 3 Machine 3 becomes `rows[2].M[2]`, etc.).
10. The capacity of 2 specified for "all buffers" applies to the internal row buffers, the source/sink connection buffers, and the cross-row interconnection buffers.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class LinearRow(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        # Machines M[1] to M[n]
        self.M = [Machine(env, id=f"M[{i+1}]", processing_delay=2) for i in range(n)]
        self.add_child_node(self.M)
        
        # Buffers B[1] to B[n-1]
        self.buffers = [Buffer(env, id=f"B[{i+1}]", capacity=2) for i in range(n-1)]
        self.add_child_edge(self.buffers)
        
        # Connect machines in series
        for i in range(n-1):
            self.buffers[i].connect(self.M[i], self.M[i+1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source
        self.source = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.source)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # 5 Parallel Rows
        # Row 1: 5 machines, Row 2: 4, Row 3: 3, Row 4: 5, Row 5: 4
        row_counts = [5, 4, 3, 5, 4]
        self.rows = [LinearRow(env, id=f"row{i+1}", n=count) for i, count in enumerate(row_counts)]
        self.add_child_node(self.rows)
        
        self.ext_buffers = []
        buf_count = 1
        
        # Connect Source to first machine of each row
        for r in self.rows:
            b = Buffer(env, id=f"B{buf_count}", capacity=2)
            self.add_child_edge(b)
            b.connect(self.source, r.M[0])
            self.ext_buffers.append(b)
            buf_count += 1
            
        # Connect last machine of each row to Sink
        for r in self.rows:
            b = Buffer(env, id=f"B{buf_count}", capacity=2)
            self.add_child_edge(b)
            b.connect(r.M[-1], self.sink)
            self.ext_buffers.append(b)
            buf_count += 1
            
        # Interconnections
        # row1.M2 (idx 0, 1) -> row2.m2 (idx 1, 1)
        # row3.m3 (idx 2, 2) -> row4.m4 (idx 3, 3)
        # row4.m1 (idx 3, 0) -> row5.m2 (idx 4, 1)
        interconnections = [(0, 1, 1, 1), (2, 2, 3, 3), (3, 0, 4, 1)]
        
        for src_r, src_m, dst_r, dst_m in interconnections:
            b = Buffer(env, id=f"B{buf_count}", capacity=2)
            self.add_child_edge(b)
            b.connect(self.rows[src_r].M[src_m], self.rows[dst_r].M[dst_m])
            self.ext_buffers.append(b)
            buf_count += 1
            
        # Set work_capacity=2 for machines with multiple inputs
        # Targets: row2.m2 (1,1), row4.m4 (3,3), row5.m2 (4,1)
        multi_input_targets = [(1, 1), (3, 3), (4, 1)]
        for r, m in multi_input_targets:
            self.rows[r].M[m].work_capacity = 2

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)