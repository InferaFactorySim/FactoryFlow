"""
ModelDescription:
The flow from a machine splits into 5 sinks.

 MODEL ASSUMPTIONS:
1. A Source node named 'src' is added to the system to generate flow into the machine.
2. The machine is named 'M' and the 5 sinks are named 'sink[0]' through 'sink[4]'.
3. All connections between nodes use the 'Buffer' edge type.
4. A single buffer is used for every connection between nodes.
5. The Machine 'M' is connected to each of the 5 sinks via separate buffers to represent the split.
6. Default values are used for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
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

        # Creating source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)

        # Creating machine M
        self.M = Machine(env, id="M")
        self.add_child_node(self.M)

        # Creating 5 sinks
        self.sinks = [Sink(env, id=f"sink[{i}]") for i in range(5)]
        self.add_child_node(self.sinks)

        # Creating edge from source to machine
        self.edge_src = Buffer(env, id="edge[0]")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.source, self.M)

        # Creating edges from machine to sinks
        self.edges_sink = [Buffer(env, id=f"edge[{i+1}]") for i in range(5)]
        self.add_child_edge(self.edges_sink)

        # Connecting machine to sinks
        for i in range(5):
            self.edges_sink[i].connect(self.M, self.sinks[i])

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