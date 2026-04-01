"""
ModelDescription:
A series of 100 machines 

 MODEL ASSUMPTIONS:
1. Added a Source node named 'src' at the start and a Sink node named 'sink' at the end of the series to complete the simulation flow.
2. Inferred machine IDs as 'M[0]' through 'M[99]'.
3. Used 'Buffer' edges for all connections, assuming a single buffer connects the Source to the first machine, each machine to the next, and the last machine to the Sink.
4. Inferred a linear flow direction from Source to Machine 0, sequentially through to Machine 99, and finally to the Sink.
5. Used default values for all unspecified parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id, n=100):
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
        # We need n+1 buffers: 1 from source, n-1 between machines, 1 to sink
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        self.add_child_edge(self.e)
        
        # connecting nodes with edges
        # src to first machine
        self.e[0].connect(self.src, self.M[0])
        
        # machines in between
        for i in range(n-1):
            self.e[i+1].connect(self.M[i], self.M[i+1])
            
        # last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating linear model with 100 machines
TOP = SystemModel(env, "TOP", n=100)
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)