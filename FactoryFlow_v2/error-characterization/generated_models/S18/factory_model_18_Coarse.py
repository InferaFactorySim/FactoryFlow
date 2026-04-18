"""
ModelDescription:
A system with 2 nodes interconnected. One node has 2 machines in parallel  and the second one has 2 machines in series . The output of the last node is fed to first machine in node1.  The system has a common source

 MODEL ASSUMPTIONS:
1.  Inferred the top-level system name as "SystemModel".
2.  Inferred two custom node classes to represent the subsystems: "ParallelNode" (Node 1) and "SeriesNode" (Node 2).
3.  Assumed "ParallelNode" contains 2 machines named "M[0]" and "M[1]" and "SeriesNode" contains 2 machines named "M[0]" and "M[1]".
4.  Used default edge type "Buffer" for all connections between nodes and machines as edge type was not specified.
5.  Used a single buffer for every connection between components.
6.  Assumed the "Common Source" connects to the "ParallelNode". Specifically, the Source connects to both "M[0]" and "M[1]" inside "ParallelNode" via buffers to achieve parallel flow without a splitter.
7.  Assumed a forward connection exists where both machines in "ParallelNode" connect to the first machine ("M[0]") of "SeriesNode" via buffers to merge the flow.
8.  Assumed the "first machine in node1" referred to in the feedback loop is "M[0]" of the "ParallelNode".
9.  Assumed a "Sink" node is required and connected it to the output of the last machine in "SeriesNode" to allow entities to exit the system.
10. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
"""

import simpy

#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from factorysimpy.utils.utils import draw_blockdiagram


from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class ParallelNode(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines in parallel
        self.M = [Machine(env, id=f"M[{i}]") for i in range(2)]
        self.add_child_node(self.M)

class SeriesNode(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines in series
        self.M = [Machine(env, id=f"M[{i}]") for i in range(2)]
        self.add_child_node(self.M)
        
        # Creating edge between machines
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(1)]
        self.add_child_edge(self.edges)
        
        # Connecting machines in series
        self.edges[0].connect(self.M[0], self.M[1])

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing subsystems
        self.parallel_node = ParallelNode(env, id="ParallelNode")
        self.add_child_node(self.parallel_node)
        
        self.series_node = SeriesNode(env, id="SeriesNode")
        self.add_child_node(self.series_node)
        
        # Creating edges for system connections
        # 0,1: Source -> ParallelNode
        # 2,3: ParallelNode -> SeriesNode
        # 4: SeriesNode -> Sink
        # 5: SeriesNode -> ParallelNode (Feedback)
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(6)]
        self.add_child_edge(self.edges)
        
        # Connecting Source to ParallelNode machines
        for i in range(2):
            self.edges[i].connect(self.source, self.parallel_node.M[i])
            
        # Connecting ParallelNode machines to SeriesNode first machine
        for i in range(2):
            self.edges[2+i].connect(self.parallel_node.M[i], self.series_node.M[0])
            
        # Connecting SeriesNode last machine to Sink
        self.edges[4].connect(self.series_node.M[1], self.sink)
        
        # Connecting SeriesNode last machine to ParallelNode first machine (Feedback)
        self.edges[5].connect(self.series_node.M[1], self.parallel_node.M[0])

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
fig = draw_blockdiagram(TOP)
path =fig.render(filename="factory_model_18_Coarse",directory=".", format="png", cleanup=True)

TOP.validate()
# Running the simulation
TOP.run_simulation(25)