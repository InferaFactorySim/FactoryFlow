"""
Description:
The system is a 100 *100 grid. It consists of 100 independent production lines arranged in parallel. Each production line contains 100 machines connected in strict series, with a source at the beginning and a sink at the end. There is inter row connection between machines of adjacent rows. Source and sink are not common for all lines.

ASSUMPTIONS:
1. Assumed generic names and hierarchical IDs for the 100 sources, 100 sinks, and 10,000 machines since they were not specified in the description.
2. Assumed exactly one buffer is used for every connection (source to first machine, between machines in series, last machine to sink, and inter-row connections) as the number of buffers was not specified.
3. Used default values for all missing parameters for all components, including machine processing delays, source inter-arrival times, and buffer capacities.
4. Assumed inter-row connections flow directionally from a machine at position j in row i to the corresponding machine at position j in row i+1.
5. Assumed equal splitting of flow for machines with multiple outgoing edges (one to the next machine in the series and one to the adjacent row) by using out_edge_selection = "ROUND_ROBIN".
6. Inferred that a single production line (consisting of its own source, 100 machines in strict series, and its own sink) is a repeated pattern, and assumed the creation of a separate class for this pattern to instantiate the 100 rows in the grid.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class ProductionLine(Node):
    def __init__(self, env, id, n=100):
        super().__init__(env, id)
        
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        self.M = [Machine(env, id=f"M[{i}]", out_edge_selection="ROUND_ROBIN") for i in range(n)]
        self.add_child_node(self.M)
        
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        self.add_child_edge(self.e)
        
        self.e[0].connect(self.src, self.M[0])
        for i in range(n-1):
            self.e[i+1].connect(self.M[i], self.M[i+1])
        self.e[n].connect(self.M[n-1], self.sink)

class SystemModel(Node):
    def __init__(self, env, id, rows=100, machines=100):
        super().__init__(env, id)
        self.num_rows = rows
        self.num_machines = machines
        
        self.lines = [ProductionLine(env, id=f"Line[{i}]", n=self.num_machines) for i in range(self.num_rows)]
        self.add_child_node(self.lines)
        
        self.sources = [line.src for line in self.lines]
        self.sinks = [line.sink for line in self.lines]
        
        self.inter_e = []
        for i in range(self.num_rows - 1):
            inter_e_row = [Buffer(env, id=f"inter_e[{i}][{j}]") for j in range(self.num_machines)]
            self.add_child_edge(inter_e_row)
            for j in range(self.num_machines):
                inter_e_row[j].connect(self.lines[i].M[j], self.lines[i+1].M[j])
            self.inter_e.append(inter_e_row)

env = simpy.Environment()
TOP = SystemModel(env, "TOP", rows=100, machines=100)
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)