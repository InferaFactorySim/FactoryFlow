"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.

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

# A system with 4 parallel subsystems, each consisting of a source and 5 machines in series.
# All subsystems connect to a common sink.
# Specific cross-connections exist between machines of different subsystems.

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating 4 parallel subsystems
        self.subsystems = [LinearSubsystem(env, id=f"subsystems[{i}]") for i in range(4)]
        self.add_child_node(self.subsystems)
        
        # Creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        self.e = []
        
        # Connecting the last machine of each subsystem to the common sink
        for i in range(4):
            edge = Buffer(env, id=f"edge[{len(self.e)}]")
            self.add_child_edge(edge)
            # Connect last machine (index 4) to sink
            edge.connect(self.subsystems[i].M[-1], self.sink)
            self.e.append(edge)
            
        # Cross-connections
        # Source node: 3rd machine in 2nd subsystem (index 1, machine index 2)
        cross_source = self.subsystems[1].M[2]
        
        # Target 1: 4th machine in 3rd subsystem (index 2, machine index 3)
        cross_target_1 = self.subsystems[2].M[3]
        edge_cross_1 = Buffer(env, id=f"edge[{len(self.e)}]")
        self.add_child_edge(edge_cross_1)
        edge_cross_1.connect(cross_source, cross_target_1)
        self.e.append(edge_cross_1)
        
        # Target 2: 2nd machine in 4th subsystem (index 3, machine index 1)
        cross_target_2 = self.subsystems[3].M[1]
        edge_cross_2 = Buffer(env, id=f"edge[{len(self.e)}]")
        self.add_child_edge(edge_cross_2)
        edge_cross_2.connect(cross_source, cross_target_2)
        self.e.append(edge_cross_2)

class LinearSubsystem(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        
        self.e = []
        
        # Connecting source to first machine
        edge_src = Buffer(env, id=f"edge[{len(self.e)}]")
        self.add_child_edge(edge_src)
        edge_src.connect(self.source, self.M[0])
        self.e.append(edge_src)
        
        # Connecting machines in series
        for i in range(n-1):
            edge = Buffer(env, id=f"edge[{len(self.e)}]")
            self.add_child_edge(edge)
            edge.connect(self.M[i], self.M[i+1])
            self.e.append(edge)

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