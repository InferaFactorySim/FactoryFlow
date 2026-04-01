"""
ModelDescription:
"8 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. 
Name machines  M00,M01,..M07 ,   Buffers ID are B_src_00, B_01_02,B_02_03,..B_07_sink.
There are 8 such series. 2 such complete 8*8 systems are present in the system model. 
There are cross buffers bet M04 in 8*8_sys_1 to M04 in 8*8_sys_2. Similarly all 5th machines 
are inter connected between these systems B ID would be B_x_04, B_x_14, and so on 
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class LinearSeries(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing machines M00 to M07
        self.M = [Machine(env, id=f"M{i:02d}") for i in range(8)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        self.edges = []
        
        # Buffer from Source to M00
        b_src = Buffer(env, id="B_src_00")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.M[0])
        self.edges.append(b_src)
        
        # Buffers between machines (M00->M01, ..., M06->M07)
        for i in range(7):
            b_id = f"B_{i:02d}_{i+1:02d}"
            b = Buffer(env, id=b_id)
            self.add_child_edge(b)
            b.connect(self.M[i], self.M[i+1])
            self.edges.append(b)
            
        # Buffer from M07 to Sink
        b_sink = Buffer(env, id="B_07_sink")
        self.add_child_edge(b_sink)
        b_sink.connect(self.M[7], self.sink)
        self.edges.append(b_sink)

class System8x8(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 8 rows of LinearSeries
        self.rows = [LinearSeries(env, id=f"row_{i}") for i in range(8)]
        self.add_child_node(self.rows)

class TopSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating two 8x8 systems
        self.sys_1 = System8x8(env, id="sys_1")
        self.sys_2 = System8x8(env, id="sys_2")
        self.add_child_node([self.sys_1, self.sys_2])
        
        # Creating cross buffers connecting M04 of sys_1 to M04 of sys_2
        self.cross_buffers = []
        for i in range(8):
            # ID pattern: B_x_{row_index}4
            b_id = f"B_x_{i}4"
            b = Buffer(env, id=b_id)
            self.add_child_edge(b)
            
            # M04 is at index 4 (5th machine)
            source_machine = self.sys_1.rows[i].M[4]
            dest_machine = self.sys_2.rows[i].M[4]
            
            b.connect(source_machine, dest_machine)
            self.cross_buffers.append(b)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = TopSystem(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)