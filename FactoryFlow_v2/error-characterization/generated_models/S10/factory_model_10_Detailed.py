"""
ModelDescription:
Source_1 (arrival rate 5.0s) feeds Machine_M1 via Buffer with ID- buffer_main. M1 acts as a router with a split ratio of 0.5 to Path A and 0.5 to Path B. Path A consists of Buffer with ID-Buffer_A_1 feeding Machine_M2 and Buffer with ID-Buffer_A_sink to Sink_1. Path B consists of Buffer with ID- Buffer_B_1 feeding Machine_M3 to Buffer with ID- Buffer_B_sink to Sink_2. M2 and M3 both connect to individual Sinks, Sink_1 and Sink_2 via Buffer with ID- Buffer_A_sink and Buffer with ID- Buffer_B_sink respectively. The out_edge_selection of Machine_M1 is "ROUND_ROBIN".All machines have a processing_Delay of 2 and buffers have a capacity of 2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed "arrival rate 5.0s" corresponds to an inter_arrival_time of 5.0 for Source_1.
3. Assumed Machine_M1 connects to Buffer_A_1 and Buffer_B_1 to route entities to Path A and Path B respectively.
4. Assumed the specified "ROUND_ROBIN" out_edge_selection strategy is used to achieve the 0.5 split ratio.
5. Used a single buffer for each connection as implied by the specific buffer IDs provided.
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
        
        # Initializing Source
        self.source = Source(env, id="Source_1", inter_arrival_time=5.0)
        self.add_child_node(self.source)
        
        # Initializing Router Machine M1
        self.m1 = Machine(env, id="Machine_M1", processing_delay=2, out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.m1)
        
        # Connecting Source to M1
        self.buffer_main = Buffer(env, id="buffer_main", capacity=2)
        self.add_child_edge(self.buffer_main)
        self.buffer_main.connect(self.source, self.m1)
        
        # Defining Paths A and B
        paths = ['A', 'B']
        self.path_machines = []
        self.path_sinks = []
        
        # Creating components for Path A and Path B using a loop
        for i, p in enumerate(paths):
            # Create Machine (M2 for A, M3 for B)
            m = Machine(env, id=f"Machine_M{i+2}", processing_delay=2)
            self.path_machines.append(m)
            
            # Create Sink (Sink_1 for A, Sink_2 for B)
            s = Sink(env, id=f"Sink_{i+1}")
            self.path_sinks.append(s)
            
            # Add nodes to children
            self.add_child_node(m)
            self.add_child_node(s)
            
            # Create Buffer from M1 to Machine (Buffer_A_1 / Buffer_B_1)
            b_start = Buffer(env, id=f"Buffer_{p}_1", capacity=2)
            self.add_child_edge(b_start)
            b_start.connect(self.m1, m)
            
            # Create Buffer from Machine to Sink (Buffer_A_sink / Buffer_B_sink)
            b_end = Buffer(env, id=f"Buffer_{p}_sink", capacity=2)
            self.add_child_edge(b_end)
            b_end.connect(m, s)

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