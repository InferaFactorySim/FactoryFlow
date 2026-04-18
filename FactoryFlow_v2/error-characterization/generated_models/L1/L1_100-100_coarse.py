"""
Description:
The system consists of 100 independent production lines arranged in parallel. Each production line contains 100 machines connected in strict series, with a single source at the beginning and a single sink at the end. Source and sink are common for all lines

ASSUMPTIONS:
1. Inferred a repeated pattern of 100 machines connected in strict series; assumed a custom class will be created to represent a single production line and instantiated 100 times in parallel.
2. Node names and machine IDs were not specified in the description and have been logically inferred.
3. Assumed exactly 1 buffer is used for every connection between nodes (from the common source to the first machine of each line, between machines within the lines, and from the last machine of each line to the common sink) as the number of buffers was not specified.
4. Used default values for all missing parameters for all components, including machine processing delays, buffer capacities, and source inter-arrival times.
5. Assumed out_edge_selection is set to ROUND_ROBIN to equally distribute items from the single common source to the 100 parallel production lines, as split ratios were not specified.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class ProductionLine(Node):
    def __init__(self, env, id, num_machines=100):
        super().__init__(env, id)
        
        self.M = [Machine(env, id=f"M[{i}]") for i in range(num_machines)]
        self.add_child_node(self.M)
        
        self.e = [Buffer(env, id=f"edge[{i}]") for i in range(num_machines - 1)]
        self.add_child_edge(self.e)
        
        for i in range(num_machines - 1):
            self.e[i].connect(self.M[i], self.M[i+1])
            
        self.entry = self.M[0]
        self.exit = self.M[-1]

class SystemModel(Node):
    def __init__(self, env, id, num_lines=100):
        super().__init__(env, id)
        
        self.source = Source(env, id="src", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.source)
        
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        self.lines = [ProductionLine(env, id=f"Line[{i}]", num_machines=100) for i in range(num_lines)]
        self.add_child_node(self.lines)
        
        self.src_edges = [Buffer(env, id=f"src_edge[{i}]") for i in range(num_lines)]
        self.add_child_edge(self.src_edges)
        
        self.sink_edges = [Buffer(env, id=f"sink_edge[{i}]") for i in range(num_lines)]
        self.add_child_edge(self.sink_edges)
        
        for i in range(num_lines):
            self.src_edges[i].connect(self.source, self.lines[i].entry)
            self.sink_edges[i].connect(self.lines[i].exit, self.sink)

env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)