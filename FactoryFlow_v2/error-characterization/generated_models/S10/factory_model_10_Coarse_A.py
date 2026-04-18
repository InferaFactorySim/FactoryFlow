"""
ModelDescription:
A system with a machine feeding finished parts equally to two other machines. Path A consists of Buffer with ID-Buffer_A_1 feeding Machine_M2 and Buffer with ID-Buffer_A_sink to Sink_1. Path B consists of Buffer with ID- Buffer_B_1 feeding Machine_M3 to Buffer with ID- Buffer_B_sink to Sink_2. M2 and M3 both connect to individual Sinks, Sink_1 and Sink_2 via Buffer with ID- Buffer_A_sink and Buffer with ID- Buffer_B_sink respectively. 

 MODEL ASSUMPTIONS:
3. Used 'Buffer' for all connections, assuming a single buffer between the Source and Machine_M1, between Machine_M1 and each parallel machine, and between each parallel machine and the Sink.
4. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
5. Assumed the 'Machine_M1' machine handles the routing logic to split the flow equally between the two downstream machines.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating nodes
        
        # initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # initializing machines
        # Machine_M1 splits flow, M2 and M3 are parallel
        self.m1 = Machine(env, id="Machine_M1")
        self.m2 = Machine(env, id="Machine_M2")
        self.m3 = Machine(env, id="Machine_M3")
        self.add_child_node([self.m1, self.m2, self.m3])
        
        # initializing sinks
        self.sink1 = Sink(env, id="Sink_1")
        self.sink2 = Sink(env, id="Sink_2")
        self.sinks = [self.sink1, self.sink2]
        self.add_child_node(self.sinks)
        
        # creating edges
        
        # Buffer between Source and Machine_M1 (Assumption 3)
        self.edge_src = Buffer(env, id="edge[0]")
        
        # Path A Buffers
        self.buffer_a_1 = Buffer(env, id="Buffer_A_1")
        self.buffer_a_sink = Buffer(env, id="Buffer_A_sink")
        
        # Path B Buffers
        self.buffer_b_1 = Buffer(env, id="Buffer_B_1")
        self.buffer_b_sink = Buffer(env, id="Buffer_B_sink")
        
        # adding edges to child edges
        self.add_child_edge([self.edge_src, self.buffer_a_1, self.buffer_a_sink, self.buffer_b_1, self.buffer_b_sink])
        
        # connecting nodes with edges
        
        # Source to Machine_M1
        self.edge_src.connect(self.source, self.m1)
        
        # Path A: M1 -> Buffer_A_1 -> M2 -> Buffer_A_sink -> Sink_1
        self.buffer_a_1.connect(self.m1, self.m2)
        self.buffer_a_sink.connect(self.m2, self.sink1)
        
        # Path B: M1 -> Buffer_B_1 -> M3 -> Buffer_B_sink -> Sink_2
        self.buffer_b_1.connect(self.m1, self.m3)
        self.buffer_b_sink.connect(self.m3, self.sink2)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)