"""
ModelDescription:
There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 4 times, where they are in parallel, each with its own source. At the end, they are all connected to the common sink. The third machine in second subsystem is also connected to fourth machine in third subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine in second subsystem.All machines are name as M[i], i is the position. and all buffers as B[i], i is the position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. Let  buffer IDs be Bi, where i 1,2,3 for buffers that connect to sink and buffers used to connect inter rows.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class named `LinearSubsystem` to represent the repeated pattern of a Source connected to 5 Machines in series.
3. Inferred name `src` for the source node within each subsystem and `sink` for the single common sink node at the top level.
4. Used default edge type `Buffer` for all connections, including the cross-connections between subsystems and connections to the common sink, as specific edge types were not specified.
5. Used a single buffer for every connection between nodes.
6. Assumed 1-based indexing for machine positions to map the description to code: "second machine" corresponds to index 1, "third machine" to index 2, and "fourth machine" to index 3.
7. Inferred that the connection to the common sink is made from the last machine (index 4) of each of the 4 parallel subsystems.
8. Inferred names for the buffers used in cross-connections as (e.g., `Bi`) and connections to the sink (e.g., `Bi`) as the description only specified names `B[i]` for the internal buffers.
"""

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
        
        # Creating common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # Creating 4 parallel subsystems
        self.R = [LinearSubsystem(env, id=f"R[{i}]") for i in range(4)]
        self.add_child_node(self.R)

        # Creating external buffers (Bi)
        # 4 connections to sink + 2 cross connections = 6 buffers
        self.Bi = [Buffer(env, id=f"Bi[{i}]", capacity=2) for i in range(6)]
        self.add_child_edge(self.Bi)

        # Connecting last machine of each subsystem to common sink
        for i in range(4):
            # Last machine is M[4]
            self.Bi[i].connect(self.R[i].M[4], self.sink)

        # Cross connections
        # Third machine (index 2) in second subsystem (index 1) to fourth machine (index 3) in third subsystem (index 2)
        self.Bi[4].connect(self.R[1].M[2], self.R[2].M[3])
        
        # Third machine (index 2) in second subsystem (index 1) to second machine (index 1) in fourth subsystem (index 3)
        self.Bi[5].connect(self.R[1].M[2], self.R[3].M[1])

        # Setting work_capacity to 2 for machines with multiple input edges
        self.R[2].M[3].work_capacity = 2
        self.R[3].M[1].work_capacity = 2

class LinearSubsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)

        # Creating 5 machines in series
        self.M = [Machine(env, id=f"M[{i}]", processing_delay=2) for i in range(5)]
        self.add_child_node(self.M)

        # Creating buffers
        # 1 from src to M[0], 4 between machines = 5 buffers
        self.B = [Buffer(env, id=f"B[{i}]", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)

        # Connecting source to first machine
        self.B[0].connect(self.src, self.M[0])

        # Connecting machines in series
        for i in range(4):
            self.B[i+1].connect(self.M[i], self.M[i+1])

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)