"""
ModelDescription:
A system with two machines.

 MODEL ASSUMPTIONS:
1. Assumed the two machines are connected in a linear series sequence.
2. Added a Source node ('src') to the beginning and a Sink node ('sink') to the end of the system to enable flow.
3. Inferred Machine IDs as 'M[0]' and 'M[1]'.
4. Used a single Buffer to connect the Source to the first machine, the first machine to the second, and the second machine to the Sink.
5. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
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
        n = 2  # Number of machines based on description

        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=1.0)
        self.add_child_node(self.src)
       
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=0.0) for i in range(n)]
        self.add_child_node(self.M)
       
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # creating edges
        # initializing buffers: src->M[0], M[0]->M[1], M[1]->sink requires n+1 buffers
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
# creating system model
TOP = SystemModel(env, "TOP") 
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id() 
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)