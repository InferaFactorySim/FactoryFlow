"""
ModelDescription:
The system consists of three identical linear production units where items pass through an inspection point, with a portion looping back for rework while the majority feeds into a central router. This router partitions the total flow equally into two distinct branches, Path A and Path B, to facilitate parallel downstream processing. Finally, each branch passes through a terminal stage and terminates at its own dedicated exit, designated as Sink 1 and Sink 2. Use buffer ID = Bi where i=1,2,3... if buffer ID is not specified.

 MODEL ASSUMPTIONS:
1. Defined a class named `Subsystem1` to represent the repeated pattern of "three identical linear production units".
2. Inferred a `Source` node named `src` within each `Subsystem1_i` to generate items, as no source was explicitly described for the units.i=1,2,3
3. Mapped the "inspection point" to a `Machine` node named `M1` within each `Subsystem1`.
4. Mapped the "rework" process to a `Machine` node named `M2` within each `Subsystem1` and a "check" to a `Machine` node named `Machine_check`
5. Inferred the internal flow of the unit as: `src` connects to `M1`.
6. Inferred the rework loop connections as: `M1` connects to `M2`, and `Machine_check` connects back to `M1` Via  buffer with ID 'B_rework'. 'M2' connects to 'Machine_check' via 'B_check'
7. Mapped the "central router" to a `Machine` node named `Mac_M1`.
8. Mapped the "terminal stage" for Path A and Path B to `Machine` nodes named `Mac_M1` and `Mac_M2` respectively.
9. Inferred connections from the units to the router: The `Machine_check` of all three `Subsystem1` instances connects to the `Mac_M1` via buffer with ID 'Bi'i=1,2,3
10. Inferred connections for Path A: `Mac_M1` connects to `Mac_M2` via B_A1, which connects to `sink_1` VIA 'B_A2.
11. Inferred connections for Path A: `Mac_M1` connects to `Mac_M3` via B_B1, which connects to `sink_2` VIA 'B_B2.
12. Used default edge type `Buffer` for all edges connecting nodes as edge type was not specified.
13. Used a single buffer for every connection between nodes.
14. Used default values for processing delays, inter-arrival times, and buffer capacities for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Subsystem1(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Nodes
        self.src = Source(env, id="src")
        self.M1 = Machine(env, id="M1")
        self.M2 = Machine(env, id="M2")
        self.Machine_check = Machine(env, id="Machine_check")
        self.add_child_node([self.src, self.M1, self.M2, self.Machine_check])
        
        # Edges
        # src -> M1 (Unspecified ID -> edge[0])
        self.edge0 = Buffer(env, id="edge[0]")
        # M1 -> M2 (Unspecified ID -> edge[1])
        self.edge1 = Buffer(env, id="edge[1]")
        # M2 -> Machine_check (ID: B_check)
        self.b_check = Buffer(env, id="B_check")
        # Machine_check -> M1 (ID: B_rework)
        self.b_rework = Buffer(env, id="B_rework")
        
        self.add_child_edge([self.edge0, self.edge1, self.b_check, self.b_rework])
        
        # Connections
        self.edge0.connect(self.src, self.M1)
        self.edge1.connect(self.M1, self.M2)
        self.b_check.connect(self.M2, self.Machine_check)
        self.b_rework.connect(self.Machine_check, self.M1)
        
        self.source = self.src

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create 3 Subsystem1 instances
        self.subsystems = [Subsystem1(env, id=f"Subsystem1_{i+1}") for i in range(3)]
        self.add_child_node(self.subsystems)
        
        # Central Router
        self.Mac_M1 = Machine(env, id="Mac_M1")
        
        # Path A Nodes
        self.Mac_M2 = Machine(env, id="Mac_M2")
        self.sink_1 = Sink(env, id="sink_1")
        
        # Path B Nodes
        self.Mac_M3 = Machine(env, id="Mac_M3")
        self.sink_2 = Sink(env, id="sink_2")
        
        self.add_child_node([self.Mac_M1, self.Mac_M2, self.Mac_M3, self.sink_1, self.sink_2])
        
        # Edges from Subsystems to Router (ID: Bi)
        self.router_edges = []
        for i in range(3):
            buf = Buffer(env, id=f"B{i+1}")
            self.add_child_edge(buf)
            buf.connect(self.subsystems[i].Machine_check, self.Mac_M1)
            self.router_edges.append(buf)
            
        # Path A Edges
        self.b_a1 = Buffer(env, id="B_A1")
        self.b_a2 = Buffer(env, id="B_A2")
        self.add_child_edge([self.b_a1, self.b_a2])
        
        self.b_a1.connect(self.Mac_M1, self.Mac_M2)
        self.b_a2.connect(self.Mac_M2, self.sink_1)
        
        # Path B Edges
        self.b_b1 = Buffer(env, id="B_B1")
        self.b_b2 = Buffer(env, id="B_B2")
        self.add_child_edge([self.b_b1, self.b_b2])
        
        self.b_b1.connect(self.Mac_M1, self.Mac_M3)
        self.b_b2.connect(self.Mac_M3, self.sink_2)
        
        self.sinks = [self.sink_1, self.sink_2]

# Simulation Setup
env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)