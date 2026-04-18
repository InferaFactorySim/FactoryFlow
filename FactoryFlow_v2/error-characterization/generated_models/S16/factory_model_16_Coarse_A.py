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
6. Inferred generic node IDs (e.g., `Source_{Ri}`, `SINK_{RI}`, `Machine_W1`, ) and hierarchical naming , where i is the row count .conventions for the rows and cells. each row is called  R1, R2, R3. `Buffer_W` connects MAchine_W1 to sink in each row. B_src_Ri connectes src to machine_w1 in each row and and the cell ID is WeldingCell_Ri where i is the row number. 
7. Used default values for all missing parameters (source inter-arrival times, machine processing delays, and buffer capacities) for all components.
"""

# importing required libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the Welding Cell model
class WeldingCell(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing machine
        self.machine = Machine(env, id="Machine_W1")
        self.add_child_node(self.machine)
        
        # initializing internal holding buffer (edge)
        # Encapsulates the holding buffer as per Assumption 1
        self.buffer = Buffer(env, id="Buffer_W")
        self.add_child_edge(self.buffer)

# defining the Production Row model
class ProductionRow(Node):
    def __init__(self, env, id, row_num):
        super().__init__(env, id)
        
        # initializing source
        self.source = Source(env, id=f"Source_R{row_num}")
        self.add_child_node(self.source)
        
        # initializing welding cell
        self.welding_cell = WeldingCell(env, id=f"WeldingCell_R{row_num}")
        self.add_child_node(self.welding_cell)
        
        # initializing sink
        self.sink = Sink(env, id=f"SINK_R{row_num}")
        self.add_child_node(self.sink)
        
        # initializing edge from source to welding cell
        self.edge_src = Buffer(env, id=f"B_src_R{row_num}")
        self.add_child_edge(self.edge_src)
        
        # connecting source to machine inside welding cell
        self.edge_src.connect(self.source, self.welding_cell.machine)
        
        # connecting machine inside welding cell to sink using internal buffer
        # Buffer_W connects Machine_W1 to sink as per Assumption 6
        self.welding_cell.buffer.connect(self.welding_cell.machine, self.sink)

# defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 3 production rows operating in parallel
        self.rows = [ProductionRow(env, id=f"R{i+1}", row_num=i+1) for i in range(3)]
        self.add_child_node(self.rows)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)