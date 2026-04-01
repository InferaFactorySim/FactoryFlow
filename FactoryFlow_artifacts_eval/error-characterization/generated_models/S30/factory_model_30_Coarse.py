"""
ModelDescription:
A production line has 4 machines in series and a subsystem . The subsystem consists of 3 machines(M1,M2,M3) in series. In the production line the subsystem is repeated 3 times between the 2nd machine and the 4th machine. All machines have processing delay of 3.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description where available.
2. Added a `Source` node at the start and a `Sink` node at the end of the production line as they were not specified.
3. Inferred the names `Main_M1`, `Main_M2`, `Main_M3`, and `Main_M4` for the 4 machines in the main production line.
4. Defined a class `Subsystem` for the repeated pattern of 3 machines (`M1`, `M2`, `M3`) in series.
5. Assumed the 3 repeated subsystems are connected in parallel.
6. Assumed the parallel subsystems are inserted specifically between `Main_M2` (2nd machine) and `Main_M3` (3rd machine), which satisfies the condition of being between the 2nd and 4th machines while maintaining the series of 4 main machines.
7. Used default edge type `Buffer` for all connections between nodes.
8. Used a single buffer for every connection between machines/nodes.
9. Used default values for all missing parameters (inter-arrival time, buffer capacity) for all components.
10. Assumed `out_edge_selection="ROUND_ROBIN"` for `Main_M2` to split flow equally among the 3 parallel subsystems.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # 3 machines in series: M1, M2, M3
        self.machines = [Machine(env, id=f"{id}_M{i+1}", processing_delay=3) for i in range(3)]
        self.add_child_node(self.machines)
        
        self.edges = []
        for i in range(2):
            edge = Buffer(env, id=f"{id}_edge[{i}]")
            self.add_child_edge(edge)
            edge.connect(self.machines[i], self.machines[i+1])
            self.edges.append(edge)
            
        self.entry = self.machines[0]
        self.exit = self.machines[-1]

class ProductionLine(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="Source")
        self.add_child_node(self.source)
        
        # Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Main Line Machines
        # Main_M2 has round robin selection to split flow to parallel subsystems
        self.main_m1 = Machine(env, id="Main_M1", processing_delay=3)
        self.main_m2 = Machine(env, id="Main_M2", processing_delay=3, out_edge_selection="ROUND_ROBIN")
        self.main_m3 = Machine(env, id="Main_M3", processing_delay=3)
        self.main_m4 = Machine(env, id="Main_M4", processing_delay=3)
        
        self.main_machines = [self.main_m1, self.main_m2, self.main_m3, self.main_m4]
        self.add_child_node(self.main_machines)
        
        # 3 Parallel Subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem[{i}]") for i in range(3)]
        self.add_child_node(self.subsystems)
        
        # Edges
        
        # Source -> Main_M1
        self.edge_src = Buffer(env, id="edge_src")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.source, self.main_m1)
        
        # Main_M1 -> Main_M2
        self.edge_m1_m2 = Buffer(env, id="edge_m1_m2")
        self.add_child_edge(self.edge_m1_m2)
        self.edge_m1_m2.connect(self.main_m1, self.main_m2)
        
        # Main_M2 -> Subsystems (Fan-out)
        self.edges_fan_out = [Buffer(env, id=f"edge_fan_out[{i}]") for i in range(3)]
        self.add_child_edge(self.edges_fan_out)
        for i in range(3):
            self.edges_fan_out[i].connect(self.main_m2, self.subsystems[i].entry)
            
        # Subsystems -> Main_M3 (Fan-in)
        self.edges_fan_in = [Buffer(env, id=f"edge_fan_in[{i}]") for i in range(3)]
        self.add_child_edge(self.edges_fan_in)
        for i in range(3):
            self.edges_fan_in[i].connect(self.subsystems[i].exit, self.main_m3)
            
        # Main_M3 -> Main_M4
        self.edge_m3_m4 = Buffer(env, id="edge_m3_m4")
        self.add_child_edge(self.edge_m3_m4)
        self.edge_m3_m4.connect(self.main_m3, self.main_m4)
        
        # Main_M4 -> Sink
        self.edge_sink = Buffer(env, id="edge_sink")
        self.add_child_edge(self.edge_sink)
        self.edge_sink.connect(self.main_m4, self.sink)

# Initializing simpy environment
env = simpy.Environment()
# Creating the production line system
TOP = ProductionLine(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)