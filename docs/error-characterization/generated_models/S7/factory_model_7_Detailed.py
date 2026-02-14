"""
ModelDescription:
System has 5 machines (M1-M5) in series. M1(delay 1.0, cap 1), M2(2.0, 2), M3(0.5, 5), M4(3.0, 1), M5(1.5, 3). SRC (rate 1.0) feeds M1 via B1. All inter-machine buffers have capacity 2. Ends in SINK. 

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
        
        # Initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.src)
        
        # Initializing machines M1-M5 with specific delays and capacities
        # Config format: (processing_delay, work_capacity)
        machine_configs = [
            (1.0, 1), # M1
            (2.0, 2), # M2
            (0.5, 5), # M3
            (3.0, 1), # M4
            (1.5, 3)  # M5
        ]
        
        self.machines = []
        for i, (delay, cap) in enumerate(machine_configs):
            m = Machine(env, id=f"M{i+1}", processing_delay=delay, work_capacity=cap)
            self.machines.append(m)
        self.add_child_node(self.machines)
        
        # Initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Creating edges
        self.edges = []
        
        # Edge 0: SRC -> M1 (B1, default capacity)
        edge0 = Buffer(env, id="edge[0]")
        edge0.connect(self.src, self.machines[0])
        self.edges.append(edge0)
        
        # Edges 1-4: Inter-machine connections (Capacity 2)
        for i in range(4):
            edge = Buffer(env, id=f"edge[{i+1}]", capacity=2)
            edge.connect(self.machines[i], self.machines[i+1])
            self.edges.append(edge)
            
        # Edge 5: M5 -> SINK (Default capacity)
        edge_last = Buffer(env, id="edge[5]")
        edge_last.connect(self.machines[-1], self.sink)
        self.edges.append(edge_last)
        
        self.add_child_edge(self.edges)

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation for 25 time units
TOP.run_simulation(25)