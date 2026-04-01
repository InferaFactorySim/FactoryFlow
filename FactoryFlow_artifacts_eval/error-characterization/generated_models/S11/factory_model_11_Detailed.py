"""
ModelDescription:
Source_1 (rate 10s) and Source_2 (rate 10s) feed into Machine_M1 and Machine_M2 respectively via buffers Buffer_src1 and Buffer_src2, of capacity 2. M1 and M2 both output into Buffer_Join1 and Buffer_Join2 (capacity 10). Both Buffer_Joins  feeds a final Machine_M3 (delay 4.0s) which connects to Sink via a buffer Buffer_main_sink. All machines have a processing_Delay of 2 and buffers have a capacity of 2. The work_capacity of machine_M3 is 2.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. The final sink node is assigned the ID "Sink".
3. The "rate 10s" specified for Source_1 and Source_2 is assumed to represent an `inter_arrival_time` of 10.
4. Buffer_main_sink is assumed to have a capacity of 2, following the general rule provided in the description for buffers not explicitly assigned a capacity of 10.
5. Machine_M3 is modeled as a standard Machine node that accepts inputs from multiple buffers (Buffer_Join1 and Buffer_Join2) to act as a merge point.
6. A single buffer is used for each connection, corresponding to the specific buffer names provided in the description.
7. The system is implemented as a single SystemModel class without creating sub-classes for the input branches, as the nodes have unique, non-sequential identifiers.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # Initializing sources
        # Source_1 and Source_2 with inter_arrival_time 10
        self.sources = [Source(env, id=f"Source_{i+1}", inter_arrival_time=10) for i in range(2)]
        self.add_child_node(self.sources)

        # Initializing machines M1 and M2
        # Processing delay 2
        self.machines = [Machine(env, id=f"Machine_M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.machines)

        # Initializing machine M3
        # Delay 4.0s, work_capacity 2
        self.m3 = Machine(env, id="Machine_M3", processing_delay=4.0, work_capacity=2)
        self.add_child_node(self.m3)

        # Initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)

        # Initializing buffers from sources to machines
        # Buffer_src1 and Buffer_src2, capacity 2
        self.buffers_src = [Buffer(env, id=f"Buffer_src{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.buffers_src)

        # Initializing buffers from machines to M3
        # Buffer_Join1 and Buffer_Join2, capacity 10
        self.buffers_join = [Buffer(env, id=f"Buffer_Join{i+1}", capacity=10) for i in range(2)]
        self.add_child_edge(self.buffers_join)

        # Initializing buffer from M3 to sink
        # Buffer_main_sink, capacity 2 (Assumption 4)
        self.b_main_sink = Buffer(env, id="Buffer_main_sink", capacity=2)
        self.add_child_edge(self.b_main_sink)

        # Connecting nodes
        for i in range(2):
            # Source -> Buffer -> Machine
            self.buffers_src[i].connect(self.sources[i], self.machines[i])
            # Machine -> Buffer -> M3
            self.buffers_join[i].connect(self.machines[i], self.m3)
        
        # M3 -> Buffer -> Sink
        self.b_main_sink.connect(self.m3, self.sink)

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