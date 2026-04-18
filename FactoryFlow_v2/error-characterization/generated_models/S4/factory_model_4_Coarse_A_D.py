"""
ModelDescription:
A system with two machines in a loop. The system has a source and a sink. Source has delay 0.3

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description (Source, Sink, Machine). Specific IDs assumed are 'SRC', 'Sink', 'M1', and 'M2'.
2. Assumed the topology consists of Source connecting to M1, M1 connecting to M2, M2 connecting to Sink, and M2 connecting back to M1 to form the loop. Machines has processing_delay of 2
3. Used Buffer for all edges as it is the supported edge type.
4. Used a single buffer with capacity=2 for each connection between nodes. Name buffers as B1, B2, B3, B4
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

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # Initializing machines M1, M2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Initializing buffers B1, B2, B3, B4
        self.buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.buffers)
        
        # Connecting nodes
        # B1: Source -> M1
        self.buffers[0].connect(self.src, self.machines[0])
        # B2: M1 -> M2
        self.buffers[1].connect(self.machines[0], self.machines[1])
        # B3: M2 -> Sink
        self.buffers[2].connect(self.machines[1], self.sink)
        # B4: M2 -> M1 (Loop)
        self.buffers[3].connect(self.machines[1], self.machines[0])

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