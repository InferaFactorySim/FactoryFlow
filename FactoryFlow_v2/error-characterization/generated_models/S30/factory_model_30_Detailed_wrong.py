"""
ModelDescription:
A production line has 4 machines ID=Main_M[i],where i=0,1,2,.. in series and a subsystem . The subsystem consists of 3 machines(M1,M2,M3) in series. In the production line the subsystem is repeated 3 times between the 2nd machine and the 4th machine. All machines have processing delay of 3. All buffers have ID=Bi , i =1,2,3,..

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Main_M, M1, M2, M3).
2. Added a Source node (id='src') connected to the first machine (Main_M[0]) and a Sink node (id='sink') connected to the last machine (Main_M[3]) to complete the system flow.
3. The 3 repeated subsystems are assumed to be connected in parallel between Main_M[1] and Main_M[3].
4. Main_M[2] is assumed to be excluded from the flow path, as the subsystems are inserted between the 2nd (Main_M[1]) and 4th (Main_M[3]) machines.
5. Within each subsystem, the machines M1, M2, and M3 are connected in series (M1 -> M2 -> M3).
6. Used a single buffer (with ID format Bi) for every connection between nodes (Source-Machine, Machine-Machine, Machine-Sink).
7. Used default values for source inter-arrival time and buffer capacities as they were not specified.
8. Used default edge type 'Buffer' for all connections.
9. Assumed Round Robin routing logic for splitting the flow from Main_M[1] into the 3 parallel subsystems.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the Subsystem class: 3 machines in series (M1 -> M2 -> M3)
class Subsystem(Node):
    def __init__(self, env, id, buffer_counter):
        super().__init__(env, id)
        
        # Creating 3 machines M1, M2, M3 with processing delay of 3
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=3) for i in range(3)]
        self.add_child_node(self.M)
        
        # Creating buffers to connect machines in series
        self.edges = []
        for i in range(2):
            # Generating Buffer ID Bi
            b_id = f"B{buffer_counter[0]}"
            buffer_counter[0] += 1
            
            buf = Buffer(env, id=b_id)
            self.add_child_edge(buf)
            buf.connect(self.M[i], self.M[i+1])
            self.edges.append(buf)

# Defining the main System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Shared counter for Buffer IDs to ensure unique Bi IDs across the system
        self.buffer_counter = [1]
        
        # Initializing Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing Main Machines Main_M[0] to Main_M[3] with processing delay of 3
        self.Main_M = [Machine(env, id=f"Main_M[{i}]", processing_delay=3) for i in range(4)]
        self.add_child_node(self.Main_M)
        
        # Initializing Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating 3 repeated Subsystems
        self.subsystems = [Subsystem(env, id=f"Subsystem[{i}]", buffer_counter=self.buffer_counter) for i in range(3)]
        self.add_child_node(self.subsystems)
        
        # Creating Edges
        self.edges = []
        
        # Connect Source to Main_M[0]
        b_src = Buffer(env, id=f"B{self.buffer_counter[0]}")
        self.buffer_counter[0] += 1
        self.add_child_edge(b_src)
        b_src.connect(self.src, self.Main_M[0])
        self.edges.append(b_src)
        
        # Connect Main_M[0] to Main_M[1]
        b_m0_m1 = Buffer(env, id=f"B{self.buffer_counter[0]}")
        self.buffer_counter[0] += 1
        self.add_child_edge(b_m0_m1)
        b_m0_m1.connect(self.Main_M[0], self.Main_M[1])
        self.edges.append(b_m0_m1)
        
        # Connect Main_M[1] to the 3 Subsystems in parallel, and Subsystems to Main_M[3]
        # Main_M[2] is excluded from the flow path as per assumptions
        for i in range(3):
            # Connect Main_M[1] to first machine of Subsystem (M1)
            b_in = Buffer(env, id=f"B{self.buffer_counter[0]}")
            self.buffer_counter[0] += 1
            self.add_child_edge(b_in)
            b_in.connect(self.Main_M[1], self.subsystems[i].M[0])
            self.edges.append(b_in)
            
            # Connect last machine of Subsystem (M3) to Main_M[3]
            b_out = Buffer(env, id=f"B{self.buffer_counter[0]}")
            self.buffer_counter[0] += 1
            self.add_child_edge(b_out)
            b_out.connect(self.subsystems[i].M[2], self.Main_M[3])
            self.edges.append(b_out)
            
        # Connect Main_M[3] to Sink
        b_sink = Buffer(env, id=f"B{self.buffer_counter[0]}")
        self.buffer_counter[0] += 1
        self.add_child_edge(b_sink)
        b_sink.connect(self.Main_M[3], self.sink)
        self.edges.append(b_sink)

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