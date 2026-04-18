"""
ModelDescription:
Subsystem_A (3 machines in series) and Subsystem_B (3 machines in series). A custom edge connects M2 in Subsystem_A to M3 in Subsystem_B. All buffer ID are B_src_dest in class and B_cross_src_dest where src is src node id and dest is dest node id.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. Inferred a repeated pattern of "3 machines in series" and created a reusable class for this subsystem to instantiate both Subsystem_A and Subsystem_B.
3. Inferred machine IDs within the subsystems as 'src',  `M1`, `M2`, and `M3` and 'sink' to align with the user's specific reference to "M2" and "M3" within a 3-machine system.
4. Used default Node Type `Machine` for all nodes within the subsystems as not specified.
5. Used default Edge Type `Buffer` for all connections, including the internal series connections and the custom edge connecting the subsystems.
6. Used a single buffer for all connections between nodes where the number of buffers was not specified.
7. Inferred the need for a separate `src` and `sink` to create a valid simulation flow.
8. Assumed the separate source `src` connects to the first machine of Subsystem_A (`M1`) and Source connects to Subsystem_B (`M1`)
9. Assumed the last machine of Subsystem_B (`M3`)  and  Subsystem_A (`M3`)connects to the global `sink` and 'sink'.
10. Assumed the custom edge flows from `Subsystem_A.M2` to `Subsystem_B.M3`.
11. Used default values for all missing parameters (processing delays, capacities, inter-arrival times) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the subsystem model with 3 machines in series
class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing machines M1, M2, M3
        self.M = [Machine(env, id=f"M{i+1}") for i in range(3)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating edges
        # src to M1
        self.edge_src = Buffer(env, id=f"B_{self.src.id}_{self.M[0].id}")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.src, self.M[0])
        
        # M1 to M2, M2 to M3
        self.internal_edges = []
        for i in range(2):
            edge = Buffer(env, id=f"B_{self.M[i].id}_{self.M[i+1].id}")
            self.internal_edges.append(edge)
            self.add_child_edge(edge)
            edge.connect(self.M[i], self.M[i+1])
            
        # M3 to sink
        self.edge_sink = Buffer(env, id=f"B_{self.M[-1].id}_{self.sink.id}")
        self.add_child_edge(self.edge_sink)
        self.edge_sink.connect(self.M[-1], self.sink)

# defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating Subsystem_A
        self.sub_a = Subsystem(env, id="Subsystem_A")
        
        # creating Subsystem_B
        self.sub_b = Subsystem(env, id="Subsystem_B")
        
        self.add_child_node([self.sub_a, self.sub_b])
        
        # creating custom edge from Subsystem_A M2 to Subsystem_B M3
        # M2 is at index 1, M3 is at index 2
        src_node = self.sub_a.M[1]
        dest_node = self.sub_b.M[2]
        
        self.custom_edge = Buffer(env, id=f"B_cross_{src_node.id}_{dest_node.id}")
        self.add_child_edge(self.custom_edge)
        self.custom_edge.connect(src_node, dest_node)

# initializing simpy environment
env = simpy.Environment()

# creating the system model
TOP = SystemModel(env, "TOP")

# filling hierarchical ids
TOP.fill_hierarchical_id()

# validating the model
TOP.validate()

# running the simulation
TOP.run_simulation(25)