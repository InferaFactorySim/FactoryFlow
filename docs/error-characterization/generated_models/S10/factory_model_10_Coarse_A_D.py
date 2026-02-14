"""
ModelDescription:
A system with a machine feeding finished parts equally to two other machines. Path A consists of Buffer with ID-Buffer_A_1 feeding Machine_M2 and Buffer with ID-Buffer_A_sink to Sink_1. Path B consists of Buffer with ID- Buffer_B_1 feeding Machine_M3 to Buffer with ID- Buffer_B_sink to Sink_2. M2 and M3 both connect to individual Sinks, Sink_1 and Sink_2 via Buffer with ID- Buffer_A_sink and Buffer with ID- Buffer_B_sink respectively. The out_edge_selection of Machine_M1 is "ROUND_ROBIN".All machines have a processing_Delay of 2 and buffers have a capacity of 2

 MODEL ASSUMPTIONS:
3. Used 'Buffer' for all connections, assuming a single buffer between the Source and Machine_M1, between Machine_M1 and each parallel machine, and between each parallel machine and the Sink.
4. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
5. Assumed the 'Machine_M1' machine handles the routing logic to split the flow equally between the two downstream machines.
6.Source with ID-SRC has delay of 5.
ID of buffer after SRC is buffer_main
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
        self.source = Source(env, id="SRC", inter_arrival_time=5)
        self.add_child_node(self.source)
        
        # Initializing machines
        # M1 splits flow to M2 and M3
        self.M1 = Machine(env, id="Machine_M1", processing_delay=2, out_edge_selection="ROUND_ROBIN")
        self.M2 = Machine(env, id="Machine_M2", processing_delay=2)
        self.M3 = Machine(env, id="Machine_M3", processing_delay=2)
        self.machines = [self.M1, self.M2, self.M3]
        self.add_child_node(self.machines)
        
        # Initializing sinks
        self.sink1 = Sink(env, id="Sink_1")
        self.sink2 = Sink(env, id="Sink_2")
        self.sinks = [self.sink1, self.sink2]
        self.add_child_node(self.sinks)
        
        # Initializing buffers with specific IDs from description
        self.buffer_main = Buffer(env, id="buffer_main", capacity=2)
        self.buffer_A_1 = Buffer(env, id="Buffer_A_1", capacity=2)
        self.buffer_B_1 = Buffer(env, id="Buffer_B_1", capacity=2)
        self.buffer_A_sink = Buffer(env, id="Buffer_A_sink", capacity=2)
        self.buffer_B_sink = Buffer(env, id="Buffer_B_sink", capacity=2)
        
        self.edges = [self.buffer_main, self.buffer_A_1, self.buffer_B_1, self.buffer_A_sink, self.buffer_B_sink]
        self.add_child_edge(self.edges)
        
        # Connecting nodes
        # Source -> M1
        self.buffer_main.connect(self.source, self.M1)
        
        # Path A: M1 -> M2 -> Sink_1
        self.buffer_A_1.connect(self.M1, self.M2)
        self.buffer_A_sink.connect(self.M2, self.sink1)
        
        # Path B: M1 -> M3 -> Sink_2
        self.buffer_B_1.connect(self.M1, self.M3)
        self.buffer_B_sink.connect(self.M3, self.sink2)

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