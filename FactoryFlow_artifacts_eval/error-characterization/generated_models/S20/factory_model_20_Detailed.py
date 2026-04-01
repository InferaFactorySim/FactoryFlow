"""
ModelDescription:
A source with ID Source(4.32) feeds central Machine_Hub (delay 2.0s) via Buffer with 
ID- B_src_hub. Machine_Hub is connected to 5 separate output Buffers (cap 5), each 
leading to a unique Sink named Sink_North, Sink_South, Sink_East, Sink_West, and Sink_Central.
 All buffers have a capacity of 5. Each machine has its own buffer from the source and to the sink.
 B_src_i connects Source to Machine_i, and B_sink_i connects Machine_hub to Sink_i.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed the IDs for the 5 output buffers are 'B_sink_North', 'B_sink_South', 'B_sink_East', 'B_sink_West', and 'B_sink_Central' based on the described naming pattern 'B_sink_i' and the specific sink names.
3. Assumed 'Machine_Hub' uses a default output edge selection strategy (e.g., Round Robin or Uniform Random) to distribute entities among the 5 connected output buffers.
4. Used default values for all other missing parameters for all components.
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
        
        # Define directions based on description
        directions = ["North", "South", "East", "West", "Central"]
        
        # Initializing Source with inter_arrival_time 4.32
        self.source = Source(env, id="Source", inter_arrival_time=4.32)
        self.add_child_node(self.source)
        
        # Initializing Central Machine Hub with processing_delay 2.0s
        self.machine_hub = Machine(env, id="Machine_Hub", processing_delay=2.0)
        self.add_child_node(self.machine_hub)
        
        # Initializing Sinks
        self.sinks = [Sink(env, id=f"Sink_{d}") for d in directions]
        self.add_child_node(self.sinks)
        
        # Initializing Input Buffer with capacity 5
        self.b_src_hub = Buffer(env, id="B_src_hub", capacity=5)
        self.add_child_edge(self.b_src_hub)
        
        # Initializing Output Buffers with capacity 5
        self.b_sinks = [Buffer(env, id=f"B_sink_{d}", capacity=5) for d in directions]
        self.add_child_edge(self.b_sinks)
        
        # Connecting Source to Machine Hub
        self.b_src_hub.connect(self.source, self.machine_hub)
        
        # Connecting Machine Hub to Sinks via Output Buffers
        for i in range(len(directions)):
            self.b_sinks[i].connect(self.machine_hub, self.sinks[i])

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