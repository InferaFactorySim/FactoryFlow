"""
ModelDescription:
A source splits an incoming flow into 3 parallel machines and all three machines ends in a common sink. 

 MODEL ASSUMPTIONS:
1. Inferred node names: 'Source' for the source with delay 3.3, 'M' for the list of 3 machines, and 'sink' for the sink.
2. Used 'Buffer' type for all edges with capacity =5. 
3. Used a single buffer for each connection between the Source and each Machine, and between each Machine and the Sink.
4. Used default values for all unspecified parameters (inter-arrival time, processing delays, buffer capacities).
5. Assumed the Source connects directly to each of the 3 machines via separate buffers to split the flow.
6. Assumed each of the 3 machines connects directly to the Sink via separate buffers to merge the flow.
7. MAchine ID and delays are (Machine_alpha,1), (Machine_beta,10), (Machine_gamma alpha,20),
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
        
        # initializing source with delay 3.3 (inter_arrival_time)
        self.source = Source(env, id="Source", inter_arrival_time=3.3)
        self.add_child_node(self.source)
        
        # initializing machines with specific IDs and delays
        machine_configs = [("Machine_alpha", 1), ("Machine_beta", 10), ("Machine_gamma alpha", 20)]
        self.M = [Machine(env, id=name, processing_delay=delay) for name, delay in machine_configs]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating edges (buffers) with capacity 5
        # 3 edges for Source -> Machines, 3 edges for Machines -> Sink
        self.edges = [Buffer(env, id=f"edge[{i}]", capacity=5) for i in range(6)]
        self.add_child_edge(self.edges)
        
        # connecting nodes with edges
        for i in range(3):
            # Connect Source to each Machine
            self.edges[i].connect(self.source, self.M[i])
            # Connect each Machine to Sink
            self.edges[i+3].connect(self.M[i], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)