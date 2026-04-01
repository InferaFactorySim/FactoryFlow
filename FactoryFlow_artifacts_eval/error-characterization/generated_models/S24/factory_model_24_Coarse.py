"""
ModelDescription:
There is a mesh of 10X10 machines with the source at top left and sink at bottom right. The edges flow right and down. There is no machine at 5th row and 4th column, and from 3rd to 6th column in 7th row. This means the edges directly connect to the next element skipping the absent machines.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Sink, Machine), but specific IDs are inferred as `M_{row}_{col}` based on grid coordinates.
2. The node at grid position (0,0) is assumed to be the `Source`, and the node at grid position (9,9) is assumed to be the `Sink`.
3. Used default edge type `Buffer` for all connections as the specific edge type was not specified.
4. Used a single buffer for each connection between nodes.
5. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
6. Interpreted the specified "5th row" and "3rd to 6th column" etc., as 1-based indexing (mapping to 0-based indices 4, and 2 through 5 respectively).
7. Assumed `out_edge_selection="ROUND_ROBIN"` for all machines that connect to both a neighbor on the right and a neighbor below to handle the flow splitting.
8. Assumed machines on the bottom boundary only flow right, and machines on the right boundary only flow down.
9. Inferred that if a direct neighbor is missing (absent machine), the edge connects to the next available machine in that specific direction (Right or Down); if no subsequent machine exists in that direction, the path terminates.
10. Due to the specific irregular placement of "absent" machines, a single System class is assumed to generate the grid logic rather than creating a repeated "Row" class pattern.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class MeshSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Grid dimensions
        rows = 10
        cols = 10
        
        # Define absent nodes based on description (0-based indexing)
        # 5th row (index 4), 4th column (index 3)
        # 7th row (index 6), 3rd to 6th column (indices 2, 3, 4, 5)
        absent_indices = {(4, 3), (6, 2), (6, 3), (6, 4), (6, 5)}
        
        self.nodes_grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.all_nodes = []
        
        # Create nodes
        for r in range(rows):
            for c in range(cols):
                if (r, c) in absent_indices:
                    continue
                
                node_id = f"M_{r}_{c}"
                
                if r == 0 and c == 0:
                    # Source at top left
                    self.source = Source(env, id=node_id, inter_arrival_time=1.0)
                    self.nodes_grid[r][c] = self.source
                    self.all_nodes.append(self.source)
                elif r == rows - 1 and c == cols - 1:
                    # Sink at bottom right
                    self.sink = Sink(env, id=node_id)
                    self.nodes_grid[r][c] = self.sink
                    self.all_nodes.append(self.sink)
                else:
                    # Machine
                    # Determine connectivity for out_edge_selection
                    # Check if there is a valid neighbor to the right
                    has_right = False
                    for k in range(c + 1, cols):
                        if (r, k) not in absent_indices:
                            has_right = True
                            break
                    
                    # Check if there is a valid neighbor below
                    has_down = False
                    for k in range(r + 1, rows):
                        if (k, c) not in absent_indices:
                            has_down = True
                            break
                    
                    # If connecting to both right and down, use ROUND_ROBIN
                    if has_right and has_down:
                        machine = Machine(env, id=node_id, out_edge_selection="ROUND_ROBIN")
                    else:
                        machine = Machine(env, id=node_id)
                    
                    self.nodes_grid[r][c] = machine
                    self.all_nodes.append(machine)
        
        self.add_child_node(self.all_nodes)
        
        # Create edges
        self.edges = []
        edge_idx = 0
        
        for r in range(rows):
            for c in range(cols):
                curr = self.nodes_grid[r][c]
                if curr is None:
                    continue
                
                # Sink has no outgoing edges
                if curr == self.sink:
                    continue
                
                # Connect Right: Find next available node in the same row
                next_right = None
                for k in range(c + 1, cols):
                    if self.nodes_grid[r][k] is not None:
                        next_right = self.nodes_grid[r][k]
                        break
                
                if next_right:
                    e = Buffer(env, id=f"edge[{edge_idx}]")
                    self.add_child_edge(e)
                    e.connect(curr, next_right)
                    self.edges.append(e)
                    edge_idx += 1
                
                # Connect Down: Find next available node in the same column
                next_down = None
                for k in range(r + 1, rows):
                    if self.nodes_grid[k][c] is not None:
                        next_down = self.nodes_grid[k][c]
                        break
                
                if next_down:
                    e = Buffer(env, id=f"edge[{edge_idx}]")
                    self.add_child_edge(e)
                    e.connect(curr, next_down)
                    self.edges.append(e)
                    edge_idx += 1

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = MeshSystem(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)