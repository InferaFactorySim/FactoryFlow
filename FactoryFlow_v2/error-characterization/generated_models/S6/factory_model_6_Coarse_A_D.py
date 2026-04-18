"""
ModelDescription:
A system with 5 machines with delay 1.1 connected in parallel 

 MODEL ASSUMPTIONS:
1. Added a Source node named 'SRC' with delay 0.2 and a Sink node named 'SINK' to the system to facilitate the flow of parts through the parallel machines.
2. Inferred machine names as 'M1' through 'M5'.
3. Assumed the topology consists of the Source connecting to each of the 5 machines, and each of the 5 machines connecting to the Sink.
4. Used 'Buffer'  for all connections, with a single buffer with capacity 2 placed between any two connected nodes. Buffer IDs are like B_SRC_1, B_1_SINK, B_SRC_2, B_2_SINK, and so on
5. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
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
        
        # Creating Source
        self.src = Source(env, id="SRC", inter_arrival_time=0.2)
        self.add_child_node(self.src)
        
        # Creating Machines
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.1) for i in range(5)]
        self.add_child_node(self.machines)
        
        # Creating Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Creating and connecting buffers
        self.src_buffers = []
        self.sink_buffers = []
        
        for i in range(5):
            # Buffer from Source to Machine
            b_src = Buffer(env, id=f"B_SRC_{i+1}", capacity=2)
            self.src_buffers.append(b_src)
            self.add_child_edge(b_src)
            b_src.connect(self.src, self.machines[i])
            
            # Buffer from Machine to Sink
            b_sink = Buffer(env, id=f"B_{i+1}_SINK", capacity=2)
            self.sink_buffers.append(b_sink)
            self.add_child_edge(b_sink)
            b_sink.connect(self.machines[i], self.sink)

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