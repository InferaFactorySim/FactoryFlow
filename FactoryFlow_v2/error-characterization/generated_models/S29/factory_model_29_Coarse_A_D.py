"""
ModelDescription:
A hierarchical system where a  subystem inside a top-level cell contains a machine Machine_T1, a nested hierarchical subsystem with parallel machines  and a single machine in series(M1,M2, M3), and a final machine , Machine_T2 arranged in series between a source and a sink. All buffers have ID Bi, i=1,2,3 in all classes in if not available

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
3. Used default edge type 'Buffer' for all connections as edge type was not specified.
4. Used a single buffer for every connection between nodes.
5. Inferred a top-level container class named 'System' containing the Source, Sink, and the top-level subsystem.
6. Inferred the top-level subsystem is a class named 'Cell_Top' containing Machine_T1, Machine_T2, and the nested subsystem.
7. Inferred the nested hierarchical subsystem is a class named 'Cell_Sub'.
8. Interpreted the description "parallel machines and a single machine in series(M1,M2, M3)" to mean that M1 and M2 are the parallel machines, and M3 is the single machine in series following them within the 'Cell_Sub.
9. Assumed the flow within 'Cell_Top'  is: Machine_T1 connects to the 'Cell_Sub', which connects to Machine_T2.
10. Assumed the connection logic for the parallel setup in 'Cell_Sub' is that the input flows to both M1 and M2 via buffers, and both M1 and M2 connect to M3 via buffers.
11. Assumed the Source connects to Machine_T1 and Machine_T2 connects to the Sink.
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Cell_Sub(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Parallel machines M1 and M2
        self.parallel_M = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.parallel_M)
        
        # Single machine in series M3
        self.M3 = Machine(env, id="M3")
        self.add_child_node(self.M3)
        
        self.edges = []
        # Connect M1 and M2 to M3 using buffers B1, B2
        for i in range(2):
            b = Buffer(env, id=f"B{i+1}")
            b.connect(self.parallel_M[i], self.M3)
            self.edges.append(b)
        self.add_child_edge(self.edges)

class Cell_Top(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.Machine_T1 = Machine(env, id="Machine_T1")
        self.sub = Cell_Sub(env, id="Cell_Sub")
        self.Machine_T2 = Machine(env, id="Machine_T2")
        
        self.add_child_node([self.Machine_T1, self.sub, self.Machine_T2])
        
        self.edges = []
        # Connect Machine_T1 to parallel machines in Cell_Sub (M1, M2) using buffers B1, B2
        for i in range(2):
            b = Buffer(env, id=f"B{i+1}")
            b.connect(self.Machine_T1, self.sub.parallel_M[i])
            self.edges.append(b)
            
        # Connect Cell_Sub (M3) to Machine_T2 using buffer B3
        b3 = Buffer(env, id="B3")
        b3.connect(self.sub.M3, self.Machine_T2)
        self.edges.append(b3)
        
        self.add_child_edge(self.edges)

class System(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.source = Source(env, id="Source")
        self.cell_top = Cell_Top(env, id="Cell_Top")
        self.sink = Sink(env, id="Sink")
        
        self.add_child_node([self.source, self.cell_top, self.sink])
        
        self.edges = []
        # Connect Source to Machine_T1 using buffer B1
        b1 = Buffer(env, id="B1")
        b1.connect(self.source, self.cell_top.Machine_T1)
        self.edges.append(b1)
        
        # Connect Machine_T2 to Sink using buffer B2
        b2 = Buffer(env, id="B2")
        b2.connect(self.cell_top.Machine_T2, self.sink)
        self.edges.append(b2)
        
        self.add_child_edge(self.edges)

# Initializing simpy environment
env = simpy.Environment()
# Creating the top level system
TOP = System(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)