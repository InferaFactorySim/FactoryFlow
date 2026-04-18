"""
ModelDescription:
There is a mesh of 10X10 machines with the source at top left and sink at bottom right. The edges flow right and down. There is no machine at 5th row and 4th column, and from 3rd to 6th column in 7th row. This means the edges directly connect to the next element skipping the absent machines. src and sink is common and the "src" connects to all first machines in the row  individually and all last machines connects to "sink" individually.  The series of machines are a subsystem. 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Sink, Machine, Buffer).
2. Machines are identified using a coordinate-based naming convention (e.g., `M[row+1][col+1]`) corresponding to the 10x10 grid.
3. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
4. Used a single `Buffer` edge for every connection between nodes. Assumed Buffer IDs follow the format `B_{r1}{c1}_{r2}{c2}` (e.g., B_11_12) for connections between machines, and `B_src_{r}{c}` / `B_{r}{c}_sink` for source/sink connections.
5. The Source is assumed to connect to the machine at the top-left corner (row 0, column 0).
6. The machine at the bottom-right corner (row 9, column 9) is assumed to connect to the Sink.
7. Since Splitter nodes are not used, `Machine` nodes are assumed to handle output routing for flows that go both Right and Down, using a default `out_edge_selection` (e.g., Round Robin).
8. "Skipping absent machines" is assumed to mean that if the immediate neighbor in a direction (Right or Down) is missing, the edge connects to the next available machine in that same direction, bypassing the gap.
9. The entire mesh is treated as a single system pattern (SystemModel) containing the logic for the grid and the holes, rather than creating sub-classes for rows, due to the vertical connectivity and irregular gaps.
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
        
        # Initializing source and sink
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Grid dimensions
        rows, cols = 10, 10
        
        # Defining gaps based on description (0-based indices)
        # 5th row (index 4), 4th column (index 3)
        # 7th row (index 6), 3rd to 6th column (indices 2, 3, 4, 5)
        gaps = {
            (4, 3),
            (6, 2), (6, 3), (6, 4), (6, 5)
        }
        
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.machines = []
        
        # Creating machines
        for r in range(rows):
            for c in range(cols):
                if (r, c) not in gaps:
                    m = Machine(env, id=f"M[{r+1}][{c+1}]")
                    self.grid[r][c] = m
                    self.machines.append(m)
        self.add_child_node(self.machines)
        
        self.edges = []
        
        # Connecting Source to the first machine of each row
        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c]:
                    edge = Buffer(env, id=f"B_src_{r+1}{c+1}")
                    self.add_child_edge(edge)
                    edge.connect(self.src, self.grid[r][c])
                    self.edges.append(edge)
                    break
        
        # Connecting the last machine of each row to Sink
        for r in range(rows):
            for c in range(cols - 1, -1, -1):
                if self.grid[r][c]:
                    edge = Buffer(env, id=f"B_{r+1}{c+1}_sink")
                    self.add_child_edge(edge)
                    edge.connect(self.grid[r][c], self.sink)
                    self.edges.append(edge)
                    break
                    
        # Connecting machines within the mesh (Right and Down)
        for r in range(rows):
            for c in range(cols):
                curr = self.grid[r][c]
                if not curr:
                    continue
                
                # Connect Right (skipping gaps)
                for k in range(c + 1, cols):
                    if self.grid[r][k]:
                        edge = Buffer(env, id=f"B_{r+1}{c+1}_{r+1}{k+1}")
                        self.add_child_edge(edge)
                        edge.connect(curr, self.grid[r][k])
                        self.edges.append(edge)
                        break
                
                # Connect Down (skipping gaps)
                for k in range(r + 1, rows):
                    if self.grid[k][c]:
                        edge = Buffer(env, id=f"B_{r+1}{c+1}_{k+1}{c+1}")
                        self.add_child_edge(edge)
                        edge.connect(curr, self.grid[k][c])
                        self.edges.append(edge)
                        break

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)