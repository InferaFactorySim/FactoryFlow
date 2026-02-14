"""
ModelDescription:
A hierarchical system where a  subystem inside a top-level cell contains a machine Machine_T1, a nested hierarchical subsystem with parallel machines  and a single machine in series(M1,M2, M3), and a final machine , Machine_T2 arranged in series between a source and a sink.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
3. Used default edge type 'Buffer' for all connections as edge type was not specified.
4. Used a single buffer for every connection between nodes.
5. Inferred a top-level container class named 'System' containing the Source, Sink, and the top-level subsystem.
6. Inferred the top-level subsystem is a class named 'Outer_Subsystem' containing Machine_T1, Machine_T2, and the nested subsystem.
7. Inferred the nested hierarchical subsystem is a class named 'Inner_Subsystem'.
8. Interpreted the description "parallel machines and a single machine in series(M1,M2, M3)" to mean that M1 and M2 are the parallel machines, and M3 is the single machine in series following them within the 'Inner_Subsystem'.
9. Assumed the flow within 'Outer_Subsystem' is: Machine_T1 connects to the 'Inner_Subsystem', which connects to Machine_T2.
10. Assumed the connection logic for the parallel setup in 'Inner_Subsystem' is that the input flows to both M1 and M2 via buffers, and both M1 and M2 connect to M3 via buffers.
11. Assumed the Source connects to Machine_T1 and Machine_T2 connects to the Sink.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Inner_Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Parallel machines M1 and M2
        self.parallel_machines = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.parallel_machines)
        
        # Single machine M3 in series
        self.M3 = Machine(env, id="M3")
        self.add_child_node(self.M3)
        
        # Connecting M1 and M2 to M3
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(2)]
        self.add_child_edge(self.edges)
        for i in range(2):
            self.edges[i].connect(self.parallel_machines[i], self.M3)

class Outer_Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Machine_T1
        self.Machine_T1 = Machine(env, id="Machine_T1")
        self.add_child_node(self.Machine_T1)
        
        # Nested Inner_Subsystem
        self.inner = Inner_Subsystem(env, id="Inner_Subsystem")
        self.add_child_node(self.inner)
        
        # Machine_T2
        self.Machine_T2 = Machine(env, id="Machine_T2")
        self.add_child_node(self.Machine_T2)
        
        # Connecting Machine_T1 to Inner_Subsystem (M1 and M2)
        self.in_edges = [Buffer(env, id=f"in_edge[{i}]") for i in range(2)]
        self.add_child_edge(self.in_edges)
        for i in range(2):
            self.in_edges[i].connect(self.Machine_T1, self.inner.parallel_machines[i])
            
        # Connecting Inner_Subsystem (M3) to Machine_T2
        self.out_edge = Buffer(env, id="out_edge")
        self.add_child_edge(self.out_edge)
        self.out_edge.connect(self.inner.M3, self.Machine_T2)

class System(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id="Source")
        self.add_child_node(self.source)
        
        # Top-level subsystem
        self.outer = Outer_Subsystem(env, id="Outer_Subsystem")
        self.add_child_node(self.outer)
        
        # Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Connecting Source to Machine_T1
        self.src_edge = Buffer(env, id="src_edge")
        self.add_child_edge(self.src_edge)
        self.src_edge.connect(self.source, self.outer.Machine_T1)
        
        # Connecting Machine_T2 to Sink
        self.sink_edge = Buffer(env, id="sink_edge")
        self.add_child_edge(self.sink_edge)
        self.sink_edge.connect(self.outer.Machine_T2, self.sink)

# Initializing simpy environment
env = simpy.Environment()
# Creating the system
TOP = System(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)