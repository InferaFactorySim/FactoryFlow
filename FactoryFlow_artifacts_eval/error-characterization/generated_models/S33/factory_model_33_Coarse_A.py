"""
ModelDescription:
5 machines, a source and sink are in series and 5 such series forms a subsystem with ID= 5*5_sys_i  and it is repeated 4 times.  The machine in the 2nd row and 3rd column of all the subsystems are interconnected. Name machines  M00,M01,.. ,   Buffers ID are B_src_00, B_01_02,B_02_03,. and cross connecting buffer IDs are B_x_1, ..

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

# defining the row model (linear sequence of 5 machines)
class Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing machines M00 to M04
        self.machines = [Machine(env, id=f"M0{i}") for i in range(5)]
        self.add_child_node(self.machines)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing buffers
        self.buffers = []
        
        # Buffer from Source to M00
        b_src = Buffer(env, id="B_src_00")
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.machines[0])
        self.buffers.append(b_src)
        
        # Buffers between machines (B_00_01, B_01_02, etc.)
        for i in range(4):
            b = Buffer(env, id=f"B_0{i}_0{i+1}")
            self.add_child_edge(b)
            b.connect(self.machines[i], self.machines[i+1])
            self.buffers.append(b)
            
        # Buffer from M04 to Sink
        b_sink = Buffer(env, id="B_04_sink")
        self.add_child_edge(b_sink)
        b_sink.connect(self.machines[4], self.sink)
        self.buffers.append(b_sink)

# defining the subsystem model (5 parallel rows)
class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # creating 5 parallel rows
        self.rows = [Row(env, id=f"Row_{i}") for i in range(5)]
        self.add_child_node(self.rows)

# defining the top level system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 4 subsystems
        self.subsystems = [Subsystem(env, id=f"5*5_sys_{i}") for i in range(4)]
        self.add_child_node(self.subsystems)
        
        # creating interconnections between subsystems
        self.cross_buffers = []
        for i in range(3):
            # Machine in 2nd row (index 1) and 3rd column (index 2)
            src_machine = self.subsystems[i].rows[1].machines[2]
            dst_machine = self.subsystems[i+1].rows[1].machines[2]
            
            # Setting out_edge_selection to ROUND_ROBIN for the source machine
            src_machine.out_edge_selection = "ROUND_ROBIN"
            
            # Creating cross connecting buffer
            b_x = Buffer(env, id=f"B_x_{i+1}")
            self.add_child_edge(b_x)
            b_x.connect(src_machine, dst_machine)
            self.cross_buffers.append(b_x)

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)