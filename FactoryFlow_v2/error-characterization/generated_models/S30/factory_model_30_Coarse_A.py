"""
ModelDescription:
A production line has 4 machines in series and a subsystem . The subsystem consists of 3 machines(IDs are M1,M2,M3) in series. In the production line the subsystem is repeated 3 times between the 2nd machine and the 4th machine. All machines have processing delay of 3.  Buffer ID is Bi where i =1,2,3,.. where ID is not provided.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. Added a Source node named 'src' at the start and a Sink node named 'sink' at the end of the system as they were not specified.
3. Named the 4 machines in the main production line as `Main_M[0]`, `Main_M[1]`, `Main_M[2]`, and `Main_M[3]`.
4. Inferred that "repeated 3 times" implies the 3 subsystems are connected in parallel.
5. Inferred a repeated pattern for the subsystem and assumed a class named `Subsystem` will be created, containing machines M1, M2, and M3 connected in series.
6. Assumed the flow logic is: Source -> `Main_M[0]` -> `Main_M[1]` -> Main_M[2] -> `Main_M[3]` -> Sink.
and  `Main_M[1]` -> [3 Parallel Subsystems] -> `Main_M[3]` .
8. Used default edge type `Buffer` for all connections between nodes as edge type was not specified.
9. Used a single Buffer between every connected pair of nodes.
10. Assumed `Main_M[1]` uses a Round Robin strategy (out_edge_selection) to distribute parts to the 3 parallel subsystems.
11. Used default values for source inter-arrival time, buffer capacities, and all other missing parameters.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Global counter for buffer IDs to satisfy "Bi" naming convention
buffer_idx = 1

def get_buffer_id():
    global buffer_idx
    bid = f"B{buffer_idx}"
    buffer_idx += 1
    return bid

class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 3 machines in series with IDs M1, M2, M3
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=3) for i in range(3)]
        self.add_child_node(self.machines)
        
        # Creating buffers between machines in the subsystem
        self.edges = []
        for i in range(2):
            b = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b)
            b.connect(self.machines[i], self.machines[i+1])
            self.edges.append(b)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Creating Main Line Machines (Main_M[0] to Main_M[3])
        # Main_M[1] uses Round Robin (out_edge_selection=1) to distribute parts
        self.main_machines = []
        for i in range(4):
            selection = 1 if i == 1 else 0
            m = Machine(env, id=f"Main_M[{i}]", processing_delay=3, out_edge_selection=selection)
            self.main_machines.append(m)
        self.add_child_node(self.main_machines)
        
        # Creating Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating 3 Parallel Subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem[{i}]") for i in range(3)]
        self.add_child_node(self.subsystems)
        
        # Connecting Main Line Sequence
        # Source -> Main_M[0]
        b = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b)
        b.connect(self.src, self.main_machines[0])
        
        # Main_M[0] -> Main_M[1]
        b = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b)
        b.connect(self.main_machines[0], self.main_machines[1])
        
        # Main_M[1] -> Main_M[2]
        b = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b)
        b.connect(self.main_machines[1], self.main_machines[2])
        
        # Main_M[2] -> Main_M[3]
        b = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b)
        b.connect(self.main_machines[2], self.main_machines[3])
        
        # Main_M[3] -> Sink
        b = Buffer(env, id=get_buffer_id())
        self.add_child_edge(b)
        b.connect(self.main_machines[3], self.sink)
        
        # Connecting Subsystems in Parallel between Main_M[1] and Main_M[3]
        for sub in self.subsystems:
            # Main_M[1] -> Subsystem Start (M1)
            b_in = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b_in)
            b_in.connect(self.main_machines[1], sub.machines[0])
            
            # Subsystem End (M3) -> Main_M[3]
            b_out = Buffer(env, id=get_buffer_id())
            self.add_child_edge(b_out)
            b_out.connect(sub.machines[-1], self.main_machines[3])

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)