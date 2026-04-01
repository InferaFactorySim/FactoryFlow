"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. All rows to be named as row1, row2, row3, row4. For all buffers outside rows, buffer IDs are Bi, where i 1,2,3 for buffers that connect to sink and buffers used to connect inter rows.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description, with generic IDs (e.g., "M", "src", "sink") assigned where specific names were not provided.
2. A class named `Subsystem` (or similar) is inferred to represent the repeated structure of one Source connected to 5 Machines in series.
3. Used default edge type `Buffer` for all connections (between machines in series, from subsystems to the common sink, and for the specific cross-connections described) as edge type was not specified.
4. Used a single buffer for every connection between two nodes.
5. Assumed the "end" of the subsystem refers to the last machine (5th machine) in the series, which is connected to the common sink.
6. Interpreted "second subsystem" as index 1, "third subsystem" as index 2, and "fourth subsystem" as index 3 (0-based indexing).
7. Interpreted "second machine" as index 1, "third machine" as index 2, and "fourth machine" as index 3 within their respective subsystems.
8. Used default values for all missing parameters (inter-arrival times, processing delays, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the subsystem model (Source + 5 Machines in series)
class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # Initializing 5 machines in series
        # Machines are named M[i+1]
        self.M = []
        for i in range(5):
            # Default work_capacity is 1, processing_delay is 2
            m = Machine(env, id=f"M[{i+1}]", processing_delay=2, work_capacity=1)
            self.M.append(m)
        self.add_child_node(self.M)
        
        # Initializing internal buffers
        # Buffers are named B[i+1]
        self.B = []
        
        # Connect Source to first machine (M[1])
        b_src = Buffer(env, id="B[1]", capacity=2)
        self.B.append(b_src)
        b_src.connect(self.src, self.M[0])
        
        # Connect machines in series
        for i in range(4):
            b = Buffer(env, id=f"B[{i+2}]", capacity=2)
            self.B.append(b)
            b.connect(self.M[i], self.M[i+1])
            
        self.add_child_edge(self.B)

# Defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating 4 parallel subsystems (rows)
        self.rows = []
        for i in range(4):
            row = Subsystem(env, id=f"row{i+1}")
            self.rows.append(row)
        self.add_child_node(self.rows)
        
        # Adjusting work_capacity for machines with multiple inputs
        # Third machine in second subsystem (row2, M3) connects to:
        # 1. Fourth machine in third subsystem (row3, M4)
        # 2. Second machine in fourth subsystem (row4, M2)
        
        # row3.M4 has inputs from row3.M3 (internal) and row2.M3 (external)
        self.rows[2].M[3].work_capacity = 2
        
        # row4.M2 has inputs from row4.M1 (internal) and row2.M3 (external)
        self.rows[3].M[1].work_capacity = 2
        
        # Creating external buffers (Bi)
        self.ext_buffers = []
        buf_idx = 1
        
        # Cross connection 1: row2.M3 -> row3.M4
        b_cross1 = Buffer(env, id=f"B{buf_idx}", capacity=2)
        self.add_child_edge(b_cross1)
        b_cross1.connect(self.rows[1].M[2], self.rows[2].M[3])
        self.ext_buffers.append(b_cross1)
        buf_idx += 1
        
        # Cross connection 2: row2.M3 -> row4.M2
        b_cross2 = Buffer(env, id=f"B{buf_idx}", capacity=2)
        self.add_child_edge(b_cross2)
        b_cross2.connect(self.rows[1].M[2], self.rows[3].M[1])
        self.ext_buffers.append(b_cross2)
        buf_idx += 1
        
        # Connecting all rows to the common sink
        for i in range(4):
            b_sink = Buffer(env, id=f"B{buf_idx}", capacity=2)
            self.add_child_edge(b_sink)
            # Connect last machine of each row to sink
            b_sink.connect(self.rows[i].M[4], self.sink)
            self.ext_buffers.append(b_sink)
            buf_idx += 1

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