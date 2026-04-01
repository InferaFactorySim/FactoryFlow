"""
ModelDescription:
System has a single machine(ID=MACHINE) with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to Machine via a Buffer(ID=BUFFER1) and MACHINE to
 SINK via a Buffer(ID=BUFFER2).. Buffer has capacity of 3. MACHINE has a work_capacity is 2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed the Sink node has ID "sink".
3. Assumed the specified buffer capacity of 3 applies to both BUFFER1 and BUFFER2.
4. Used default values for all missing parameters for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.src)

        # initializing machine
        self.machine = Machine(env, id="MACHINE", processing_delay=2, work_capacity=2)
        self.add_child_node(self.machine)

        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # initializing buffers
        self.edge = []
        
        # BUFFER1 connecting SRC to MACHINE
        self.edge.append(Buffer(env, id="BUFFER1", capacity=3))
        
        # BUFFER2 connecting MACHINE to SINK
        self.edge.append(Buffer(env, id="BUFFER2", capacity=3))
        
        # adding edges to child edges
        self.add_child_edge(self.edge)

        # connecting nodes with edges
        self.edge[0].connect(self.src, self.machine)
        self.edge[1].connect(self.machine, self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation for 25 time units
TOP.run_simulation(25)