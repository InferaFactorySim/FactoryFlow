"""
ModelDescription:
There are five linear homogenous serial systems in parallel. First and fourth series have 5 machines each, 2nd and 5th have 4. 3rd have 3 machine. There is interconnection between row1.M2 to row2.m2  , row3.m3 to row4.m4. row4.m1 to row5.m2. All machines are name as M[i], i is the position. and all buffers as B[i], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. A `LinearRow` class is created to represent the repeated pattern of linear serial systems, parameterized by the number of machines `n`.
3. A single Sink node named "sink" is added to the system to collect processed parts, as it is not explicitly mentioned but required for flow termination.
4. The common Source ("src") is connected to the first machine (M[0]) of all five parallel rows using buffers.
5. The last machine of each of the five parallel rows is connected to the common Sink using buffers.
6. Within each `LinearRow`, machines are connected in a linear series (M[i] to M[i+1]) using a single buffer between them.
7. All connections (Source to Rows, Internal Row connections, Cross-row connections, and Rows to Sink) use the 'Buffer' edge type.
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

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating common source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # Creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Defining row configurations based on description
        # Row 1: 5 machines, Row 2: 4, Row 3: 3, Row 4: 5, Row 5: 4
        row_counts = [5, 4, 3, 5, 4]
        
        # Creating parallel linear rows
        self.rows = [LinearRow(env, id=f"row[{i}]", n=count) for i, count in enumerate(row_counts)]
        self.add_child_node(self.rows)
        
        # Connecting Source to the first machine of each row
        self.src_edges = [Buffer(env, id=f"src_edge[{i}]", capacity=2) for i in range(len(row_counts))]
        self.add_child_edge(self.src_edges)
        for i in range(len(row_counts)):
            self.src_edges[i].connect(self.src, self.rows[i].M[0])
            
        # Connecting the last machine of each row to Sink
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]", capacity=2) for i in range(len(row_counts))]
        self.add_child_edge(self.sink_edges)
        for i in range(len(row_counts)):
            self.sink_edges[i].connect(self.rows[i].M[-1], self.sink)
            
        # Creating cross-row interconnections
        # Mapping description to 0-based indices:
        # row1.M2 -> row2.m2  => rows[0].M[1] -> rows[1].M[1]
        # row3.m3 -> row4.m4  => rows[2].M[2] -> rows[3].M[3]
        # row4.m1 -> row5.m2  => rows[3].M[0] -> rows[4].M[1]
        cross_connections = [
            (0, 1, 1, 1),
            (2, 2, 3, 3),
            (3, 0, 4, 1)
        ]
        
        self.cross_edges = [Buffer(env, id=f"cross_edge[{i}]", capacity=2) for i in range(len(cross_connections))]
        self.add_child_edge(self.cross_edges)
        
        for i, (r_src, m_src, r_dst, m_dst) in enumerate(cross_connections):
            self.cross_edges[i].connect(self.rows[r_src].M[m_src], self.rows[r_dst].M[m_dst])
            # Setting work_capacity to 2 for machines with multiple input edges
            self.rows[r_dst].M[m_dst].work_capacity = 2

class LinearRow(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        
        # Creating machines with processing delay of 2
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=2) for i in range(n)]
        self.add_child_node(self.M)
        
        # Creating buffers with capacity of 2
        self.B = [Buffer(env, id=f"B[{i}]", capacity=2) for i in range(n-1)]
        self.add_child_edge(self.B)
        
        # Connecting machines in series
        for i in range(n-1):
            self.B[i].connect(self.M[i], self.M[i+1])

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