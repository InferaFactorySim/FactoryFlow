"""
GENERATED MODEL ASSUMPTIONS:
1. Added a Source node named "src" and a Sink node named "sink" to the system to facilitate entity flow.
2. Named the single machine "M".
3. Connected the Source to the Machine and the Machine to the Sink using a single Buffer for each connection.
4. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
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
        
        # Creating nodes
        # Initializing source with default inter-arrival time
        self.src = Source(env, id="src", inter_arrival_time=1.0)
        self.add_child_node(self.src)
        
        # Initializing the single machine "M" with default processing delay
        self.M = Machine(env, id="M", processing_delay=0.0)
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        # We need 2 buffers: src->M and M->sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(2)]
        self.add_child_edge(self.edges)
        
        # Connecting nodes with edges
        # Connect Source to Machine
        self.edges[0].connect(self.src, self.M)
        # Connect Machine to Sink
        self.edges[1].connect(self.M, self.sink)

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