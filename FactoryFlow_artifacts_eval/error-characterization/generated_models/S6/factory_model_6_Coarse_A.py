"""
ModelDescription:
A system with 5 machines connected in parallel 

 MODEL ASSUMPTIONS:
1. Added a Source node named 'SRC' and a Sink node named 'SINK' to the system to facilitate the flow of parts through the parallel machines.
2. Inferred machine names as 'M1' through 'M5'.
3. Assumed the topology consists of the Source connecting to each of the 5 machines, and each of the 5 machines connecting to the Sink.
4. Used 'Buffer' for all connections, with a single buffer placed between any two connected nodes. Let Buffer IDs be B_SRC_1, B_1_SINK, B_SRC_2, B_2_SINK, AND SO ON
5. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.


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
        
        # Initialize Source
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)
        
        # Initialize Machines M1 to M5
        self.machines = [Machine(env, id=f"M{i+1}") for i in range(5)]
        self.add_child_node(self.machines)
        
        # Initialize Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Initialize Buffers
        # We need 5 buffers from Source to Machines and 5 buffers from Machines to Sink
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(10)]
        self.add_child_edge(self.edges)
        
        # Connect Source to each Machine
        for i in range(5):
            self.edges[i].connect(self.source, self.machines[i])
            
        # Connect each Machine to Sink
        for i in range(5):
            self.edges[5 + i].connect(self.machines[i], self.sink)

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)