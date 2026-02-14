"""
ModelDescription:
There’s a subsytem A- "1-3-1" where a single machine is connected to 3 machines in parallel which are then connected to another common machine. this subsytem is connected to another subsystem B"1-1" having 2 machines in series. B is again connected to A. Now this whole ABA thing is repeated 3 times and is connected in series.

 MODEL ASSUMPTIONS:
1.  **Hierarchical Structure**: A class named `SubsystemA` will be created for the "1-3-1" configuration, and a class named `SubsystemB` will be created for the "1-1" configuration. A third class named `CompositeBlock` will be created to represent the "ABA" sequence (SubsystemA -> SubsystemB -> SubsystemA).
2.  **Global Inputs/Outputs**: Since the description describes a processing line but not the entry and exit points, a `Source` node is assumed to be connected to the start of the first "ABA" block, and a `Sink` node is assumed to be connected to the end of the third "ABA" block.
3.  **Node Naming**: Since specific machine names are not provided, machines within Subsystem A will be named `In_Machine`, `Parallel_Machine_1` through `3`, and `Out_Machine`. Machines in Subsystem B will be named `Machine_1` and `Machine_2`.
4.  **Edge Type**: All connections between nodes and subsystems are assumed to be of type `Buffer`.
5.  **Buffer Quantity**: A single `Buffer` is assumed to exist between every connected pair of machines or subsystems, as the number of buffers was not specified.
6.  **Parameters**: Used default values for all missing parameters (processing delays, buffer capacities, and source inter-arrival times) for all components.
7.  **Flow Logic**: In Subsystem A, the single input machine acts as a splitter distributing parts to the 3 parallel machines, and the common output machine acts as a combiner receiving parts from them.
8.  **System Topology**: The final system consists of 3 `CompositeBlock` instances connected in series.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Subsystem A: "1-3-1" configuration
# Single machine -> 3 parallel machines -> Common machine
class SubsystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating nodes
        self.in_machine = Machine(env, id="In_Machine")
        self.parallel_machines = [Machine(env, id=f"Parallel_Machine_{i+1}") for i in range(3)]
        self.out_machine = Machine(env, id="Out_Machine")
        
        # Adding nodes to child nodes
        self.add_child_node(self.in_machine)
        self.add_child_node(self.parallel_machines)
        self.add_child_node(self.out_machine)
        
        # Creating edges
        # 3 edges for In -> Parallel, 3 edges for Parallel -> Out
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(6)]
        self.add_child_edge(self.edges)
        
        # Connecting In_Machine to Parallel Machines
        for i in range(3):
            self.edges[i].connect(self.in_machine, self.parallel_machines[i])
            
        # Connecting Parallel Machines to Out_Machine
        for i in range(3):
            self.edges[3+i].connect(self.parallel_machines[i], self.out_machine)
            
        # Defining source and sink for this subsystem
        self.source = self.in_machine
        self.sink = self.out_machine

# Subsystem B: "1-1" configuration
# 2 machines in series
class SubsystemB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating nodes
        self.m1 = Machine(env, id="Machine_1")
        self.m2 = Machine(env, id="Machine_2")
        
        # Adding nodes to child nodes
        self.add_child_node([self.m1, self.m2])
        
        # Creating edge
        self.edge = Buffer(env, id="edge[0]")
        self.add_child_edge(self.edge)
        
        # Connecting Machine_1 to Machine_2
        self.edge.connect(self.m1, self.m2)
        
        # Defining source and sink for this subsystem
        self.source = self.m1
        self.sink = self.m2

# Composite Block: "ABA" sequence
# SubsystemA -> SubsystemB -> SubsystemA
class CompositeBlock(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating subsystems
        self.sub_a1 = SubsystemA(env, id="SubsystemA_1")
        self.sub_b = SubsystemB(env, id="SubsystemB")
        self.sub_a2 = SubsystemA(env, id="SubsystemA_2")
        
        # Adding subsystems to child nodes
        self.add_child_node([self.sub_a1, self.sub_b, self.sub_a2])
        
        # Creating edges to connect subsystems
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(2)]
        self.add_child_edge(self.edges)
        
        # Connecting A1 -> B
        self.edges[0].connect(self.sub_a1.sink, self.sub_b.source)
        
        # Connecting B -> A2
        self.edges[1].connect(self.sub_b.sink, self.sub_a2.source)
        
        # Defining source and sink for this block
        self.source = self.sub_a1.source
        self.sink = self.sub_a2.sink

# Overall System Model
# 3 CompositeBlocks in series with global Source and Sink
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating global source and sink
        self.src = Source(env, id="src")
        self.sink_node = Sink(env, id="sink")
        self.add_child_node([self.src, self.sink_node])
        
        # Creating 3 CompositeBlocks
        self.blocks = [CompositeBlock(env, id=f"CompositeBlock[{i}]") for i in range(3)]
        self.add_child_node(self.blocks)
        
        # Creating edges
        # 1 (Src->B0) + 2 (B0->B1, B1->B2) + 1 (B2->Sink) = 4 edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(4)]
        self.add_child_edge(self.edges)
        
        # Connecting Source to first block
        self.edges[0].connect(self.src, self.blocks[0].source)
        
        # Connecting blocks in series
        for i in range(2):
            self.edges[i+1].connect(self.blocks[i].sink, self.blocks[i+1].source)
            
        # Connecting last block to Sink
        self.edges[3].connect(self.blocks[2].sink, self.sink_node)

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