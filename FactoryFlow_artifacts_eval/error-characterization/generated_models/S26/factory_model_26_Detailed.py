"""
ModelDescription:
Subsystem_A (3 machines in series) and Subsystem_B (3 machines in series). A custom edge connects Subsystem_A.M2 to Subsystem_B.M3.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. Inferred a repeated pattern of "3 machines in series" and created a reusable class for this subsystem to instantiate both Subsystem_A and Subsystem_B.
3. Inferred machine IDs within the subsystems as 'src',  `M[1]`, `M[2]`, and `M[3]` and 'sink' to align with the user's specific reference to "M2" and "M3" within a 3-machine system.
4. Used default Node Type `Machine` for all nodes within the subsystems as not specified.
5. Used default Edge Type `Buffer` for all connections, including the internal series connections and the custom edge connecting the subsystems.
6. Used a single buffer for all connections between nodes where the number of buffers was not specified.
7. Inferred the need for a separate `src` and `sink` to create a valid simulation flow.
8. Assumed the separate source `src` connects to the first machine of Subsystem_A (`M[1]`) and Source connects to Subsystem_B (`M[1]`)
9. Assumed the last machine of Subsystem_B (`M[3]`)  and  Subsystem_A (`M[3]`)connects to the global `sink` and 'sink'.
10. Assumed the custom edge flows from `Subsystem_A.M[2]` to `Subsystem_B.M[3]`.
11. Used default values for all missing parameters (processing delays, capacities, inter-arrival times) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SeriesSubsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Creating 3 machines M[1], M[2], M[3]
        self.M = [Machine(env, id=f"M[{i+1}]") for i in range(3)]
        self.add_child_node(self.M)
        
        # Creating sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        # 1 from src to M[1], 2 between machines, 1 from M[3] to sink = 4 edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(4)]
        self.add_child_edge(self.edges)
        
        # Connect src to M[1]
        self.edges[0].connect(self.src, self.M[0])
        
        # Connect machines in series
        for i in range(2):
            self.edges[i+1].connect(self.M[i], self.M[i+1])
            
        # Connect last machine to sink
        self.edges[3].connect(self.M[2], self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Instantiate Subsystem_A
        self.Subsystem_A = SeriesSubsystem(env, id="Subsystem_A")
        self.add_child_node(self.Subsystem_A)
        
        # Instantiate Subsystem_B
        self.Subsystem_B = SeriesSubsystem(env, id="Subsystem_B")
        self.add_child_node(self.Subsystem_B)
        
        # Create custom edge connecting Subsystem_A.M2 to Subsystem_B.M3
        # M2 is at index 1, M3 is at index 2
        self.edge = [Buffer(env, id=f"edge[{i}]") for i in range(1)]
        self.add_child_edge(self.edge)
        
        self.edge[0].connect(self.Subsystem_A.M[1], self.Subsystem_B.M[2])

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