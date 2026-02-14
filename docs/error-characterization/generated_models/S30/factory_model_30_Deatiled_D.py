"""
ModelDescription:
A production line has 4 machines ID=Main_M[i],where i=0,1,2,.. in series and a subsystem . The subsystem consists of 3 machines(M1,M2,M3) in series. In the production line the subsystem is repeated 3 times between the 2nd machine and the 4th machine. All machines have processing delay of 3. All buffers have ID=Bi , i =1,2,3,..


 MODEL ASSUMPTIONS:
1. Added a Source node named "Source" connected to the first machine (`Main_M[0]`), and `Main_M[0]`, `Main_M[1]`, `Main_M[2]` and `Main_M[3]`are connected in series and a Sink node named "Sink" connected to the last machine (`Main_M[3]`) to complete the flow.
2. Inferred a reusable class structure for the "Subsystem" which contains machines `M1`, `M2`, and `M3` connected in series.
3. Interpreted "repeated 3 times between the 2nd machine and the 4th machine" as 3 instances of the Subsystem connected in parallel between `Main_M[1]` and `Main_M[3]`.

5. Used a single `Buffer` for every connection between nodes (between Source/Machines, Machines/Subsystems, and inside Subsystems).
6. Assumed `Main_M[1]` uses Round Robin logic (default `out_edge_selection`) to split the flow equally among the 3 parallel subsystems.
7. Used default values for Source inter-arrival time and Buffer capacities as they were not specified.
8. Node names and Types are chosen according to users description.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Global counter to ensure unique Buffer IDs (Bi) across the entire system
buffer_counter = 1

def get_buffer_id():
    global buffer_counter
    bid = f"B{buffer_counter}"
    buffer_counter += 1
    return bid

class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # 3 machines M1, M2, M3 in series with processing delay of 3
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=3) for i in range(3)]
        self.add_child_node(self.machines)
        
        self.edges = []
        # Connect M1 -> M2 and M2 -> M3
        for i in range(2):
            buf = Buffer(env, id=get_buffer_id())
            self.add_child_edge(buf)
            buf.connect(self.machines[i], self.machines[i+1])
            self.edges.append(buf)
            
        # Expose entry and exit points
        self.entry = self.machines[0]
        self.exit = self.machines[-1]

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="Source")
        self.add_child_node(self.source)
        
        # Main Line Machines: Main_M[0] to Main_M[3]
        self.main_machines = [Machine(env, id=f"Main_M[{i}]", processing_delay=3) for i in range(4)]
        self.add_child_node(self.main_machines)
        
        # Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # 3 Subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem_{i}") for i in range(3)]
        self.add_child_node(self.subsystems)
        
        self.edges = []
        
        # Connect Source -> Main_M[0]
        b_src = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b_src)
        b_src.connect(self.source, self.main_machines[0])
        self.edges.append(b_src)
        
        # Connect Main Line in Series: M0->M1->M2->M3
        for i in range(3):
            b = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b)
            b.connect(self.main_machines[i], self.main_machines[i+1])
            self.edges.append(b)
            
        # Connect Main_M[3] -> Sink
        b_sink = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b_sink)
        b_sink.connect(self.main_machines[3], self.sink)
        self.edges.append(b_sink)
        
        # Connect Subsystems in parallel between Main_M[1] (2nd machine) and Main_M[3] (4th machine)
        for sub in self.subsystems:
            # From Main_M[1] to Subsystem Entry
            b_in = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b_in)
            b_in.connect(self.main_machines[1], sub.entry)
            self.edges.append(b_in)
            
            # From Subsystem Exit to Main_M[3]
            b_out = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b_out)
            b_out.connect(sub.exit, self.main_machines[3])
            self.edges.append(b_out)

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