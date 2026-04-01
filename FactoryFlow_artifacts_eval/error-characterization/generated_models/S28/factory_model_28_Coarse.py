"""
ModelDescription:
A system composed of a repeated hierarchical subsystem, where each subsystem contains two machines in series connected by a buffer.  Three such subsystems are connected sequentially, forming a linear hierarchical structure with a single source and a single sink. The subsystems are heterogeneous.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Inferred a class named `Subsystem` for the repeated hierarchical pattern containing two machines in series.
3. Inferred machine IDs within the `Subsystem` as `M[0]` and `M[1]`.
4. Inferred top-level system class name as `SystemModel`.
5. Used default edge type `Buffer` for all connections where edge type was not specified (specifically between the sequential subsystems and connecting the source/sink).
6. Used a single buffer for all connections between nodes and subsystems where the number of buffers was not specified.
7. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
8. Inferred logical flow: Source -> Buffer -> Subsystem[0] -> Buffer -> Subsystem[1] -> Buffer -> Subsystem[2] -> Buffer -> Sink.
9. Inferred logical flow within `Subsystem`: `M[0]` -> Buffer -> `M[1]`.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating machines M[0] and M[1]
        self.M = [Machine(env, id=f"M[{i}]") for i in range(2)]
        self.add_child_node(self.M)
        
        # Creating buffer between machines
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(1)]
        self.add_child_edge(self.e)
        
        # Connecting M[0] -> Buffer -> M[1]
        self.e[0].connect(self.M[0], self.M[1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Creating 3 Subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem[{i}]") for i in range(3)]
        self.add_child_node(self.subsystems)
        
        # Creating Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating buffers for connections between subsystems and endpoints
        # 1 from Source, 2 between subsystems, 1 to Sink = 4 buffers
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(4)]
        self.add_child_edge(self.edges)
        
        # Connecting Source -> Subsystem[0] (M[0])
        self.edges[0].connect(self.source, self.subsystems[0].M[0])
        
        # Connecting Subsystems sequentially
        for i in range(2):
            self.edges[i+1].connect(self.subsystems[i].M[1], self.subsystems[i+1].M[0])
            
        # Connecting Subsystem[2] (M[1]) -> Sink
        self.edges[3].connect(self.subsystems[2].M[1], self.sink)

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