"""
ModelDescription:
A hierarchical system where a top-level cell contains a machine, a nested hierarchical subsystem with parallel machines, and a final machine arranged in series between a source and a sink.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description; generic names (e.g., `System`, `ParallelSubsystem`, `M_start`, `M_end`, `M_parallel`) are inferred for unnamed components.
2. Assumed the "nested hierarchical subsystem" is defined as a separate class containing the parallel machines.
3. Assumed the number of parallel machines in the nested subsystem is 3, as the quantity was not specified.
4. Used default edge type `Buffer` for all connections as edge type was not specified.
5. Used a single `Buffer` for every connection between nodes as the number of buffers was not specified.
6. Inferred logical flow: Source connects to the first machine (`M_start`), `M_start` connects to the parallel subsystem, the parallel subsystem connects to the final machine (`M_end`), and `M_end` connects to the Sink.
7. Assumed the connection topology involves `M_start` connecting to *each* of the 3 parallel machines individually, and *each* of the 3 parallel machines connecting to `M_end` individually.
8. Used default values for all missing parameters (inter-arrival times, processing delays, capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the nested hierarchical subsystem with parallel machines
class ParallelSubsystem(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        # Creating parallel machines
        self.M = [Machine(env, id=f"M_parallel[{i}]") for i in range(n)]
        self.add_child_node(self.M)

# Defining the top-level system
class System(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Creating M_start
        self.M_start = Machine(env, id="M_start")
        self.add_child_node(self.M_start)
        
        # Creating Nested Subsystem
        self.subsystem = ParallelSubsystem(env, id="ParallelSubsystem", n=3)
        self.add_child_node(self.subsystem)
        
        # Creating M_end
        self.M_end = Machine(env, id="M_end")
        self.add_child_node(self.M_end)
        
        # Creating Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating Edges
        
        # Edge from Source to M_start
        self.edge_src = Buffer(env, id="edge_src")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.source, self.M_start)
        
        # Edges from M_start to Parallel Subsystem Machines
        self.edges_in = [Buffer(env, id=f"edge_in[{i}]") for i in range(3)]
        self.add_child_edge(self.edges_in)
        for i in range(3):
            self.edges_in[i].connect(self.M_start, self.subsystem.M[i])
            
        # Edges from Parallel Subsystem Machines to M_end
        self.edges_out = [Buffer(env, id=f"edge_out[{i}]") for i in range(3)]
        self.add_child_edge(self.edges_out)
        for i in range(3):
            self.edges_out[i].connect(self.subsystem.M[i], self.M_end)
            
        # Edge from M_end to Sink
        self.edge_sink = Buffer(env, id="edge_sink")
        self.add_child_edge(self.edge_sink)
        self.edge_sink.connect(self.M_end, self.sink)

# Initializing SimPy environment
env = simpy.Environment()

# Creating the system model
TOP = System(env, "TOP")

# Filling hierarchical IDs
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)