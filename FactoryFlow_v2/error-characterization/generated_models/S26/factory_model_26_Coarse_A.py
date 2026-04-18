"""
ModelDescription:
Two subsystems where a machine inside Subsystem A connects directly to a specific machine deep inside Subsystem B.

 MODEL ASSUMPTIONS:
1. Inferred a top-level system containing two subsystems named `SubsystemA` and `SubsystemB`.
2. Assumed `SubsystemA` contains a linear sequence of 3 machines and `SubsystemB` contains a linear sequence of 3 machines to provide a structure where a "deep" connection is possible.
3. Added a `src`  and 'sink' node in `SubsystemA` and `SubsystemB`  to ensure a valid simulation flow.
4. Interpreted the connection "deep inside Subsystem B" as a `Buffer` connecting the second machine of `SubsystemA` to the 3rd machine (index 2) of `SubsystemB`.
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

# Defining the top-level system containing two subsystems
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # Creating SubsystemA and SubsystemB
        # Assumption 1 & 2: SubsystemA and SubsystemB are linear sequences of 3 machines
        self.SubsystemA = LinearSubsystem(env, id="SubsystemA", n=3)
        self.SubsystemB = LinearSubsystem(env, id="SubsystemB", n=3)
        
        # Adding subsystems as child nodes
        self.add_child_node([self.SubsystemA, self.SubsystemB])

        # Creating the deep connection edge
        # Assumption 4: Buffer connecting the second machine of SubsystemA (index 1) 
        # to the 3rd machine (index 2) of SubsystemB.
        self.edge = [Buffer(env, id="edge[0]")]
        self.add_child_edge(self.edge)

        # Connecting the specific machines
        self.edge[0].connect(self.SubsystemA.M[1], self.SubsystemB.M[2])

# Defining the linear subsystem model
class LinearSubsystem(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        # Assumption 3: Added a src and sink node in SubsystemA and SubsystemB
        self.src = Source(env, id="src")
        self.add_child_node(self.src)

        # Creating machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)

        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # Creating edges (buffers)
        # Assumption 5: Machines within each subsystem are connected in a standard linear series
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        self.add_child_edge(self.e)

        # Connecting source to first machine
        self.e[0].connect(self.src, self.M[0])

        # Connecting machines in series
        for i in range(n-1):
            self.e[i+1].connect(self.M[i], self.M[i+1])

        # Connecting last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)

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