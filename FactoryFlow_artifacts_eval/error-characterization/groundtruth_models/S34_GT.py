"""
ModelDescription:
A series of 100 machine with ID= M[i], i=0,.. and buffer IDs are B[i] i=0,..
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
        self.source = Source(env, id="Source")
        self.add_child_node(self.source)
        
        # Initializing Machines M[0] to M[99]
        self.machines = [Machine(env, id=f"M[{i}]") for i in range(100)]
        self.add_child_node(self.machines)
        
        # Initializing Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Creating edge from Source to first machine
        self.source_edge = Buffer(env, id="source_edge")
        self.add_child_edge(self.source_edge)
        
        # Creating buffers B[i] between machines
        self.buffers = [Buffer(env, id=f"B[{i}]") for i in range(99)]
        self.add_child_edge(self.buffers)
        
        # Creating edge from last machine to Sink
        self.sink_edge = Buffer(env, id="sink_edge")
        self.add_child_edge(self.sink_edge)
        
        # Connecting Source to M[0]
        self.source_edge.connect(self.source, self.machines[0])
        
        # Connecting machines in series via buffers B[i]
        for i in range(99):
            self.buffers[i].connect(self.machines[i], self.machines[i+1])
            
        # Connecting M[99] to Sink
        self.sink_edge.connect(self.machines[99], self.sink)

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