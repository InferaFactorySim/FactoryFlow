"""
ModelDescription:
3 machines connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. In every row and the 2nd and 3rd machines have 3 buffers in between them

 MODEL ASSUMPTIONS:
1.  Node names and Types are chosen according to the user's description.
2.  A repeated pattern class is created for the linear sequence containing a Source, 3 Machines, and a Sink.
3.  The system is assumed to consist of 4 instances of this sequence class instantiated in parallel.
4.  Inside each sequence, the flow is inferred as Source -> Machine 1 -> Machine 2 -> Machine 3 -> Sink.
5.  Used a single Buffer for all connections where the number of buffers was not explicitly specified (Source to Machine 1, Machine 1 to Machine 2, Machine 3 to Sink).
6.  The 3 buffers specified between the 2nd and 3rd machines in every row are assumed to be connected in parallel.
7.  The connection between "M1 in r1" and "M1 in row2" is assumed to be a Buffer with flow direction from Row 1 (index 0) to Row 2 (index 1).
8.  The connection between "M3 in row2" and "M3 in row4" is assumed to be a Buffer with flow direction from Row 2 (index 1) to Row 4 (index 3).
9.  Row references (r1, row2, row4) are mapped to 0-based indices 0, 1, and 3 respectively.
10. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class RowSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing 3 machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(3)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        self.edges = []
        edge_idx = 0
        
        # Connect Source to M[0] (Machine 1)
        e_src = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e_src)
        e_src.connect(self.source, self.M[0])
        self.edges.append(e_src)
        edge_idx += 1
        
        # Connect M[0] (Machine 1) to M[1] (Machine 2)
        e_m1_m2 = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e_m1_m2)
        e_m1_m2.connect(self.M[0], self.M[1])
        self.edges.append(e_m1_m2)
        edge_idx += 1
        
        # Connect M[1] (Machine 2) to M[2] (Machine 3) with 3 parallel buffers
        for k in range(3):
            e_m2_m3 = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e_m2_m3)
            e_m2_m3.connect(self.M[1], self.M[2])
            self.edges.append(e_m2_m3)
            edge_idx += 1
            
        # Connect M[2] (Machine 3) to Sink
        e_sink = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e_sink)
        e_sink.connect(self.M[2], self.sink)
        self.edges.append(e_sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 parallel row sequences
        self.rows = [RowSequence(env, id=f"row[{i}]") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Creating cross-connection edges
        self.cross_edges = []
        edge_idx = 0
        
        # Connection between M1 in r1 (index 0) and M1 in row2 (index 1)
        # M1 corresponds to M[0] in the row sequence
        e1 = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e1)
        e1.connect(self.rows[0].M[0], self.rows[1].M[0])
        self.cross_edges.append(e1)
        edge_idx += 1
        
        # Connection between M3 in row2 (index 1) and M3 in row4 (index 3)
        # M3 corresponds to M[2] in the row sequence
        e2 = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e2)
        e2.connect(self.rows[1].M[2], self.rows[3].M[2])
        self.cross_edges.append(e2)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)