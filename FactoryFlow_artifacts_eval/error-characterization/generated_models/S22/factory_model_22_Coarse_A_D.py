"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. All rows to be named as row1, row2, row3, row4.  For all buffers outside rows, buffer IDs are Bi, where i 1,2,3 for buffers that connect to sink and buffers used to connect inter rows.

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

class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines
        self.M = [Machine(env, id=f"M[{i+1}]", processing_delay=2) for i in range(5)]
        self.add_child_node(self.M)
        
        # initializing buffers
        self.B = [Buffer(env, id=f"B[{i+1}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)
        
        # connecting source to first machine
        self.B[0].connect(self.src, self.M[0])
        
        # connecting machines in series
        for i in range(4):
            self.B[i+1].connect(self.M[i], self.M[i+1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 4 subsystems
        self.rows = [Subsystem(env, id=f"row{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating external buffers
        # 4 for sink connections + 2 for cross connections
        self.ext_buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(6)]
        self.add_child_edge(self.ext_buffers)
        
        # connecting last machine of each row to sink
        for i in range(4):
            self.ext_buffers[i].connect(self.rows[i].M[-1], self.sink)
            
        # connecting third machine in second subsystem to fourth machine in third subsystem
        # row2 (index 1) M3 (index 2) -> row3 (index 2) M4 (index 3)
        self.ext_buffers[4].connect(self.rows[1].M[2], self.rows[2].M[3])
        
        # connecting third machine in second subsystem to second machine in fourth subsystem
        # row2 (index 1) M3 (index 2) -> row4 (index 3) M2 (index 1)
        self.ext_buffers[5].connect(self.rows[1].M[2], self.rows[3].M[1])
        
        # updating work_capacity for machines with multiple inputs
        self.rows[2].M[3].work_capacity = 2
        self.rows[3].M[1].work_capacity = 2

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