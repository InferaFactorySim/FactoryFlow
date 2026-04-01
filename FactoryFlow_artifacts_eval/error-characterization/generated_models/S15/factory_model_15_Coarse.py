"""
ModelDescription:
3 machines each with a delay of 4,3,2 connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every row and the 2nd and 3rd machines have 3 buffers in between them
 MODEL ASSUMPTIONS:
1. Assumed a single common Source and a single common Sink for the entire system, with the 4 sequences connected in parallel between them.
2. Inferred a repeated pattern class (e.g., `RowSequence`) for the sequence of 3 machines, which is instantiated 4 times.
3. Node names and IDs are inferred (e.g., `src`, `sink`, `row_0`, `M_0`) as they were not explicitly provided.
4. Used default values for all missing parameters (Source inter-arrival time, Buffer capacity, etc.) for all components.
5. Used `Buffer` for all connections (edges) as the default edge type.
6. Assumed a single buffer is used for all connections (Source to Row start, M1 to M2, Row end to Sink, and cross-connections) except between the 2nd and 3rd machines in every row where 3 buffers are explicitly specified.
7. Assumed the "3 buffers" between the 2nd and 3rd machines are connected in parallel.
8. Assumed the flow for the cross-connections follows the order of mention or increasing row index: from Row 1 (Index 0) Machine 1 to Row 2 (Index 1) Machine 1, and from Row 2 (Index 1) Machine 3 to Row 4 (Index 3) Machine 3.
9. Assumed "M1", "M2", "M3" refer to the 1st, 2nd, and 3rd machines in the sequence respectively.
"""

import simpy
import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class RowSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 3 machines with specific delays: 4, 3, 2
        delays = [4, 3, 2]
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=delays[i]) for i in range(3)]
        self.add_child_node(self.M)
        
        self.edges = []
        edge_idx = 0
        
        # Connection between M1 (index 0) and M2 (index 1): 1 buffer
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.M[0], self.M[1])
        self.edges.append(e)
        edge_idx += 1
        
        # Connection between M2 (index 1) and M3 (index 2): 3 buffers in parallel
        for k in range(3):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.M[1], self.M[2])
            self.edges.append(e)
            edge_idx += 1

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # 4 Parallel Rows
        self.rows = [RowSequence(env, id=f"row[{i}]") for i in range(4)]
        self.add_child_node(self.rows)
        
        self.edges = []
        edge_idx = 0
        
        # Connect Source to first machine (M[0]) of each row
        for i in range(4):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.source, self.rows[i].M[0])
            self.edges.append(e)
            edge_idx += 1
            
        # Connect last machine (M[2]) of each row to Sink
        for i in range(4):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.rows[i].M[2], self.sink)
            self.edges.append(e)
            edge_idx += 1
            
        # Cross connection: M1 in r1 (row 0) to M1 in row2 (row 1)
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.rows[0].M[0], self.rows[1].M[0])
        self.edges.append(e)
        edge_idx += 1
        
        # Cross connection: M3 in row2 (row 1) to M3 in row4 (row 3)
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.rows[1].M[2], self.rows[3].M[2])
        self.edges.append(e)
        edge_idx += 1

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