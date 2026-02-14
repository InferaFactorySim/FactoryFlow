"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. All buffer ID is as "B[i]"

 MODEL ASSUMPTIONS:
1. The repeated structure of a source connected to 5 machines in series is defined as a reusable class (e.g., LinearSubsystem).
2. Node names and IDs are inferred based on their hierarchical position and index (e.g., M[0]...M[4] for machines, subsystems[0]...subsystems[3]) as they are not explicitly provided.
3. All connections between nodes (Source to Machine, Machine to Machine, Machine to Sink) are assumed to be of type Buffer.
4. A single Buffer is used for every connection between two nodes.
5. The connection to the common sink is made from the last machine (the 5th machine) of each of the 4 parallel subsystems.
6. Default values are used for all missing parameters including processing delays, inter-arrival times, and buffer capacities.
7. The specific cross-connections between subsystems (e.g., 3rd machine of 2nd subsystem to others) are implemented using Buffers.
8. References to ordinal positions (e.g., "third machine", "second subsystem") are interpreted as 0-based indices (e.g., index 2 for third machine, index 1 for second subsystem).
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class LinearSubsystem(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=2) for i in range(n)]
        self.add_child_node(self.M)
        
        # creating edges
        self.edges = []
        
        # src to first machine
        e = Buffer(env, id="edge[0]", capacity=2)
        self.add_child_edge(e)
        e.connect(self.src, self.M[0])
        self.edges.append(e)
        
        # machines in between
        for i in range(n-1):
            e = Buffer(env, id=f"edge[{i+1}]", capacity=2)
            self.add_child_edge(e)
            e.connect(self.M[i], self.M[i+1])
            self.edges.append(e)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating subsystems
        self.subsystems = [LinearSubsystem(env, id=f"subsystems[{i}]") for i in range(4)]
        self.add_child_node(self.subsystems)
        
        # initializing common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        self.edges = []
        edge_idx = 0
        
        # connecting last machine of each subsystem to common sink
        for i in range(4):
            e = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(e)
            # Last machine is M[4]
            e.connect(self.subsystems[i].M[4], self.sink)
            self.edges.append(e)
            edge_idx += 1
            
        # Cross connections
        # 3rd machine in 2nd subsystem (index 1, machine 2) -> 4th machine in 3rd subsystem (index 2, machine 3)
        # 3rd machine in 2nd subsystem (index 1, machine 2) -> 2nd machine in 4th subsystem (index 3, machine 1)
        
        # Update work capacities for machines with multiple inputs
        self.subsystems[2].M[3].work_capacity = 2
        self.subsystems[3].M[1].work_capacity = 2
        
        # Connection 1
        e1 = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
        self.add_child_edge(e1)
        e1.connect(self.subsystems[1].M[2], self.subsystems[2].M[3])
        self.edges.append(e1)
        edge_idx += 1
        
        # Connection 2
        e2 = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
        self.add_child_edge(e2)
        e2.connect(self.subsystems[1].M[2], self.subsystems[3].M[1])
        self.edges.append(e2)
        edge_idx += 1

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