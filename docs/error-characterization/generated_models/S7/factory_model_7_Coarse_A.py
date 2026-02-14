"""
ModelDescription:
A sequence of 5 heterogeneous machines

 MODEL ASSUMPTIONS:
1. Added a Source node at the beginning and a Sink node at the end of the sequence to form a complete flow.
2. Used the `Machine` node type for the 5 heterogeneous machines.
3. Used the `Buffer` edge type for all connections between nodes. Buffer IDs are B1, B2, B3, B4, etc.
4. Connected the nodes in a linear series (Source → Machine 0 → ... → Machine 4 → Sink) with a single buffer between each adjacent pair.
5. Inferred node IDs: 'src' for the Source, 'sink' for the Sink, and 'M1' through 'M5' for the machines.
6. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.source = Source(env, id="src", inter_arrival_time=1.0)
        self.add_child_node(self.source)
        
        # initializing machines
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=0.0) for i in range(5)]
        self.add_child_node(self.machines)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing buffers
        self.edges = [Buffer(env, id=f"B{i+1}") for i in range(6)]
        self.add_child_edge(self.edges)
        
        # connecting nodes with edges
        # src to first machine
        self.edges[0].connect(self.source, self.machines[0])
        
        # machines in between
        for i in range(4):
            self.edges[i+1].connect(self.machines[i], self.machines[i+1])
            
        # last machine to sink
        self.edges[5].connect(self.machines[4], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model

from factorysimpy.utils import utils
fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="factory_model_7_Coarse_A", directory=".", format="png", cleanup=True)
TOP.validate()
# running the simulation
TOP.run_simulation(25)