"""
ModelDescription:
System has 5 machines (M1-M5) in series. M1(delay 1.0, cap 1), M2(2.0, 2), M3(0.5, 5), M4(3.0, 1), M5(1.5, 3). SRC (rate 1.0) feeds M1 via B1. All inter-machine buffers have capacity 2. Ends in SINK. Buffer IDs are B1, B2, B3, etc.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Used Buffer edge type for all connections.
3. Used a single buffer between all connected nodes.
4. Inferred names for the buffers connecting M1 to M2, M2 to M3, M3 to M4, M4 to M5, and M5 to SINK.
5. Assumed the buffer connecting M5 to SINK and buffer B1 have default capacity as they are not strictly inter-machine buffers.
6. Assumed inter_arrival_time is 1.0 for Source SRC based on the specified rate.
7. Assumed the Machine class accepts a capacity parameter to accommodate the specified capacities for M1 through M5.
8. Used default values for all other missing parameters for all components.
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.source)
        
        # Initializing machines with specific parameters
        # M1(delay 1.0, cap 1), M2(2.0, 2), M3(0.5, 5), M4(3.0, 1), M5(1.5, 3)
        machine_data = [
            (1.0, 1),
            (2.0, 2),
            (0.5, 5),
            (3.0, 1),
            (1.5, 3)
        ]
        self.machines = []
        for i, (delay, cap) in enumerate(machine_data):
            m = Machine(env, id=f"M{i+1}", processing_delay=delay, work_capacity=cap)
            self.machines.append(m)
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Initializing buffers
        self.buffers = []
        
        # Buffer B1 (Source to M1) - default capacity
        self.buffers.append(Buffer(env, id="B1"))
        
        # Inter-machine buffers B2 to B5 - capacity 2
        for i in range(4):
            self.buffers.append(Buffer(env, id=f"B{i+2}", capacity=2))
            
        # Buffer B6 (M5 to SINK) - default capacity
        self.buffers.append(Buffer(env, id="B6"))
        
        self.add_child_edge(self.buffers)
        
        # Connecting nodes
        # SRC to M1 via B1
        self.buffers[0].connect(self.source, self.machines[0])
        
        # Connecting machines in series via B2-B5
        for i in range(4):
            self.buffers[i+1].connect(self.machines[i], self.machines[i+1])
            
        # M5 to SINK via B6
        self.buffers[5].connect(self.machines[4], self.sink)

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