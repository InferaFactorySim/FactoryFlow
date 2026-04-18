"""
ModelDescription:
A linear sequence of 3 machines connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4

 MODEL ASSUMPTIONS:
1. Inferred a repeated pattern class `LinearSequence` containing a Source, 3 Machines, and a Sink to represent the linear sequence described.
2. Assumed the system consists of 4 instances of `LinearSequence` indexed 0 to 3, corresponding to rows r1 through r4.
3. Assumed machines within each sequence are indexed 0, 1, and 2, corresponding to M1, M2, and M3 respectively.
4. Used default edge type `Buffer` for all connections (Source to Machine, Machine to Machine, Machine to Sink) within the sequences as edge type was not specified.
5. Assumed the connection "between M1 in r1 and M1 in row2" is a directed flow from the first machine of the first row (index 0) to the first machine of the second row (index 1) using a Buffer.
6. Assumed the connection "between M3 in row2 and M3 in row4" is a directed flow from the third machine of the second row (index 1) to the third machine of the fourth row (index 3) using a Buffer.
7. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
8. Assumed `out_edge_selection` is set to default (Round Robin) for machines with multiple outgoing edges.
"""

# A linear sequence of 3 machines connected with a sink and a source. 4 such sequences are in parallel. 
# There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the linear sequence model
class LinearSequence(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges (buffers)
        # n+1 edges: src->M0, M0->M1, M1->M2, M2->sink
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        self.add_child_edge(self.e)
        
        # Connecting nodes
        # Source to first machine
        self.e[0].connect(self.src, self.M[0])
        
        # Machines in between
        for i in range(n-1):
            self.e[i+1].connect(self.M[i], self.M[i+1])
            
        # Last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)

# Defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        num_rows = 4
        
        # Creating 4 linear sequences
        self.rows = [LinearSequence(env, id=f"row[{i}]") for i in range(num_rows)]
        self.add_child_node(self.rows)
        
        # Creating cross-row connections
        self.cross_edges = [Buffer(env, id=f"cross_edge[{i}]") for i in range(2)]
        self.add_child_edge(self.cross_edges)
        
        # Connection 1: M1 in r1 (row 0, machine 0) to M1 in r2 (row 1, machine 0)
        self.cross_edges[0].connect(self.rows[0].M[0], self.rows[1].M[0])
        
        # Connection 2: M3 in r2 (row 1, machine 2) to M3 in r4 (row 3, machine 2)
        self.cross_edges[1].connect(self.rows[1].M[2], self.rows[3].M[2])

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