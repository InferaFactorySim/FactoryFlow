"""
ModelDescription:
There are five linear homogenous serial systems in parallel. First, and fourth series have 5 machines each, 2nd and 5th have 4. 3rd have 3 machine. There is interconnection between row1.M2 to row2.m2  , row3.m3 to row4.m4. row4.m1 to row5.m2. All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position.  All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. USe ID B[i+1] for all buffers in the model

 MODEL ASSUMPTIONS:
1. Node names and Types for machines and buffers within the rows are chosen according to the user's description.
2. Added a common Source node named 'src' and a common Sink node named 'sink' to the system to facilitate flow, as these were not specified in the description.
3. Connected the common Source to the first machine (M[0]) of each of the five rows using a single buffer for each connection.
4. Connected the last machine of each of the five rows to the common Sink using a single buffer for each connection.
5. Used default edge type 'Buffer' for all connections (source-to-row, intra-row, inter-row, and row-to-sink) as edge types were not specified. Buffer ID is "B[i+1]"
6. Used a single buffer for every connection between nodes, as the number of buffers was not specified.
7. Used default values for all missing parameters (processing delays, buffer capacities, source inter-arrival times) for all components.
8. Inferred a repeated pattern for the linear rows and assumed a parameterized class (e.g., `LinearRow`) will be created and instantiated 5 times with machine counts of 5, 4, 3, 5, and 4 respectively.
9. Mapped row references (row1 through row5) to 0-based indices (index 0 through 4) for implementation.
10. Interpreted machine references in the interconnections (e.g., M2, M3) as referring to the specific Machine ID (e.g., M[2], M[3]) within that row.
11. Assumed the direction of flow for interconnections is from the first mentioned node to the second (e.g., from row1.M2 to row2.m2).
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Row configurations: 5 rows with specific machine counts
        row_counts = [5, 4, 3, 5, 4]
        self.rows = [LinearRow(env, id=f"row{i+1}", n=count) for i, count in enumerate(row_counts)]
        self.add_child_node(self.rows)
        
        # Connecting Source to first machine of each row
        self.src_edges = [Buffer(env, id=f"src_edge[{i}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.src_edges)
        for i in range(5):
            self.src_edges[i].connect(self.src, self.rows[i].M[0])
            
        # Connecting last machine of each row to Sink
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.sink_edges)
        for i in range(5):
            self.sink_edges[i].connect(self.rows[i].M[-1], self.sink)
            
        # Interconnections
        # row1.M2 (idx 1) -> row2.m2 (idx 1)
        # row3.m3 (idx 2) -> row4.m4 (idx 3)
        # row4.m1 (idx 0) -> row5.m2 (idx 1)
        # Format: (src_row_idx, src_m_idx, dst_row_idx, dst_m_idx)
        inter_conns = [
            (0, 1, 1, 1),
            (2, 2, 3, 3),
            (3, 0, 4, 1)
        ]
        
        self.inter_edges = [Buffer(env, id=f"inter_edge[{i}]", capacity=2) for i in range(len(inter_conns))]
        self.add_child_edge(self.inter_edges)
        
        for i, (sr, sm, dr, dm) in enumerate(inter_conns):
            source_node = self.rows[sr].M[sm]
            dest_node = self.rows[dr].M[dm]
            
            # Update work capacity for machines with multiple inputs
            dest_node.work_capacity = 2
            
            self.inter_edges[i].connect(source_node, dest_node)

class LinearRow(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        
        # initializing machines
        # M[i+1] naming convention, processing_delay=2
        self.M = [Machine(env, id=f"M[{i+1}]", processing_delay=2, work_capacity=1) for i in range(n)]
        self.add_child_node(self.M)
        
        # initializing buffers
        # B[i+1] naming convention, capacity=2
        self.B = [Buffer(env, id=f"B[{i+1}]", capacity=2) for i in range(n-1)]
        self.add_child_edge(self.B)
        
        # connecting machines in series
        for i in range(n-1):
            self.B[i].connect(self.M[i], self.M[i+1])

# initiliating simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)