"""
ModelDescription:
A series of 100 machine with ID= M[i], i=0,1,2... and buffer IDs are B[i] i=0,1,2...

 MODEL ASSUMPTIONS:
1. Added a Source node (ID "Source") and a Sink node (ID "Sink") to complete the system flow, as they were not specified in the description.
2. Inferred a linear topology where Source connects to M[0], M[i] connects to M[i+1], and M[99] connects to Sink.
3. Assumed buffers B[i] are used for all connections, mapping sequentially from the start to the end of the line (e.g., B[0] connects Source to M[0], B[1] connects M[0] to M[1], etc.).
4. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
5. Node names and Types are chosen according to users description.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the model
class SystemModel(Node):
    def __init__(self, env, id, n=100):
        super().__init__(env, id)
        
        # initializing source
        self.source = Source(env, id="Source")
        self.add_child_node(self.source)
        
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # initializing buffers
        # We need n+1 buffers to connect Source -> M[0] -> ... -> M[n-1] -> Sink
        self.B = [Buffer(env, id=f"B[{i}]") for i in range(n+1)]
        self.add_child_edge(self.B)
        
        # connecting nodes with edges
        
        # Source to first machine using B[0]
        self.B[0].connect(self.source, self.M[0])
        
        # Machines in between
        for i in range(n-1):
            self.B[i+1].connect(self.M[i], self.M[i+1])
            
        # Last machine to sink using B[n]
        self.B[n].connect(self.M[n-1], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating linear model with 100 machines
TOP = SystemModel(env, "TOP", n=100)
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)