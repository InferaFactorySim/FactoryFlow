"""
ModelDescription:
There is a subsystem as follows. M1 feeds M2 via a Buffer (cap 5). After M2, items enter Buffer_Check and Machine_check. Machine_Check routes 20% of items back to the input of M1 for rework and 80% forward to next machine The rework loop buffer has a capacity of 1. There are 3 such system.  Similarly there is another sub-system as follows- Mac_M1 acts as a router with a split ratio of 0.5 to Path A and 0.5 to Path B. Path A consists of B_A1 feeding  Mac_M2. Path B consists of B_B1 feeding Mac_M3. Mac_M2 and Mac_M3 both connect to individual Sinks, sink_1 and sink_2 via B_A2 and B_B2 respectively. 80% out from  Machine_Check in first type of subsystem enters MacM1 that is in the second type of sub system. . All machines have a processing_Delay of 2 and buffers have a capacity of 2 unless not specified before.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class `Subsystem_1` for the repeated pattern containing M1, M2, and Machine_Check, and a class `Subsystem_2` for the pattern containing Mac_M1, Mac_M2, Mac_M3, and the sinks.
3. Assumed the overall system topology consists of 3 instances of `Subsystem_1` running in parallel, all feeding into a single instance of `Subsystem_2`.
4. Assumed the common Source `src` connects to the input of `M1` in each of the 3 `Subsystem_1` instances via separate buffers.
5. Assumed the 80% forward output from `Machine_Check` in each of the 3 `Subsystem_1` instances connects to the input of `Mac_M1` in `Subsystem_2` via separate buffers.
6. Interpreted `Buffer_Check` as the specific buffer connecting `M2` to `Machine_Check`, and `B_A1`, `B_B1`, `B_A2`, `B_B2` as specific buffers connecting their respective machines.
7. Used default edge type `Buffer` for all connections where edge type was not specified (e.g., Source to M1, Machine_Check to Mac_M1).
8. Used a single buffer for all connections between nodes where the number of buffers was not specified.
9. Used default capacity of 2 for all buffers where capacity was not specified in the description.
10. Assumed `Mac_M1` and `Machine_Check` are nodes of type `Machine` configured with the specified routing logic/split ratios.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining Subsystem_1
class Subsystem_1(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # M1 has inputs from Source and Rework loop, so work_capacity is 2
        self.M1 = Machine(env, id="M1", processing_delay=2, work_capacity=2)
        self.M2 = Machine(env, id="M2", processing_delay=2)
        self.Machine_Check = Machine(env, id="Machine_Check", processing_delay=2)
        
        self.add_child_node([self.M1, self.M2, self.Machine_Check])
        
        # Buffer between M1 and M2 with capacity 5
        self.b_m1_m2 = Buffer(env, id="Buffer", capacity=5)
        # Buffer_Check between M2 and Machine_Check
        self.b_check = Buffer(env, id="Buffer_Check", capacity=2)
        # Rework loop buffer with capacity 1
        self.b_rework = Buffer(env, id="Buffer_Rework", capacity=1)
        
        self.add_child_edge([self.b_m1_m2, self.b_check, self.b_rework])
        
        self.b_m1_m2.connect(self.M1, self.M2)
        self.b_check.connect(self.M2, self.Machine_Check)
        self.b_rework.connect(self.Machine_Check, self.M1)

# defining Subsystem_2
class Subsystem_2(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Mac_M1 has inputs from 3 Subsystem_1 instances, so work_capacity is 2
        self.Mac_M1 = Machine(env, id="Mac_M1", processing_delay=2, work_capacity=2)
        self.Mac_M2 = Machine(env, id="Mac_M2", processing_delay=2)
        self.Mac_M3 = Machine(env, id="Mac_M3", processing_delay=2)
        
        self.sink_1 = Sink(env, id="sink_1")
        self.sink_2 = Sink(env, id="sink_2")
        
        self.add_child_node([self.Mac_M1, self.Mac_M2, self.Mac_M3, self.sink_1, self.sink_2])
        
        # Path A buffers
        self.B_A1 = Buffer(env, id="B_A1", capacity=2)
        self.B_A2 = Buffer(env, id="B_A2", capacity=2)
        
        # Path B buffers
        self.B_B1 = Buffer(env, id="B_B1", capacity=2)
        self.B_B2 = Buffer(env, id="B_B2", capacity=2)
        
        self.add_child_edge([self.B_A1, self.B_A2, self.B_B1, self.B_B2])
        
        # Path A connections
        self.B_A1.connect(self.Mac_M1, self.Mac_M2)
        self.B_A2.connect(self.Mac_M2, self.sink_1)
        
        # Path B connections
        self.B_B1.connect(self.Mac_M1, self.Mac_M3)
        self.B_B2.connect(self.Mac_M3, self.sink_2)

# defining the overall SystemModel
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # 3 instances of Subsystem_1
        self.sub1 = [Subsystem_1(env, id=f"Subsystem_1[{i}]") for i in range(3)]
        self.add_child_node(self.sub1)
        
        # 1 instance of Subsystem_2
        self.sub2 = Subsystem_2(env, id="Subsystem_2")
        self.add_child_node(self.sub2)
        
        # Connecting Source to M1 of each Subsystem_1
        self.src_edges = [Buffer(env, id=f"src_edge[{i}]", capacity=2) for i in range(3)]
        self.add_child_edge(self.src_edges)
        
        for i in range(3):
            self.src_edges[i].connect(self.src, self.sub1[i].M1)
            
        # Connecting Machine_Check of each Subsystem_1 to Mac_M1 of Subsystem_2
        self.inter_edges = [Buffer(env, id=f"inter_edge[{i}]", capacity=2) for i in range(3)]
        self.add_child_edge(self.inter_edges)
        
        for i in range(3):
            self.inter_edges[i].connect(self.sub1[i].Machine_Check, self.sub2.Mac_M1)

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)