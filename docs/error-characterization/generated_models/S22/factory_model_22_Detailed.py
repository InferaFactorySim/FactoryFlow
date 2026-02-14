"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.All machines are name as M[i], i is the position. and all buffers as B[i], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class named `LinearSubsystem` to represent the repeated pattern of a Source connected to 5 Machines in series.
3. Inferred name `src` for the source node within each subsystem and `sink` for the single common sink node at the top level.
4. Used default edge type `Buffer` for all connections, including the cross-connections between subsystems and connections to the common sink, as specific edge types were not specified.
5. Used a single buffer for every connection between nodes.
6. Assumed 0-based indexing for machine positions to map the description to code: "second machine" corresponds to index 1, "third machine" to index 2, and "fourth machine" to index 3.
7. Inferred that the connection to the common sink is made from the last machine (index 4) of each of the 4 parallel subsystems.
8. Inferred names for the buffers used in cross-connections (e.g., `cross_edge`) and connections to the sink (e.g., `sink_edge`) as the description only specified names `B[i]` for the internal buffers.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class LinearSubsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=2) for i in range(5)]
        self.add_child_node(self.M)
        
        # initializing buffers
        # B[0] connects src to M[0]
        # B[1] connects M[0] to M[1]
        # ...
        # B[4] connects M[3] to M[4]
        self.B = [Buffer(env, id=f"B[{i}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)
        
        # connecting nodes
        self.B[0].connect(self.src, self.M[0])
        for i in range(4):
            self.B[i+1].connect(self.M[i], self.M[i+1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing subsystems
        self.subsystems = [LinearSubsystem(env, id=f"subsystem[{i}]") for i in range(4)]
        self.add_child_node(self.subsystems)
        
        # initializing edges to sink
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]", capacity=2) for i in range(4)]
        self.add_child_edge(self.sink_edges)
        
        # connecting subsystems to sink
        for i in range(4):
            self.sink_edges[i].connect(self.subsystems[i].M[4], self.sink)
            
        # initializing cross connection edges
        self.cross_edges = [Buffer(env, id=f"cross_edge[{i}]", capacity=2) for i in range(2)]
        self.add_child_edge(self.cross_edges)
        
        # defining cross connections
        # 3rd machine in 2nd subsystem (index 1) -> M[2]
        src_node = self.subsystems[1].M[2]
        
        # 4th machine in 3rd subsystem (index 2) -> M[3]
        dest_node_1 = self.subsystems[2].M[3]
        
        # 2nd machine in 4th subsystem (index 3) -> M[1]
        dest_node_2 = self.subsystems[3].M[1]
        
        # connecting cross edges
        self.cross_edges[0].connect(src_node, dest_node_1)
        self.cross_edges[1].connect(src_node, dest_node_2)
        
        # setting work capacity for machines with multiple inputs
        dest_node_1.work_capacity = 2
        dest_node_2.work_capacity = 2

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating model
TOP.validate()
# running simulation
TOP.run_simulation(25)