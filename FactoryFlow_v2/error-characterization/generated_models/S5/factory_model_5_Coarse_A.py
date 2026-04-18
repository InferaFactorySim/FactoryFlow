"""
ModelDescription:
A sequence of 5 machines

 MODEL ASSUMPTIONS:
1. A Source node is added to the start of the sequence to generate entities, and a Sink node is added to the end to collect them.
2. The 5 machines are connected in a linear series topology (SRC(1.2) →B1 M1 →B2 ... → M5 ->B6→ SINK).
3. Single Buffer edges are used to connect all adjacent nodes (Source to Machine, Machine to Machine, and Machine to Sink).
4. Node IDs are inferred as 'SRC' for the Source, 'SINK' for the Sink, and 'M1' through 'M5' for the machines. Edge IDs are B1, B2, B3,..
5. Default values are used for all unspecified parameters, including source inter-arrival times, machine processing delays, and buffer capacities.
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
        
        # initializing source with inter_arrival_time 1.2 as per assumption SRC(1.2)
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # initializing 5 machines with IDs M1 to M5
        self.machines = [Machine(env, id=f"M{i+1}") for i in range(5)]
        self.add_child_node(self.machines)
        
        # initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # initializing buffers with IDs B1 to B6
        # 5 machines in series + source + sink requires 6 buffers
        self.edges = [Buffer(env, id=f"B{i+1}") for i in range(6)]
        self.add_child_edge(self.edges)
        
        # connecting source to first machine (SRC -> B1 -> M1)
        self.edges[0].connect(self.source, self.machines[0])
        
        # connecting machines in series (M1 -> B2 -> M2 ... -> M5)
        for i in range(4):
            self.edges[i+1].connect(self.machines[i], self.machines[i+1])
            
        # connecting last machine to sink (M5 -> B6 -> SINK)
        self.edges[5].connect(self.machines[4], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating the model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)