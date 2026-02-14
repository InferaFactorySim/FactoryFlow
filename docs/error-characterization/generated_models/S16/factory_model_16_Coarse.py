"""
ModelDescription:
A source feeds a production row. Each row consists of a welding cell that processes incoming items and then passes them onward to a sink. Within each welding cell, items are processed by a single machine and temporarily held before exiting the cell.
All rows operate in parallel and do not interact with each other. There are 3 such rows.


 MODEL ASSUMPTIONS:
1. Inferred a repeated pattern and assumed a class `WeldingCell` is created to encapsulate the machine and the holding buffer, and a class `ProductionRow` is created to encapsulate the Source, Welding Cell, and Sink, instantiated 3 times.
2. Assumed the "temporarily held" requirement within the welding cell is implemented by a `Buffer` node connected to the output of the Machine within the cell.
3. Assumed each of the 3 rows possesses its own independent `Source` and `Sink` nodes to satisfy the condition that rows do not interact.
4. Used default edge type `Buffer` for all connections (Source to Welding Cell, Machine to internal holding Buffer, internal holding Buffer to Sink) as edge types were not specified.
5. Used a single buffer for all connections between nodes where the number of buffers was not specified.
6. Inferred generic node IDs (e.g., `src`, `sink`, `M`, `hold_buf`) and hierarchical naming conventions for the rows and cells.
7. Used default values for all missing parameters (source inter-arrival times, machine processing delays, and buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class WeldingCell(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Machine inside the cell
        self.M = Machine(env, id="M")
        self.add_child_node(self.M)
        
        # Holding buffer inside the cell (Assumption 1 & 2)
        self.hold_buf = Buffer(env, id="hold_buf")
        self.add_child_edge(self.hold_buf)

class ProductionRow(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source (Assumption 3)
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Welding Cell (Assumption 1)
        self.wc = WeldingCell(env, id="welding_cell")
        self.add_child_node(self.wc)
        
        # Sink (Assumption 3)
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Edge from Source to Welding Cell Machine
        self.edge = Buffer(env, id="edge")
        self.add_child_edge(self.edge)
        
        # Connect Source -> Machine
        self.edge.connect(self.src, self.wc.M)
        
        # Connect Machine -> Sink using the internal holding buffer
        self.wc.hold_buf.connect(self.wc.M, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # 3 Parallel Rows (Assumption 1)
        self.rows = [ProductionRow(env, id=f"Row[{i}]") for i in range(3)]
        self.add_child_node(self.rows)

# Initializing simpy environment
env = simpy.Environment()

# Creating the top level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)