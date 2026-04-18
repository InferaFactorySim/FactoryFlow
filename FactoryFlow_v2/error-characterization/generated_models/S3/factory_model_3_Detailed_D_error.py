"""
ModelDescription:
System has two machines M1and M2 with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. SRC is connected to M1 and M1  to Sink via Buffers with IDs B1, B2. M2 is connected parallel to M1 using Buffer with IDs B3 and B4. All buffers have a capacity of 2. Source and sink are common. All machines have a processing_Delay of 1.4

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed the Sink node has ID "Sink".
3. Assumed a buffer connects `SRC` to `M1` and another buffer connects `SRC` to `M2` to facilitate the parallel connection, as these edges were not explicitly named.
4. Assumed Buffers `B1` and `B2` are connected in series between `M1` and `Sink` (M1 -> B1 -> B2 -> Sink).
5. Assumed Buffers `B3` and `B4` are connected in series between `M2` and `Sink` (M2 -> B3 -> B4 -> Sink).
6. Assumed processing delay is 1.4 for all machines, overriding the conflicting value of 2 mentioned initially for M1 and M2.
7. Assumed all inferred buffers have a capacity of 2, consistent with the description for all buffers.
8. Inferred a repeated pattern of a machine connected to the sink via two series buffers, and will create a class for this repeated structure.
"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..','..', '..','src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Class for the repeated structure: Machine -> Buffer -> Connector -> Buffer -> Sink
class Branch(Node):
    def __init__(self, env, id, machine_id, buffer_ids, sink_node):
        super().__init__(env, id)
        
        # Initializing machine
        self.m = Machine(env, id=machine_id, processing_delay=1.4)
        self.add_child_node(self.m)
        
        # Initializing connector machine (dummy node for series buffers)
        self.connector = Machine(env, id=f"{machine_id}_connector", processing_delay=0)
        self.add_child_node(self.connector)
        
        # Initializing buffers
        self.buffers = [Buffer(env, id=b_id, capacity=2) for b_id in buffer_ids]
        self.add_child_edge(self.buffers)
        
        # Connecting Machine to Connector via first buffer
        self.buffers[0].connect(self.m, self.connector)
        
        # Connecting Connector to Sink via second buffer
        self.buffers[1].connect(self.connector, sink_node)
        
        # Exposing entry point
        self.entry = self.m

# Defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.source)
        
        # Initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Creating branches for M1 and M2
        self.branches = []
        for i in range(2):
            m_id = f"M{i+1}"
            b_ids = [f"B{2*i+1}", f"B{2*i+2}"]
            branch = Branch(env, id=f"Branch[{i}]", machine_id=m_id, buffer_ids=b_ids, sink_node=self.sink)
            self.branches.append(branch)
        self.add_child_node(self.branches)
        
        # Creating edges from Source to Branches
        self.edges = [Buffer(env, id=f"edge[{i}]", capacity=2) for i in range(2)]
        self.add_child_edge(self.edges)
        
        # Connecting Source to each Branch
        for i in range(2):
            self.edges[i].connect(self.source, self.branches[i].entry)

# Initializing SimPy environment
env = simpy.Environment()

# Creating the system model
TOP = SystemModel(env, "TOP")

# Filling hierarchical IDs
TOP.fill_hierarchical_id()

from factorysimpy.utils.utils import draw_blockdiagram
# Visualizing the model
fig = draw_blockdiagram(TOP)
path = fig.render(filename="S3_Detailed", directory=".", format="png", cleanup=True)

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)