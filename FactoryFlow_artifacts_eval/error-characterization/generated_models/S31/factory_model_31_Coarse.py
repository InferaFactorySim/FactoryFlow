"""
ModelDescription:
The system consists of ten independent production lines arranged in parallel. Each production line contains ten machines connected in strict series, with a single source at the beginning and a single sink at the end. Source and sink are common for all lines. However, between the 5th machine and the 6th machine in every row, there are four parallel buffers instead of one.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
3. Inferred a repeated pattern for the production lines and created a class `ProductionLine` containing 10 machines to be instantiated 10 times.
4. Assumed a single buffer is used to connect machines in the series (e.g., Machine 1 to 2), except between the 5th and 6th machines where the specified 4 parallel buffers are used.
5. Assumed the common Source connects to the first machine of each of the 10 production lines via a separate buffer for each line.
6. Assumed the last machine of each of the 10 production lines connects to the common Sink via a separate buffer for each line.
7. Assumed default routing logic (Round Robin) for nodes with multiple output edges (Source and the 5th machine in each line) to distribute items.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the Production Line class (10 machines in series)
class ProductionLine(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 10 machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(10)]
        self.add_child_node(self.M)
        
        # Connecting machines
        # Loop through 0 to 8 to connect M[i] to M[i+1]
        for i in range(9):
            if i == 4:
                # Between 5th (M[4]) and 6th (M[5]) machine: 4 parallel buffers
                special_edges = [Buffer(env, id=f"e_special[{k}]") for k in range(4)]
                self.add_child_edge(special_edges)
                for edge in special_edges:
                    edge.connect(self.M[i], self.M[i+1])
            else:
                # Standard connection: 1 buffer
                edge = Buffer(env, id=f"e[{i}]")
                self.add_child_edge(edge)
                edge.connect(self.M[i], self.M[i+1])

# Defining the System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating 10 parallel production lines
        self.lines = [ProductionLine(env, id=f"Line[{i}]") for i in range(10)]
        self.add_child_node(self.lines)
        
        # Creating buffers from Source to the first machine of each line
        self.src_edges = [Buffer(env, id=f"src_edge[{i}]") for i in range(10)]
        self.add_child_edge(self.src_edges)
        
        # Creating buffers from the last machine of each line to Sink
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]") for i in range(10)]
        self.add_child_edge(self.sink_edges)
        
        # Connecting Source and Sink to the lines
        for i in range(10):
            self.src_edges[i].connect(self.src, self.lines[i].M[0])
            self.sink_edges[i].connect(self.lines[i].M[9], self.sink)

# Initializing SimPy environment
env = simpy.Environment()

# Creating the top-level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical IDs
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)