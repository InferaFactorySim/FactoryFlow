"""
ModelDescription:
A system with two machines in a loop. The system has a source and a sink.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description (Source, Sink, Machine). Specific IDs assumed are 'src', 'sink', 'M1', and 'M2'.
2. Assumed the topology consists of Source connecting to M1, M1 connecting to M2, M2 connecting to Sink, and M2 connecting back to M1 to form the loop.
3. Used Buffer for all edges as it is the supported edge type.
4. Used a single buffer for each connection between nodes.
5. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
6. Assumed default routing logic (uniform probability) for the flow split at M2 (sending parts to Sink or back to M1).
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class LoopSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing machines M1 and M2
        self.M = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing buffers
        # We need 4 edges: src->M1, M1->M2, M2->sink, M2->M1
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(4)]
        self.add_child_edge(self.edges)
        
        # Connecting nodes
        # src to M1
        self.edges[0].connect(self.source, self.M[0])
        # M1 to M2
        self.edges[1].connect(self.M[0], self.M[1])
        # M2 to Sink
        self.edges[2].connect(self.M[1], self.sink)
        # M2 to M1 (Loop)
        self.edges[3].connect(self.M[1], self.M[0])

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = LoopSystem(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)