"""
ModelDescription:
A source splits an incoming flow into 3 parallel machines and all three machines ends in a common sink. 

 MODEL ASSUMPTIONS:
1. Inferred node names: 'src' for the source, 'M' for the list of 3 machines, and 'sink' for the sink.
2. Used 'Buffer' type for all edges.
3. Used a single buffer for each connection between the Source and each Machine, and between each Machine and the Sink.
4. Used default values for all unspecified parameters (inter-arrival time, processing delays, buffer capacities).
5. Assumed the Source connects directly to each of the 3 machines via separate buffers to split the flow.
6. Assumed each of the 3 machines connects directly to the Sink via separate buffers to merge the flow.
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
        
        # Create nodes
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing 3 parallel machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(3)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Create edges
        # We need 3 edges from Source to Machines and 3 edges from Machines to Sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(6)]
        self.add_child_edge(self.edges)
        
        # Connect Source to each Machine
        for i in range(3):
            self.edges[i].connect(self.src, self.M[i])
            
        # Connect each Machine to Sink
        for i in range(3):
            self.edges[3 + i].connect(self.M[i], self.sink)

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