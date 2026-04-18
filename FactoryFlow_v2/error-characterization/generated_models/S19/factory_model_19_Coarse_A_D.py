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
7. MAchine ID and delays are (Machine_alpha,1), (Machine_beta,10), (Machine_gamma,20),
8. The identifier `i` in the buffer naming conventions (`B_src_i`, `B_sink_i`) is assumed to be replaced by the specific machine name suffixes: 1,2,3
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

        # Initializing Source with delay 3.3
        self.source = Source(env, id="Source", inter_arrival_time=3.3)
        self.add_child_node(self.source)

        # Initializing Machines with specific IDs and delays
        machine_data = [("Machine_alpha", 1), ("Machine_beta", 10), ("Machine_gamma", 20)]
        self.M = []
        for m_id, delay in machine_data:
            self.M.append(Machine(env, id=m_id, processing_delay=delay))
        self.add_child_node(self.M)

        # Initializing Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # Creating buffers from Source to Machines
        self.src_edges = [Buffer(env, id=f"B_src_{i+1}", capacity=5) for i in range(3)]
        self.add_child_edge(self.src_edges)

        # Creating buffers from Machines to Sink
        self.sink_edges = [Buffer(env, id=f"B_sink_{i+1}", capacity=5) for i in range(3)]
        self.add_child_edge(self.sink_edges)

        # Connecting Source to Machines
        for i in range(3):
            self.src_edges[i].connect(self.source, self.M[i])

        # Connecting Machines to Sink
        for i in range(3):
            self.sink_edges[i].connect(self.M[i], self.sink)

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