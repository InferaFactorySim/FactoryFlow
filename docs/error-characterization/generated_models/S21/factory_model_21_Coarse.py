"""
ModelDescription:
There are five linear homogenous serial systems in parallel. First, and fourth series have 5 machines each, 2nd and 5th have 4. 3rd have 3 machine. There is interconnection between row1.M2 to row2.m2  , row3.m3 to row4.m4. row4.m1 to row5.m2. All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position

 MODEL ASSUMPTIONS:
1. Node names and Types for machines and buffers within the rows are chosen according to the user's description.
2. Added a common Source node named 'src' and a common Sink node named 'sink' to the system to facilitate flow, as these were not specified in the description.
3. Connected the common Source to the first machine (M[0]) of each of the five rows using a single buffer for each connection.
4. Connected the last machine of each of the five rows to the common Sink using a single buffer for each connection.
5. Used default edge type 'Buffer' for all connections (source-to-row, intra-row, inter-row, and row-to-sink) as edge types were not specified.
6. Used a single buffer for every connection between nodes, as the number of buffers was not specified.
7. Used default values for all missing parameters (processing delays, buffer capacities, source inter-arrival times) for all components.
8. Inferred a repeated pattern for the linear rows and assumed a parameterized class (e.g., `LinearRow`) will be created and instantiated 5 times with machine counts of 5, 4, 3, 5, and 4 respectively.
9. Mapped row references (row1 through row5) to 0-based indices (index 0 through 4) for implementation.
10. Interpreted machine references in the interconnections (e.g., M2, M3) as referring to the specific Machine ID (e.g., M[2], M[3]) within that row.
11. Assumed the direction of flow for interconnections is from the first mentioned node to the second (e.g., from row1.M2 to row2.m2).
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
        # Machines named M[1] to M[n]
        self.M = [Machine(env, id=f"M[{i+1}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # Buffers named B[1] to B[n-1] connecting machines in series
        if n > 1:
            self.B = [Buffer(env, id=f"B[{i+1}]") for i in range(n-1)]
            self.add_child_edge(self.B)
            for i in range(n-1):
                self.B[i].connect(self.M[i], self.M[i+1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source and Sink
        self.src = Source(env, id="src")
        self.sink = Sink(env, id="sink")
        self.add_child_node([self.src, self.sink])
        
        # Create 5 rows with specified machine counts
        # Row 1: 5, Row 2: 4, Row 3: 3, Row 4: 5, Row 5: 4
        row_counts = [5, 4, 3, 5, 4]
        self.rows = [LinearRow(env, id=f"row{i+1}", n=count) for i, count in enumerate(row_counts)]
        self.add_child_node(self.rows)
        
        self.edges = []
        edge_idx = 0
        
        # Connect Source to the first machine of each row
        for row in self.rows:
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.src, row.M[0])
            self.edges.append(e)
            edge_idx += 1
            
        # Connect the last machine of each row to Sink
        for row in self.rows:
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(row.M[-1], self.sink)
            self.edges.append(e)
            edge_idx += 1
            
        # Interconnections between rows
        # Format: (source_row_idx, source_machine_idx, dest_row_idx, dest_machine_idx)
        # Note: Machine indices are 0-based (M1->0, M2->1, etc.)
        interconnects = [
            (0, 1, 1, 1), # row1.M2 -> row2.m2
            (2, 2, 3, 3), # row3.m3 -> row4.m4
            (3, 0, 4, 1)  # row4.m1 -> row5.m2
        ]
        
        for r_src, m_src, r_dst, m_dst in interconnects:
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.rows[r_src].M[m_src], self.rows[r_dst].M[m_dst])
            self.edges.append(e)
            edge_idx += 1

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