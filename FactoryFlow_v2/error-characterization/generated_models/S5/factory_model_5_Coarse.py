"""
ModelDescription:
A sequence of 5 machines

 MODEL ASSUMPTIONS:
1. A Source node is added to the start of the sequence to generate entities, and a Sink node is added to the end to collect them.
2. The 5 machines are connected in a linear series topology (Source → Machine 1 → ... → Machine 5 → Sink).
3. Single Buffer edges are used to connect all adjacent nodes (Source to Machine, Machine to Machine, and Machine to Sink).
4. Node IDs are inferred as 'src' for the Source, 'sink' for the Sink, and 'M[0]' through 'M[4]' for the machines.
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
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing buffers
        # We need n+1 buffers: src->M0, M0->M1...M3->M4, M4->sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(n+1)]
        self.add_child_edge(self.edges)
        
        # connecting nodes with edges
        # src to first machine
        self.edges[0].connect(self.src, self.M[0])
        
        # machines in between
        for i in range(n-1):
            self.edges[i+1].connect(self.M[i], self.M[i+1])
            
        # last machine to sink
        self.edges[n].connect(self.M[n-1], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating linear model with 5 machines
TOP = SystemModel(env, "TOP", n=5)
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)