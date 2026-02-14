"""
ModelDescription:
8 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. Name machines  M00,M01,..M07 ,   Buffers ID are B_src_00, B_01_02,B_02_03,..B_07_sink.
There are 8 such series. 2 such complete 8*8 systems are present in the system model. there are cross buffers bet M04 in 8*8_sys_1 to M04 in 8*8_sys_2. Similarly all 5th machines are inter connected between these systems B ID would be B_x_04, B_x_14, and so on 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a hierarchical structure consisting of a 'Row' class (containing the linear sequence of 8 machines), a 'System8x8' class (containing 8 parallel 'Row' instances), and a Top-level model containing 2 'System8x8' instances.
3. Assumed the 8 series (rows) within each 8x8 system are arranged in parallel.
4. Assumed hierarchical naming (appending system and row indices) is used for Machines, Sources, Sinks, and Buffers to ensure unique IDs, as the provided IDs (e.g., 'src', 'M00', 'B_01_02') would otherwise duplicate across the 8 rows and 2 systems.
5. Assumed the cross-connection connects the 5th machine (M04) of Row 'i' in System 1 to the 5th machine (M04) of Row 'i' in System 2.
6. Assumed the direction of flow for the cross buffers is from System 1 to System 2.
7. Assumed 'out_edge_selection' is set to Round Robin (or default splitting) for Machine M04 in System 1, as it connects to both M05 (internal sequence) and the cross buffer leading to System 2.
8. Used default values for all missing parameters (processing delays, capacities, inter-arrival times) for all components.
9. Used a single buffer for all connections where the number of buffers was not explicitly defined.
10. Assumed the ID format for cross buffers 'B_x_04', 'B_x_14' corresponds to 'B_x_{row_index}4'.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines M00 to M07
        self.machines = [Machine(env, id=f"M{i:02d}") for i in range(8)]
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating buffers
        self.buffers = []
        
        # Buffer from Source to M00
        b_src = Buffer(env, id="B_src_00")
        b_src.connect(self.src, self.machines[0])
        self.buffers.append(b_src)
        
        # Buffers between machines (M00->M01, M01->M02, ..., M06->M07)
        for i in range(7):
            b_id = f"B_{i:02d}_{i+1:02d}"
            b = Buffer(env, id=b_id)
            b.connect(self.machines[i], self.machines[i+1])
            self.buffers.append(b)
            
        # Buffer from M07 to Sink
        b_sink = Buffer(env, id="B_07_sink")
        b_sink.connect(self.machines[7], self.sink)
        self.buffers.append(b_sink)
        
        self.add_child_edge(self.buffers)

class System8x8(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 8 parallel rows
        self.rows = [Row(env, id=f"Row_{i}") for i in range(8)]
        self.add_child_node(self.rows)

class TopModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating two 8x8 systems
        self.sys1 = System8x8(env, id="8*8_sys_1")
        self.sys2 = System8x8(env, id="8*8_sys_2")
        self.add_child_node([self.sys1, self.sys2])
        
        # Creating cross buffers between M04 of Sys1 and M04 of Sys2
        self.cross_buffers = []
        for i in range(8):
            # M04 is at index 4
            src_node = self.sys1.rows[i].machines[4]
            dst_node = self.sys2.rows[i].machines[4]
            
            # ID format: B_x_{row_index}4
            b_id = f"B_x_{i}4"
            b = Buffer(env, id=b_id)
            b.connect(src_node, dst_node)
            self.cross_buffers.append(b)
            
        self.add_child_edge(self.cross_buffers)

# Initializing simpy environment
env = simpy.Environment()

# Defining the top level system
TOP = TopModel(env, "TOP")

# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)