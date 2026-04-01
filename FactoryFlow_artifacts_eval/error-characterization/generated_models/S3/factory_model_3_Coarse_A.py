"""
ModelDescription:
A system with two machines connected parallely

 MODEL ASSUMPTIONS:
1. A Source node ('src') is added to generate entities and a Sink node ('sink') is added to collect processed entities, as they are required for a complete simulation flow but not mentioned in the description.
2. The "parallel" connection is implemented by connecting the Source to both machines, and connecting both machines to the Sink.
3. Inferred node IDs: 'SRC' for the Source, 'Sink' for the Sink, and 'M1' and 'M2' for the two machines.
4. 'Buffer' edges are used for all connections between nodes as the default edge type.Buffer IDs are B1, B2, B3,B4
5. Used a single buffer for each connection between nodes (Source to Machines, Machines to Sink).
6. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
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

        # Initializing Source
        self.source = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.source)

        # Initializing Machines
        self.machines = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.machines)

        # Initializing Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)

        # Initializing Buffers with IDs B1, B2, B3, B4
        self.edges = [Buffer(env, id=f"B{i+1}") for i in range(4)]
        self.add_child_edge(self.edges)

        # Connecting Source to Machines
        for i in range(2):
            self.edges[i].connect(self.source, self.machines[i])

        # Connecting Machines to Sink
        for i in range(2):
            self.edges[2+i].connect(self.machines[i], self.sink)

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