"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. All rows to be named as row1, row2, row3, row4. For all buffers outside rows, buffer IDs are Bi, where i 1,2,3 for buffers that connect to sink and buffers used to connect inter rows.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class named `LinearSubsystem` to represent the repeated pattern of a Source connected to 5 Machines in series.
3. Inferred name `src` for the source node within each subsystem and `sink` for the single common sink node at the top level.
4. Used default edge type `Buffer` for all connections, including the cross-connections between subsystems and connections to the common sink, as specific edge types were not specified.
5. Used a single buffer for every connection between nodes.
6. Assumed 0-based indexing for machine positions to map the description to code: "second machine" corresponds to index 1, "third machine" to index 2, and "fourth machine" to index 3. But machine IDs are "M[i+1]" for machine in ith position.
7. Inferred that the connection to the common sink is made from the last machine (index 4) of each of the 4 parallel subsystems.
8. Inferred names for the buffers used in cross-connections as (e.g., `Bi`) and connections to the sink (e.g., `Bi`)
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the subsystem model
class LinearSubsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines M[1] to M[5]
        self.M = [Machine(env, id=f"M[{i+1}]", processing_delay=2, work_capacity=1) for i in range(5)]
        self.add_child_node(self.M)
        
        # initializing buffers B[1] to B[5]
        self.B = [Buffer(env, id=f"B[{i+1}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)
        
        # connecting nodes
        # src to first machine
        self.B[0].connect(self.src, self.M[0])
        # machines in between
        for i in range(4):
            self.B[i+1].connect(self.M[i], self.M[i+1])

# defining the top level system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 4 rows
        self.rows = [LinearSubsystem(env, id=f"row{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating external buffers
        self.ext_buffers = []
        buf_idx = 1
        
        # connecting last machine of each row to sink
        for i in range(4):
            b = Buffer(env, id=f"B{buf_idx}", capacity=2)
            self.add_child_edge(b)
            b.connect(self.rows[i].M[-1], self.sink)
            self.ext_buffers.append(b)
            buf_idx += 1
            
        # Cross connections
        # Row 2 Machine 3 (index 2) to Row 3 Machine 4 (index 3)
        # Row 2 Machine 3 (index 2) to Row 4 Machine 2 (index 1)
        
        # Setting work capacity for machines with multiple inputs
        self.rows[2].M[3].work_capacity = 2
        self.rows[3].M[1].work_capacity = 2
        
        # Connection 1: row2.M[2] -> row3.M[3]
        b_cross1 = Buffer(env, id=f"B{buf_idx}", capacity=2)
        self.add_child_edge(b_cross1)
        b_cross1.connect(self.rows[1].M[2], self.rows[2].M[3])
        self.ext_buffers.append(b_cross1)
        buf_idx += 1
        
        # Connection 2: row2.M[2] -> row4.M[1]
        b_cross2 = Buffer(env, id=f"B{buf_idx}", capacity=2)
        self.add_child_edge(b_cross2)
        b_cross2.connect(self.rows[1].M[2], self.rows[3].M[1])
        self.ext_buffers.append(b_cross2)
        buf_idx += 1

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