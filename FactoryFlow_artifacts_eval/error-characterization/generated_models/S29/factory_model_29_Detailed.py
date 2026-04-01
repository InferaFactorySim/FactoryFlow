"""
ModelDescription:
Source "SRC" feeds Cell_Top, which contains- Machine_T1, a Subsystem Cell_Sub, which itself contains two parallel machines feeding a machine
and finally a Machine_T2.Buffer IDs are all B1, B2,.. (capacity=2) connect all elements.Final output goes to "SINK". All machines are with delay 3.3 

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description where available.
2. Inferred names for the unspecified machines inside `Cell_Sub` as `Sub_M1` and `Sub_M2` (for the two parallel machines) and `Sub_M3` (for the machine they feed).
3. Used default inter-arrival time (1.0) for Source `SRC` as it was not specified.
4. Assumed a single buffer connects each pair of interacting nodes in the flow path, as the specific number of buffers between nodes was not defined.
5. Inferred logical flow: `SRC` feeds `Machine_T1`; `Machine_T1` splits flow to `Sub_M1` and `Sub_M2`; `Sub_M1` and `Sub_M2` merge flow into `Sub_M3`; `Sub_M3` feeds `Machine_T2`; `Machine_T2` feeds `SINK`.
6. Assumed `Machine_T1` connects to both `Sub_M1` and `Sub_M2` via separate buffers to handle the splitting of flow without a dedicated Splitter node.
7. Assumed `Sub_M1` and `Sub_M2` both connect to `Sub_M3` via separate buffers to handle the merging of flow without a dedicated Combiner node.
8. Assumed sequential naming for Buffer IDs (B1, B2, etc.) based on the flow order.
"""

import simpy
import itertools
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Global counter for buffer IDs
b_counter = itertools.count(1)

class Cell_Sub(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Inferred names: Sub_M1, Sub_M2 (parallel machines)
        self.parallel_machines = [Machine(env, id=f"Sub_M{i+1}", processing_delay=3.3) for i in range(2)]
        self.add_child_node(self.parallel_machines)
        
        # Inferred name: Sub_M3 (machine fed by parallel machines)
        self.merge_machine = Machine(env, id="Sub_M3", processing_delay=3.3)
        self.add_child_node(self.merge_machine)
        
        # Edges from parallel machines to merge machine
        self.internal_edges = []
        for i in range(2):
            buf = Buffer(env, id=f"B{next(b_counter)}", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.parallel_machines[i], self.merge_machine)
            self.internal_edges.append(buf)
            
        # Expose endpoints
        self.entries = self.parallel_machines
        self.exit = self.merge_machine

class Cell_Top(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Machine_T1
        self.m_t1 = Machine(env, id="Machine_T1", processing_delay=3.3)
        self.add_child_node(self.m_t1)
        
        # Cell_Sub
        self.sub = Cell_Sub(env, id="Cell_Sub")
        self.add_child_node(self.sub)
        
        # Machine_T2
        self.m_t2 = Machine(env, id="Machine_T2", processing_delay=3.3)
        self.add_child_node(self.m_t2)
        
        # Edges from T1 to Sub (Split)
        self.split_edges = []
        for i in range(2):
            buf = Buffer(env, id=f"B{next(b_counter)}", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.m_t1, self.sub.entries[i])
            self.split_edges.append(buf)
            
        # Edge from Sub to T2
        self.edge_sub_t2 = Buffer(env, id=f"B{next(b_counter)}", capacity=2)
        self.add_child_edge(self.edge_sub_t2)
        self.edge_sub_t2.connect(self.sub.exit, self.m_t2)
        
        # Expose endpoints
        self.entry = self.m_t1
        self.exit = self.m_t2

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.source)
        
        # Cell_Top
        self.cell_top = Cell_Top(env, id="Cell_Top")
        self.add_child_node(self.cell_top)
        
        # Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # Edge Source -> Cell_Top
        self.edge_src = Buffer(env, id=f"B{next(b_counter)}", capacity=2)
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.source, self.cell_top.entry)
        
        # Edge Cell_Top -> Sink
        self.edge_sink = Buffer(env, id=f"B{next(b_counter)}", capacity=2)
        self.add_child_edge(self.edge_sink)
        self.edge_sink.connect(self.cell_top.exit, self.sink)

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