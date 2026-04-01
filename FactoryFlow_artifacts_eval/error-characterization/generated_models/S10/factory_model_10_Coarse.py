"""
ModelDescription:
A system with a machine feeding finished parts equally to two other machines

 MODEL ASSUMPTIONS:
1. Added a Source node to feed the first machine and a Sink node to collect parts from the two receiving machines to complete the flow.
2. Inferred node IDs: 'M_Feeder' for the first machine, and 'M_Parallel_1' and 'M_Parallel_2' for the two receiving machines.
3. Used 'Buffer' for all connections, assuming a single buffer between the Source and M_Feeder, between M_Feeder and each parallel machine, and between each parallel machine and the Sink.
4. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
5. Assumed the 'M_Feeder' machine handles the routing logic to split the flow equally between the two downstream machines.
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
        
        # Creating nodes
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing feeder machine
        self.feeder = Machine(env, id="M_Feeder")
        self.add_child_node(self.feeder)
        
        # Initializing parallel machines
        self.parallel_machines = [Machine(env, id=f"M_Parallel_{i+1}") for i in range(2)]
        self.add_child_node(self.parallel_machines)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        # 1 edge from Source to Feeder
        # 2 edges from Feeder to Parallel Machines
        # 2 edges from Parallel Machines to Sink
        # Total 5 edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(5)]
        self.add_child_edge(self.edges)
        
        # Connecting nodes with edges
        
        # Connect Source to Feeder
        self.edges[0].connect(self.source, self.feeder)
        
        # Connect Feeder to Parallel Machines and Parallel Machines to Sink
        for i in range(2):
            # Connect Feeder to Parallel Machine i
            # Edges 1 and 2 used here
            self.edges[1 + i].connect(self.feeder, self.parallel_machines[i])
            
            # Connect Parallel Machine i to Sink
            # Edges 3 and 4 used here
            self.edges[3 + i].connect(self.parallel_machines[i], self.sink)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system model
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation for 25 time units
TOP.run_simulation(25)