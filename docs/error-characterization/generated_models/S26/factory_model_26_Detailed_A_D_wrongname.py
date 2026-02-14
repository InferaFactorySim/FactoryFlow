"""
ModelDescription:
Subsystem_A (3 machines in series) and Subsystem_B (3 machines in series). A custom edge connects  Subsystem_A.M2  to Subsystem_B.M3 . All buffer ID are B_src_dest in class and B_cross_src_dest where src is src node id and dest is dest node id.

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

# Reusable class for "3 machines in series" pattern
class ThreeMachineSeries(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating internal source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Creating machines M1, M2, M3
        self.machines = []
        for i in range(1, 4):
            m = Machine(env, id=f"M{i}")
            self.machines.append(m)
        self.add_child_node(self.machines)
        
        # Exposing machines for external connections
        self.M1 = self.machines[0]
        self.M2 = self.machines[1]
        self.M3 = self.machines[2]
        
        # Creating internal sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges (buffers)
        # Sequence: src -> M1 -> M2 -> M3 -> sink
        nodes_seq = [self.src] + self.machines + [self.sink]
        self.edges = []
        
        for i in range(len(nodes_seq) - 1):
            u = nodes_seq[i]
            v = nodes_seq[i+1]
            # Buffer ID convention: B_src_dest
            edge_id = f"B_{u.id}_{v.id}"
            b = Buffer(env, id=edge_id)
            b.connect(u, v)
            self.edges.append(b)
            
        self.add_child_edge(self.edges)

# Main System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Instantiating Subsystem_A and Subsystem_B
        self.Subsystem_A = ThreeMachineSeries(env, id="Subsystem_A")
        self.Subsystem_B = ThreeMachineSeries(env, id="Subsystem_B")
        self.add_child_node([self.Subsystem_A, self.Subsystem_B])
        
        # Creating custom edge from Subsystem_A.M2 to Subsystem_B.M3
        src_node = self.Subsystem_A.M2
        dest_node = self.Subsystem_B.M3
        
        # Buffer ID convention: B_cross_src_dest
        # Using hierarchical names to ensure uniqueness and clarity
        edge_id = f"B_cross_{self.Subsystem_A.id}_{src_node.id}_{self.Subsystem_B.id}_{dest_node.id}"
        self.cross_edge = Buffer(env, id=edge_id)
        self.add_child_edge(self.cross_edge)
        
        self.cross_edge.connect(src_node, dest_node)

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