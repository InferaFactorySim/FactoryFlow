"""
ModelDescription:
A system with 2 nodes interconnected. One node has 2 machines in parallel  and the second one has 2 machines in series . The output of the last node is fed to first machine in node1.  The system has a common source. All buffer IDs are B1, B2, B3, etc.  in all classes.

 MODEL ASSUMPTIONS:
1. Named the top-level system node `SystemModel`.
2. Inferred two custom node classes: `ParallelNode` (for Node 1) and `SeriesNode` (for Node 2) to represent the distinct internal structures described.
3. Inferred `ParallelNode` contains 2 machines named `M1` and `M2`.
4. Inferred `SeriesNode` contains 2 machines named `M1` and `M2`.
5. Used default edge type `Buffer` for all connections between machines and nodes.
6. Used a single `Buffer` for every connection between components as the number of buffers was not specified.
7. Inferred a `Source` named `src` and connected it to both machines (`M1` and `M2`) in `ParallelNode` via separate buffers to establish the parallel flow.
8. Inferred a `Sink` named `sink` connected to the last machine (`M2`) of `SeriesNode` to allow entities to exit the system, as a source-fed system with only a feedback loop would be invalid.
9. Connected the outputs of both machines in `ParallelNode` to the first machine (`M1`) of `SeriesNode`.
10. Connected the first machine (`M1`) of `SeriesNode` to the second machine (`M2`) of `SeriesNode` to form the series sequence.
11. Connected the output of the last machine (`M2`) in `SeriesNode` to the first machine (`M1`) of `ParallelNode` using a buffer to satisfy the feedback loop description.
12. Used default values for all missing parameters (processing delays, buffer capacities, inter-arrival times) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class ParallelNode(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Inferred ParallelNode contains 2 machines named M1 and M2
        self.M1 = Machine(env, id="M1")
        self.M2 = Machine(env, id="M2")
        self.add_child_node([self.M1, self.M2])

class SeriesNode(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Inferred SeriesNode contains 2 machines named M1 and M2
        self.M1 = Machine(env, id="M1")
        self.M2 = Machine(env, id="M2")
        self.add_child_node([self.M1, self.M2])
        
        # Connected the first machine (M1) of SeriesNode to the second machine (M2)
        self.edge = Buffer(env, id="B1")
        self.add_child_edge(self.edge)
        self.edge.connect(self.M1, self.M2)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Inferred a Source named src
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Inferred two custom node classes: ParallelNode and SeriesNode
        self.node1 = ParallelNode(env, id="TypeA")
        self.node2 = SeriesNode(env, id="TypeB")
        self.add_child_node([self.node1, self.node2])
        
        # Inferred a Sink named sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating buffers B1 to B6 for system connections
        self.buffers = [Buffer(env, id=f"B{i+1}") for i in range(6)]
        self.add_child_edge(self.buffers)
        
        # Connected src to both machines (M1 and M2) in ParallelNode
        self.buffers[0].connect(self.src, self.node1.M1)
        self.buffers[1].connect(self.src, self.node1.M2)
        
        # Connected the outputs of both machines in ParallelNode to the first machine (M1) of SeriesNode
        self.buffers[2].connect(self.node1.M1, self.node2.M1)
        self.buffers[3].connect(self.node1.M2, self.node2.M1)
        
        # Connected the output of the last machine (M2) in SeriesNode to Sink
        self.buffers[4].connect(self.node2.M2, self.sink)
        
        # Connected the output of the last machine (M2) in SeriesNode to the first machine (M1) of ParallelNode (Feedback)
        self.buffers[5].connect(self.node2.M2, self.node1.M1)

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