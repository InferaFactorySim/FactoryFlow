"""
ModelDescription:
A system with two machines with delay 1.4 connected parallely

 MODEL ASSUMPTIONS:
1. A Source node with delay 1.2 ('src') is added to generate entities and a Sink node ('sink') is added to collect processed entities, as they are required for a complete simulation flow but not mentioned in the description.
2. The "parallel" connection is implemented by connecting the Source to both machines, and connecting both machines to the Sink.
3. Inferred node IDs: 'SRC' for the Source, 'Sink' for the Sink, and 'M1' and 'M2' for the two machines.
4. 'Buffer' edges with capacity=2 are used for all connections between nodes as the default edge type.Buffer IDs are B1, B2, B3,B4
5. Used a single buffer for each connection between nodes (Source to Machines, Machines to Sink).
6. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
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
        
        # Source
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Machines
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=1.4) for i in range(2)]
        self.add_child_node(self.machines)
        
        # Buffers
        self.edges = []
        for i in range(2):
            # Input buffer (B1, B2) connecting Source to Machines
            b_in = Buffer(env, id=f"B{i+1}", capacity=2)
            self.add_child_edge(b_in)
            b_in.connect(self.source, self.machines[i])
            self.edges.append(b_in)
            
            # Output buffer (B3, B4) connecting Machines to Sink
            b_out = Buffer(env, id=f"B{i+3}", capacity=2)
            self.add_child_edge(b_out)
            b_out.connect(self.machines[i], self.sink)
            self.edges.append(b_out)

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)