"""
ModelDescription:
Two subsystems where a machine inside Subsystem A connects directly to a specific machine deep inside Subsystem B. Machine IDs M1, M2, ... Buffer ID are 'B_srcnodeid_destnodeid' for buffers within a subsystem and 'B_cross_srcnodeid_destnodeid' for interconnecting subsystems

 MODEL ASSUMPTIONS:
1. Inferred a top-level system containing two subsystems named `SubsystemA` and `SubsystemB`.
2. Assumed `SubsystemA` contains a linear sequence of 3 machines and `SubsystemB` contains a linear sequence of 3 machines to provide a structure where a "deep" connection is possible.
3. Added a `src`  and 'sink' node in `SubsystemA` and `SubsystemB`  to ensure a valid simulation flow.
4. Interpreted the connection "deep inside Subsystem B" as a `Buffer` connecting the second machine of `SubsystemA` to the 3rd machine (index 2) of `SubsystemB`.
5. Assumed machines within each subsystem are connected in a standard linear series using single buffers.
6. Used default edge type `Buffer` for all connections.
7. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the subsystem model
class Subsystem(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing machines M1, M2, ...
        self.M = [Machine(env, id=f"M{i+1}") for i in range(n)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating edges
        self.edges = []
        
        # connecting source to first machine
        b_src = Buffer(env, id=f"B_{self.src.id}_{self.M[0].id}")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.M[0])
        self.edges.append(b_src)
        
        # connecting machines in series
        for i in range(n-1):
            b = Buffer(env, id=f"B_{self.M[i].id}_{self.M[i+1].id}")
            self.add_child_edge(b)
            b.connect(self.M[i], self.M[i+1])
            self.edges.append(b)
            
        # connecting last machine to sink
        b_sink = Buffer(env, id=f"B_{self.M[-1].id}_{self.sink.id}")
        self.add_child_edge(b_sink)
        b_sink.connect(self.M[-1], self.sink)
        self.edges.append(b_sink)

# defining the top level system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating subsystems
        self.subA = Subsystem(env, id="SubsystemA", n=3)
        self.add_child_node(self.subA)
        
        self.subB = Subsystem(env, id="SubsystemB", n=3)
        self.add_child_node(self.subB)
        
        # creating cross connection
        # Buffer connecting the second machine of SubsystemA to the 3rd machine of SubsystemB
        src_node = self.subA.M[1] # 2nd machine (index 1)
        dest_node = self.subB.M[2] # 3rd machine (index 2)
        
        self.cross_buffer = Buffer(env, id=f"B_cross_{src_node.id}_{dest_node.id}")
        self.add_child_edge(self.cross_buffer)
        self.cross_buffer.connect(src_node, dest_node)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)