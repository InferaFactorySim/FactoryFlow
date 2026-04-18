"""
ModelDescription:
A system with 5 machines connected in parallel 

 MODEL ASSUMPTIONS:
1. Added a Source node named 'src' and a Sink node named 'sink' to the system to facilitate the flow of parts through the parallel machines.
2. Inferred machine names as 'M[0]' through 'M[4]'.
3. Assumed the topology consists of the Source connecting to each of the 5 machines, and each of the 5 machines connecting to the Sink.
4. Used 'Buffer' for all connections, with a single buffer placed between any two connected nodes.
5. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id, n=5):
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
        
        # Creating edges
        # We need n edges from source to machines and n edges from machines to sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(2 * n)]
        self.add_child_edge(self.edges)
        
        # Connecting nodes with edges
        for i in range(n):
            # Connect source to each machine
            self.edges[i].connect(self.src, self.M[i])
            # Connect each machine to sink (using the second half of the edges list)
            self.edges[n + i].connect(self.M[i], self.sink)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system model
TOP = SystemModel(env, "TOP", n=5)

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)