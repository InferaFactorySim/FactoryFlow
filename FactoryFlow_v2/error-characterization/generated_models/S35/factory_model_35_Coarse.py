"""
ModelDescription:
A systemA with  machine that splits into 10 machines  and the output from these machines ends in another a machine. There are 5 such systems that are connected in series .  There is another systemB with 10 machines in series and there are 5 such systems. the last machine in systemA is connected to the first machines in each row in systemB

 MODEL ASSUMPTIONS:
1. Inferred two reusable class definitions based on repeated patterns: "SystemA_Block" (consisting of 1 split machine, 10 parallel machines, and 1 merge machine) and "SystemB_Row" (consisting of 10 machines in series).
2. Added a Source node "src" connected to the input of the first SystemA block and a Sink node "sink" connected to the outputs of all 5 SystemB rows to complete the simulation flow, as these were not specified.
3. Interpreted the structure of SystemB as 5 parallel rows based on the phrase "connected to the first machines in each row", where each row contains 10 machines in series.
4. Used default edge type Buffer for all connections between machines and subsystems as edge type was not specified.
5. Used a single buffer for every connection between nodes where the number of buffers was not specified.
6. Inferred node names and IDs (e.g., "Split_M", "Parallel_M", "Merge_M" for SystemA; "Series_M" for SystemB) as they were not provided in the description.
7. Assumed out_edge_selection is "ROUND_ROBIN" for the splitting machine in SystemA and for the connection between the last SystemA block and the 5 parallel SystemB rows to ensure equal distribution.
8. Used default values for all missing parameters (processing delays, buffer capacities, inter-arrival times) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Class for SystemA Block: 1 Split Machine -> 10 Parallel Machines -> 1 Merge Machine
class SystemA_Block(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Split Machine with Round Robin selection
        self.split_m = Machine(env, id="Split_M", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.split_m)
        
        # 10 Parallel Machines
        self.parallel_m = [Machine(env, id=f"Parallel_M[{i}]") for i in range(10)]
        self.add_child_node(self.parallel_m)
        
        # Merge Machine
        self.merge_m = Machine(env, id="Merge_M")
        self.add_child_node(self.merge_m)
        
        # Edges from Split Machine to Parallel Machines
        self.edges_split = [Buffer(env, id=f"edge_split[{i}]") for i in range(10)]
        self.add_child_edge(self.edges_split)
        for i in range(10):
            self.edges_split[i].connect(self.split_m, self.parallel_m[i])
            
        # Edges from Parallel Machines to Merge Machine
        self.edges_merge = [Buffer(env, id=f"edge_merge[{i}]") for i in range(10)]
        self.add_child_edge(self.edges_merge)
        for i in range(10):
            self.edges_merge[i].connect(self.parallel_m[i], self.merge_m)
            
        # Expose entry and exit points
        self.entry = self.split_m
        self.exit = self.merge_m

# Class for SystemB Row: 10 Machines in Series
class SystemB_Row(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # 10 Machines in series
        self.series_m = [Machine(env, id=f"Series_M[{i}]") for i in range(10)]
        self.add_child_node(self.series_m)
        
        # Edges connecting machines in series
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(9)]
        self.add_child_edge(self.edges)
        for i in range(9):
            self.edges[i].connect(self.series_m[i], self.series_m[i+1])
            
        # Expose entry and exit points
        self.entry = self.series_m[0]
        self.exit = self.series_m[-1]

# Main System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # 5 SystemA Blocks connected in series
        self.sysA = [SystemA_Block(env, id=f"SysA[{i}]") for i in range(5)]
        self.add_child_node(self.sysA)
        
        # 5 SystemB Rows (parallel)
        self.sysB = [SystemB_Row(env, id=f"SysB[{i}]") for i in range(5)]
        self.add_child_node(self.sysB)
        
        # Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Connect Source to the first SystemA block
        self.e_src = Buffer(env, id="e_src")
        self.add_child_edge(self.e_src)
        self.e_src.connect(self.src, self.sysA[0].entry)
        
        # Connect SystemA blocks in series (SysA[i] -> SysA[i+1])
        self.e_sysA = [Buffer(env, id=f"e_sysA[{i}]") for i in range(4)]
        self.add_child_edge(self.e_sysA)
        for i in range(4):
            self.e_sysA[i].connect(self.sysA[i].exit, self.sysA[i+1].entry)
            
        # Connect the last SystemA block to all 5 SystemB rows
        # Set out_edge_selection to ROUND_ROBIN for the last SystemA block's exit machine
        self.sysA[4].exit.out_edge_selection = "ROUND_ROBIN"
        
        self.e_inter = [Buffer(env, id=f"e_inter[{i}]") for i in range(5)]
        self.add_child_edge(self.e_inter)
        for i in range(5):
            self.e_inter[i].connect(self.sysA[4].exit, self.sysB[i].entry)
            
        # Connect all SystemB rows to the Sink
        self.e_sink = [Buffer(env, id=f"e_sink[{i}]") for i in range(5)]
        self.add_child_edge(self.e_sink)
        for i in range(5):
            self.e_sink[i].connect(self.sysB[i].exit, self.sink)

# Initialize SimPy environment
env = simpy.Environment()
# Create the top-level system
TOP = SystemModel(env, "TOP")
# Fill hierarchical IDs
TOP.fill_hierarchical_id()
# Validate the model
TOP.validate()
# Run the simulation
TOP.run_simulation(25)