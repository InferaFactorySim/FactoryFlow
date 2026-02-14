"""
ModelDescription:

System has a single machine(ID=MACHINE) with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to Machine via a Buffer(ID=BUFFER1) and MACHINE to
 SINK via a Buffer(ID=BUFFER2).. Buffer has capacity of 3. MACHINE has a work_capacity is 2
 

 MODEL ASSUMPTIONS:
1. Added a Source node named "SRC" with inter_Arrival_time of 1.2 and a Sink node named "SINK" to the system to facilitate entity flow.
2. Named the single machine "MACHINE" with delay 2 and 
3. Connected the Source to the Machine and the Machine to the Sink using a single Buffer with capacity =2  for each connection. Name Buffer as "BUFFER1", "BUFFER2"
4. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
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

        # Initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.src)

        # Initializing machine
        self.machine = Machine(env, id="MACHINE", processing_delay=2, work_capacity=2)
        self.add_child_node(self.machine)

        # Initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Initializing buffers
        self.buffer1 = Buffer(env, id="BUFFER1", capacity=3)
        self.add_child_edge(self.buffer1)

        self.buffer2 = Buffer(env, id="BUFFER2", capacity=3)
        self.add_child_edge(self.buffer2)

        # Connecting nodes
        self.buffer1.connect(self.src, self.machine)
        self.buffer2.connect(self.machine, self.sink)

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