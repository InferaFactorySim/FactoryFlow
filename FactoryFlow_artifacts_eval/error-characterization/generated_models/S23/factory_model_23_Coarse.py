"""
ModelDescription:
The system consists of three identical linear production units where items pass through an inspection point, with a portion looping back for rework while the majority feeds into a central router. This router partitions the total flow equally into two distinct branches, Path A and Path B, to facilitate parallel downstream processing. Finally, each branch passes through a terminal stage and terminates at its own dedicated exit, designated as Sink 1 and Sink 2.

 MODEL ASSUMPTIONS:
1. Defined a class named `ProductionUnit` to represent the repeated pattern of "three identical linear production units".
2. Inferred a `Source` node named `Unit_Source` within each `ProductionUnit` to generate items, as no source was explicitly described for the units.
3. Mapped the "inspection point" to a `Machine` node named `Inspection_Machine` within each `ProductionUnit`.
4. Mapped the "rework" process to a `Machine` node named `Rework_Machine` within each `ProductionUnit`.
5. Inferred the internal flow of the unit as: `Unit_Source` connects to `Inspection_Machine`.
6. Inferred the rework loop connections as: `Inspection_Machine` connects to `Rework_Machine`, and `Rework_Machine` connects back to `Inspection_Machine`.
7. Mapped the "central router" to a `Machine` node named `Central_Router`.
8. Mapped the "terminal stage" for Path A and Path B to `Machine` nodes named `Terminal_Machine_A` and `Terminal_Machine_B` respectively.
9. Inferred connections from the units to the router: The `Inspection_Machine` of all three `ProductionUnit` instances connects to the `Central_Router`.
10. Inferred connections for Path A: `Central_Router` connects to `Terminal_Machine_A`, which connects to `Sink 1`.
11. Inferred connections for Path B: `Central_Router` connects to `Terminal_Machine_B`, which connects to `Sink 2`.
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

class ProductionUnit(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Nodes
        self.source = Source(env, id="Unit_Source")
        self.inspection = Machine(env, id="Inspection_Machine")
        self.rework = Machine(env, id="Rework_Machine")
        self.add_child_node([self.source, self.inspection, self.rework])
        
        # Edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(3)]
        self.add_child_edge(self.edges)
        
        # Connect Unit_Source to Inspection_Machine
        self.edges[0].connect(self.source, self.inspection)
        # Connect Inspection_Machine to Rework_Machine
        self.edges[1].connect(self.inspection, self.rework)
        # Connect Rework_Machine back to Inspection_Machine
        self.edges[2].connect(self.rework, self.inspection)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create 3 Production Units
        self.units = [ProductionUnit(env, id=f"ProductionUnit[{i}]") for i in range(3)]
        self.add_child_node(self.units)
        
        # Central Router
        self.router = Machine(env, id="Central_Router")
        self.add_child_node(self.router)
        
        # Terminal Machines for Path A and Path B
        self.term_a = Machine(env, id="Terminal_Machine_A")
        self.term_b = Machine(env, id="Terminal_Machine_B")
        self.add_child_node([self.term_a, self.term_b])
        
        # Sinks
        self.sink1 = Sink(env, id="Sink 1")
        self.sink2 = Sink(env, id="Sink 2")
        self.add_child_node([self.sink1, self.sink2])
        
        # Edges from Units to Router
        self.unit_edges = [Buffer(env, id=f"unit_edge[{i}]") for i in range(3)]
        self.add_child_edge(self.unit_edges)
        
        for i in range(3):
            self.unit_edges[i].connect(self.units[i].inspection, self.router)
            
        # Edges from Router to Terminal Machines
        self.router_edges = [Buffer(env, id=f"router_edge[{i}]") for i in range(2)]
        self.add_child_edge(self.router_edges)
        
        self.router_edges[0].connect(self.router, self.term_a)
        self.router_edges[1].connect(self.router, self.term_b)
        
        # Edges from Terminal Machines to Sinks
        self.term_edges = [Buffer(env, id=f"term_edge[{i}]") for i in range(2)]
        self.add_child_edge(self.term_edges)
        
        self.term_edges[0].connect(self.term_a, self.sink1)
        self.term_edges[1].connect(self.term_b, self.sink2)

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