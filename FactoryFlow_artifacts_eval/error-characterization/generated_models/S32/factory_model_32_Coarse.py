"""
ModelDescription:
Eight machines are connected in series with src as source and sink as sink. Machines are named M00 to M07. Buffers are B_src_00, B_00_01, …, B_07_sink.
Eight such series form one 8×8 system . Two identical 8×8 systems are present.
The 5th machines of corresponding rows in both systems are interconnected using cross buffers named B_x_04, B_x_14, and so on

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
3. Inferred a repeated pattern and created a `RowModel` class representing the linear sequence of 8 machines (M00 to M07) with a Source and Sink, and a `SystemModel` class containing 8 parallel instances of `RowModel`.
4. Assumed each of the 8 rows in the 8x8 system has its own independent Source and Sink.
5. Assumed the "5th machine" corresponds to the machine at index 4 (M04).
6. Inferred the direction of flow for the cross-connection buffers is unidirectional from the first system (System 0) to the second system (System 1).
7. Assumed the cross buffers connect the output of M04 in System 0 to the input of M04 in System 1.
8. Assumed `out_edge_selection` is set to "ROUND_ROBIN" (default) for machines where flow splits (M04 in System 0).
9. Used a single buffer for all connections where the specific number of buffers was not explicitly specified.
10. Inferred that the naming convention `B_x_04`, `B_x_14` corresponds to `B_x_{row_index}_{machine_index}`.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the row model (8 machines in series)
class RowModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing machines M00 to M07
        self.M = [Machine(env, id=f"M{i:02d}") for i in range(8)]
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating edges
        self.edges = []
        
        # Buffer from source to M00: B_src_00
        b_src = Buffer(env, id="B_src_00")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.M[0])
        self.edges.append(b_src)
        
        # Buffers between machines: B_00_01 to B_06_07
        for i in range(7):
            buf = Buffer(env, id=f"B_{i:02d}_{i+1:02d}")
            self.add_child_edge(buf)
            buf.connect(self.M[i], self.M[i+1])
            self.edges.append(buf)
            
        # Buffer from M07 to sink: B_07_sink
        b_sink = Buffer(env, id="B_07_sink")
        self.add_child_edge(b_sink)
        b_sink.connect(self.M[7], self.sink)
        self.edges.append(b_sink)

# defining the 8x8 system containing 8 rows
class System8x8(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # creating 8 rows
        self.rows = [RowModel(env, id=f"Row[{i}]") for i in range(8)]
        self.add_child_node(self.rows)

# defining the top system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating two 8x8 systems
        self.systems = [System8x8(env, id=f"Sys[{i}]") for i in range(2)]
        self.add_child_node(self.systems)
        
        # creating cross connections between the 5th machine (index 4) of corresponding rows
        self.cross_buffers = []
        for r in range(8):
            # Cross buffer naming: B_x_{row}4 (e.g., B_x_04, B_x_14)
            buf_id = f"B_x_{r}4"
            buf = Buffer(env, id=buf_id)
            self.add_child_edge(buf)
            
            # Connecting M04 of System 0 to M04 of System 1
            src_mach = self.systems[0].rows[r].M[4]
            dst_mach = self.systems[1].rows[r].M[4]
            
            # Setting out_edge_selection to ROUND_ROBIN for the splitting machine in System 0
            src_mach.out_edge_selection = "ROUND_ROBIN"
            
            buf.connect(src_mach, dst_mach)
            self.cross_buffers.append(buf)

# initializing simpy environment
env = simpy.Environment()
# creating the system
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)