"""
ModelDescription:
Two subsystems where a machine inside Subsystem A connects directly to a specific machine deep inside Subsystem B.

 MODEL ASSUMPTIONS:
1. Inferred a top-level system containing two subsystems named `SubsystemA` and `SubsystemB`.
2. Assumed `SubsystemA` contains a linear sequence of 3 machines and `SubsystemB` contains a linear sequence of 5 machines to provide a structure where a "deep" connection is possible.
3. Added a `Source` node feeding the first machine of `SubsystemA` and a `Sink` node fed by the last machine of `SubsystemB` to ensure a valid simulation flow.
4. Interpreted the connection "deep inside Subsystem B" as a `Buffer` connecting the last machine of `SubsystemA` to the 3rd machine (index 2) of `SubsystemB`.
5. Assumed machines within each subsystem are connected in a standard linear series using single buffers.
6. Used default edge type `Buffer` for all connections.
7. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining Subsystem A: Linear sequence of 3 machines
class SubsystemA(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        # Creating machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # Creating internal buffers
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n-1)]
        self.add_child_edge(self.e)
        
        # Connecting machines in series
        for i in range(n-1):
            self.e[i].connect(self.M[i], self.M[i+1])

# Defining Subsystem B: Linear sequence of 5 machines
class SubsystemB(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        # Creating machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # Creating internal buffers
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n-1)]
        self.add_child_edge(self.e)
        
        # Connecting machines in series
        for i in range(n-1):
            self.e[i].connect(self.M[i], self.M[i+1])

# Defining the Top-Level System
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Subsystems
        self.subA = SubsystemA(env, id="SubsystemA", n=3)
        self.add_child_node(self.subA)
        
        self.subB = SubsystemB(env, id="SubsystemB", n=5)
        self.add_child_node(self.subB)
        
        # Creating Source and Sink
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating connecting edges
        # edge[0]: Source -> SubsystemA First Machine
        # edge[1]: SubsystemA Last Machine -> SubsystemB 3rd Machine (Index 2)
        # edge[2]: SubsystemB Last Machine -> Sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(3)]
        self.add_child_edge(self.edges)
        
        # Connecting Source to SubsystemA
        self.edges[0].connect(self.src, self.subA.M[0])
        
        # Connecting SubsystemA to SubsystemB (Deep connection)
        self.edges[1].connect(self.subA.M[-1], self.subB.M[2])
        
        # Connecting SubsystemB to Sink
        self.edges[2].connect(self.subB.M[-1], self.sink)

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