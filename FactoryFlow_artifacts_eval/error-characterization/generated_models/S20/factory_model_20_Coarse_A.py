"""
ModelDescription:
The flow from a machine splits into 5 sinks.

 MODEL ASSUMPTIONS:
1. A Source node named 'Source' (delay=4.32)is added to the system to generate flow into the machine.
2. The machine is named 'Machine_Hub' (delay=2)and the 5 sinks are named 'Sink_North', Sink_West' through 'Sink_Central'.
3. All connections between nodes use the 'Buffer' edge type.
4. A single buffer(cap=5) is used for every connection between nodes. Buffer ID s are  B_src_hub, B_sink_North, B_sink_West, etc.
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
        
        # Assumption 1: Source node named 'Source' (delay=4.32)
        self.source = Source(env, id="Source", inter_arrival_time=4.32)
        self.add_child_node(self.source)
        
        # Assumption 2: Machine named 'Machine_Hub' (delay=2)
        self.M = Machine(env, id="Machine_Hub", processing_delay=2)
        self.add_child_node(self.M)
        
        # Assumption 2 & 5: 5 sinks named 'Sink_North', 'Sink_West' through 'Sink_Central'
        # Inferring names based on cardinal directions + central to make 5, ending with Central
        sink_suffixes = ["North", "West", "South", "East", "Central"]
        self.sinks = [Sink(env, id=f"Sink_{suffix}") for suffix in sink_suffixes]
        self.add_child_node(self.sinks)
        
        # Assumption 4: Buffer IDs are B_src_hub, B_sink_North, etc.
        # Assumption 4: Capacity = 5 for all buffers
        
        # Buffer from Source to Machine
        self.b_src = Buffer(env, id="B_src_hub", capacity=5)
        self.add_child_edge(self.b_src)
        
        # Buffers from Machine to Sinks
        self.b_sinks = [Buffer(env, id=f"B_sink_{suffix}", capacity=5) for suffix in sink_suffixes]
        self.add_child_edge(self.b_sinks)
        
        # Connecting Source to Machine
        self.b_src.connect(self.source, self.M)
        
        # Connecting Machine to each Sink
        for i in range(len(sink_suffixes)):
            self.b_sinks[i].connect(self.M, self.sinks[i])

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