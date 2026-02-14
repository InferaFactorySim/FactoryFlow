"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description, with generic IDs (e.g., "M", "src", "sink") assigned where specific names were not provided.
2. A class named `Subsystem` (or similar) is inferred to represent the repeated structure of one Source connected to 5 Machines in series.
3. Used default edge type `Buffer` for all connections (between machines in series, from subsystems to the common sink, and for the specific cross-connections described) as edge type was not specified.
4. Used a single buffer for every connection between two nodes.
5. Assumed the "end" of the subsystem refers to the last machine (5th machine) in the series, which is connected to the common sink.
6. Interpreted "second subsystem" as index 1, "third subsystem" as index 2, and "fourth subsystem" as index 3 (0-based indexing).
7. Interpreted "second machine" as index 1, "third machine" as index 2, and "fourth machine" as index 3 within their respective subsystems.
8. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id, num_subsystems=4):
        super().__init__(env, id)
        
        # Creating subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem[{i}]") for i in range(num_subsystems)]
        self.add_child_node(self.subsystems)
        
        # Creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Connecting subsystems to common sink
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]") for i in range(num_subsystems)]
        self.add_child_edge(self.sink_edges)
        
        for i in range(num_subsystems):
            # Connect the last machine (index -1) of each subsystem to the common sink
            self.sink_edges[i].connect(self.subsystems[i].M[-1], self.sink)
            
        # Cross connections
        # The third machine in second subsystem (index 1, machine 2) 
        # connected to fourth machine in third subsystem (index 2, machine 3)
        # and second machine in fourth subsystem (index 3, machine 1)
        
        self.cross_edges = [Buffer(env, id=f"cross_edge[{i}]") for i in range(2)]
        self.add_child_edge(self.cross_edges)
        
        # Connection 1: Subsystem[1].M[2] -> Subsystem[2].M[3]
        self.cross_edges[0].connect(self.subsystems[1].M[2], self.subsystems[2].M[3])
        
        # Connection 2: Subsystem[1].M[2] -> Subsystem[3].M[1]
        self.cross_edges[1].connect(self.subsystems[1].M[2], self.subsystems[3].M[1])

class Subsystem(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # Creating edges (1 from source + n-1 between machines = n edges)
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n)]
        self.add_child_edge(self.e)
        
        # Connecting source to first machine
        self.e[0].connect(self.src, self.M[0])
        
        # Connecting machines in series
        for i in range(n-1):
            self.e[i+1].connect(self.M[i], self.M[i+1])

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