"""
ModelDescription:
System has 8 machines each with delay 2.  Source (ID= SRC) with inter arrival time of 1.2. All machines are interconnected via buffers. Name buffers as B1, B2, B3,.. and Machines as M1,M2,... All buffers have a capacity of 2. The sequence ends in a sink (ID=SINK). There are 4 buffers between M2 and M3 and M6 and M7. Name extra buffers as B3_1,B3_2. B7_1,B7_2 . The in_edge_selection of the machine after multiedge is "ROUND_ROBIN".  All machines have a processing_Delay of 2 and buffers have a capacity of 2. 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description (Source: SRC, Sink: SINK, Machines: M1 through M8).
2. The system topology is assumed to be a linear sequence: SRC -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8 -> SINK.
3. Buffer naming follows the sequence flow: B1 connects SRC to M1, B2 connects M1 to M2, B4 connects M3 to M4, B5 connects M4 to M5, B6 connects M5 to M6, B8 connects M7 to M8, and B9 connects M8 to SINK.
4. To satisfy the requirement of 4 buffers between M2 and M3, the buffers are assumed to be the standard B3, the specified extras B3_1 and B3_2, and an inferred extra buffer named B3_3.
5. To satisfy the requirement of 4 buffers between M6 and M7, the buffers are assumed to be the standard B7, the specified extras B7_1 and B7_2, and an inferred extra buffer named B7_3.
6. The `out_edge_selection` for machines M2 and M6 is assumed to be "ROUND_ROBIN" to distribute parts across the parallel buffers.
7. Used a single buffer for all connections where the number of buffers was not explicitly specified as 4.
8. Simulation duration is assumed to be 25 time units.
"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..', '..','..','src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # Initializing Source
        self.src = Source(env, id="SRC", inter_arrival_time=1.2)
        self.add_child_node(self.src)

        # Initializing Machines M1 to M8
        self.machines = []
        for i in range(8):
            m_id = f"M{i+1}"
            # Determine edge selection strategies based on description and assumptions
            # M2 (index 1) and M6 (index 5) connect to parallel buffers, so out_edge_selection is ROUND_ROBIN
            out_sel = "ROUND_ROBIN" if i in [1, 5] else 0
            # M3 (index 2) and M7 (index 6) receive from parallel buffers, so in_edge_selection is ROUND_ROBIN
            in_sel = "ROUND_ROBIN" if i in [2, 6] else 0
            
            m = Machine(env, id=m_id, processing_delay=2, out_edge_selection=out_sel, in_edge_selection=in_sel)
            self.machines.append(m)
        self.add_child_node(self.machines)

        # Initializing Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Initializing Buffers and Connections
        # Sequence: SRC -> M1 -> M2 -> M3 -> M4 -> M5 -> M6 -> M7 -> M8 -> SINK
        nodes = [self.src] + self.machines + [self.sink]
        self.edges = []
        
        # Loop through the 9 connections
        for i in range(9):
            u = nodes[i]
            v = nodes[i+1]
            
            # Check for parallel buffer sections:
            # i=2 corresponds to connection M2 -> M3 (B3)
            # i=6 corresponds to connection M6 -> M7 (B7)
            if i == 2 or i == 6:
                # Create 4 buffers: Bx, Bx_1, Bx_2, Bx_3
                base_id = f"B{i+1}"
                
                # Main buffer
                b_main = Buffer(env, id=base_id, capacity=2)
                self.add_child_edge(b_main)
                b_main.connect(u, v)
                self.edges.append(b_main)
                
                # Extra buffers
                for k in range(1, 4):
                    b_extra = Buffer(env, id=f"{base_id}_{k}", capacity=2)
                    self.add_child_edge(b_extra)
                    b_extra.connect(u, v)
                    self.edges.append(b_extra)
            else:
                # Single buffer for other connections
                b = Buffer(env, id=f"B{i+1}", capacity=2)
                self.add_child_edge(b)
                b.connect(u, v)
                self.edges.append(b)

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
from factorysimpy.utils.utils import draw_blockdiagram
# Validating the model
fig = draw_blockdiagram(TOP)
path = fig.render(filename="S8__Detailed", directory=".", format="png", cleanup=True)
TOP.validate()
# Running the simulation
TOP.run_simulation(25)