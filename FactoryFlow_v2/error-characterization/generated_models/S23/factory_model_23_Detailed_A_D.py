"""
ModelDescription:
There is a subsystem as follows. M1 feeds M2 via a Buffer (cap 5). After M2, items enter Buffer_Check and Machine_check. Machine_Check routes 20% of items back to the input of M1 for rework and 80% forward to next machine The rework loop buffer has a capacity of 1. There are 3 such system.  Similarly there is another sub-system as follows- Mac_M1 acts as a router with a split ratio of 0.5 to Path A and 0.5 to Path B. Path A consists of B_A1 feeding  Mac_M2. Path B consists of B_B1 feeding Mac_M3. Mac_M2 and Mac_M3 both connect to individual Sinks, sink_1 and sink_2 via B_A2 and B_B2 respectively. 80% out from  Machine_Check in first type of subsystem enters MacM1 that is in the second type of sub system. . All machines have a processing_Delay of 2 and buffers have a capacity of 2 unless not specified before.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. There is a source src inside every subsystem. all buffers  have ID as Bi ,i=1,2,3.. in all classes 

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class `Subsystem_1` for the repeated pattern containing M1, M2, and Machine_Check, and a class `Subsystem_2` for the pattern containing Mac_M1, Mac_M2, Mac_M3, and the sinks.
3. Assumed the overall system topology consists of 3 instances of `Subsystem_1` running in parallel, all feeding into a single instance of `Subsystem_2`.
4. Assumed a Source `src` in each"subsystem_1" and it connects to the input of `M1` in each of the 3 `Subsystem_1` instances via separate buffers.
5. Assumed the 80% forward output from `Machine_Check` in each of the 3 `Subsystem_1` instances connects to the input of `Mac_M1` in `Subsystem_2` via separate buffers.
6. Interpreted `Buffer_Check` as the specific buffer connecting `M2` to `Machine_Check`, and `B_A1`, `B_B1`, `B_A2`, `B_B2` as specific buffers connecting their respective machines.
7. Used default edge type `Buffer` for all connections where edge type was not specified for connecting Machine_Check to Mac_M1. ID of that buffer will be Bi , i=1,2,3..
8. Used a single buffer for all connections between nodes where the number of buffers was not specified.
9. Used default capacity of 2 for all buffers where capacity was not specified in the description.
10. Assumed `Mac_M1` and `Machine_Check` are nodes of type `Machine` out_edge_selection = "ROUND_ROBIN"
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
        
        # initializing source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing machines
        # M1 has multiple inputs (src and rework), so work_capacity=2
        self.M1 = Machine(env, id="M1", processing_delay=2, work_capacity=2)
        self.M2 = Machine(env, id="M2", processing_delay=2)
        # Machine_Check routes items, assumed ROUND_ROBIN
        self.Machine_Check = Machine(env, id="Machine_Check", processing_delay=2, out_edge_selection="ROUND_ROBIN")
        
        self.add_child_node([self.M1, self.M2, self.Machine_Check])
        
        # initializing buffers
        # src to M1, ID B1
        self.B1 = Buffer(env, id="B1", capacity=2)
        # M1 to M2, ID B2, capacity 5
        self.B2 = Buffer(env, id="B2", capacity=5)
        # M2 to Machine_Check, ID Buffer_Check
        self.Buffer_Check = Buffer(env, id="Buffer_Check", capacity=2)
        # Machine_Check to M1 (rework), ID B3, capacity 1
        self.B3 = Buffer(env, id="B3", capacity=1)
        
        self.add_child_edge([self.B1, self.B2, self.Buffer_Check, self.B3])
        
        # connecting nodes
        self.B1.connect(self.src, self.M1)
        self.B2.connect(self.M1, self.M2)
        self.Buffer_Check.connect(self.M2, self.Machine_Check)
        self.B3.connect(self.Machine_Check, self.M1)
        
        # Expose exit node for connection to next subsystem
        self.exit = self.Machine_Check

# defining Subsystem_2
class Subsystem_2(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing machines
        # Mac_M1 acts as router, inputs from 3 subsystems, work_capacity=2
        self.Mac_M1 = Machine(env, id="Mac_M1", processing_delay=2, work_capacity=2, out_edge_selection="ROUND_ROBIN")
        self.Mac_M2 = Machine(env, id="Mac_M2", processing_delay=2)
        self.Mac_M3 = Machine(env, id="Mac_M3", processing_delay=2)
        
        self.add_child_node([self.Mac_M1, self.Mac_M2, self.Mac_M3])
        
        # initializing sinks
        self.sink_1 = Sink(env, id="sink_1")
        self.sink_2 = Sink(env, id="sink_2")
        self.add_child_node([self.sink_1, self.sink_2])
        self.sinks = [self.sink_1, self.sink_2]
        
        # initializing buffers
        self.B_A1 = Buffer(env, id="B_A1", capacity=2)
        self.B_A2 = Buffer(env, id="B_A2", capacity=2)
        self.B_B1 = Buffer(env, id="B_B1", capacity=2)
        self.B_B2 = Buffer(env, id="B_B2", capacity=2)
        
        self.add_child_edge([self.B_A1, self.B_A2, self.B_B1, self.B_B2])
        
        # connecting nodes
        # Path A
        self.B_A1.connect(self.Mac_M1, self.Mac_M2)
        self.B_A2.connect(self.Mac_M2, self.sink_1)
        
        # Path B
        self.B_B1.connect(self.Mac_M1, self.Mac_M3)
        self.B_B2.connect(self.Mac_M3, self.sink_2)
        
        # Expose entry node
        self.entry = self.Mac_M1

# defining the overall SystemModel
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 3 instances of Subsystem_1
        self.sub1 = [Subsystem_1(env, id=f"Subsystem_1[{i}]") for i in range(3)]
        self.add_child_node(self.sub1)
        
        # creating 1 instance of Subsystem_2
        self.sub2 = Subsystem_2(env, id="Subsystem_2")
        self.add_child_node(self.sub2)
        
        # creating edges to connect Subsystem_1 instances to Subsystem_2
        self.inter_edges = []
        for i in range(3):
            # ID Bi, i=1,2,3
            buf = Buffer(env, id=f"B{i+1}", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.sub1[i].exit, self.sub2.entry)
            self.inter_edges.append(buf)

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