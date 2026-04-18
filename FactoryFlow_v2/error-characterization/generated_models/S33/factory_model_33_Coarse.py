"""
ModelDescription:
5 machines, a source and sink are in series and 5 such series forms a subsystem with ID= 5*5_sys_i  and it is repeated 4 times.  The machine in the 2nd row and 3rd column of all the subsystems are interconnected.

 MODEL ASSUMPTIONS:
1. Inferred a hierarchical structure: a `Row` class containing the linear sequence (Source + 5 Machines + Sink), and a `Subsystem` class containing 5 parallel `Row` instances, to match the repeated pattern description.
2. Node names and Types are chosen according to user's description where available; inferred IDs `Row_[index]` for rows and `M_[index]` for machines within rows.
3. Used default edge type `Buffer` with a quantity of 1 for all connections (between Source-Machine, Machine-Machine, Machine-Sink, and inter-subsystem connections) as not specified.
4. Used default values for all missing parameters (capacities, processing delays, inter-arrival times) for all components.
5. Interpreted "interconnected" for the machine in the 2nd row and 3rd column as a serial flow from Subsystem i to Subsystem i+1 (e.g., Sys0 -> Sys1 -> Sys2 -> Sys3).
6. Interpreted "2nd row" as index 1 and "3rd column" as the 3rd machine (index 2) in the linear sequence of 5 machines.
7. Assumed `out_edge_selection="ROUND_ROBIN"` for the interconnected machines, as they connect to both the next machine in their row and the corresponding machine in the next subsystem.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Row class: Source + 5 Machines + Sink in series
class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing 5 machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(5)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges (buffers)
        # 1 from Source->M0, 4 between machines, 1 from M4->Sink = 6 edges
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(6)]
        self.add_child_edge(self.e)
        
        # Connecting Source to first machine
        self.e[0].connect(self.src, self.M[0])
        
        # Connecting machines in series
        for i in range(4):
            self.e[i+1].connect(self.M[i], self.M[i+1])
            
        # Connecting last machine to sink
        self.e[5].connect(self.M[4], self.sink)

# Subsystem class: 5 parallel Rows
class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 5 parallel Rows
        self.rows = [Row(env, id=f"Row_[{i}]") for i in range(5)]
        self.add_child_node(self.rows)

# SystemModel class: 4 Subsystems with specific interconnection
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 Subsystems
        self.subsystems = [Subsystem(env, id=f"5*5_sys_{i}") for i in range(4)]
        self.add_child_node(self.subsystems)
        
        # Interconnecting machines in 2nd row (index 1), 3rd column (index 2)
        self.inter_edges = []
        for i in range(3):
            # Source machine in current subsystem
            src_node = self.subsystems[i].rows[1].M[2]
            # Destination machine in next subsystem
            dst_node = self.subsystems[i+1].rows[1].M[2]
            
            # Setting out_edge_selection to ROUND_ROBIN as per assumption
            src_node.out_edge_selection = "ROUND_ROBIN"
            
            # Creating buffer for connection
            edge = Buffer(env, id=f"inter_edge[{i}]")
            self.add_child_edge(edge)
            edge.connect(src_node, dst_node)
            self.inter_edges.append(edge)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)