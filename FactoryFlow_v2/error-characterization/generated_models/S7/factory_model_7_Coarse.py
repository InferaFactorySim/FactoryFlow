"""
ModelDescription:
A sequence of 5 heterogeneous machines

 MODEL ASSUMPTIONS:
1. Added a Source node at the beginning and a Sink node at the end of the sequence to form a complete flow.
2. Used the `Machine` node type for the 5 heterogeneous machines.
3. Used the `Buffer` edge type for all connections between nodes.
4. Connected the nodes in a linear series (Source → Machine 0 → ... → Machine 4 → Sink) with a single buffer between each adjacent pair.
5. Inferred node IDs: 'src' for the Source, 'sink' for the Sink, and 'M[0]' through 'M[4]' for the machines.
6. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
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
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
       
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
       
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # creating edges
        # initializing buffers
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(n+1)]
        self.add_child_edge(self.edges)
    
        # connecting nodes with edges
        # src to first machine
        self.edges[0].connect(self.source, self.M[0])
        # machines in between
        for i in range(n-1):
            self.edges[i+1].connect(self.M[i], self.M[i+1])
        # last machine to sink
        self.edges[n].connect(self.M[n-1], self.sink)

# initiliating simpy environment
env = simpy.Environment()
# creating linear model with 5 machines
TOP = SystemModel(env, "TOP", n=5) 
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id() 
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)