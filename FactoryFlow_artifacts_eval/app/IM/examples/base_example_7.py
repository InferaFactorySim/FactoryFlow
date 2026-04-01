# DESCRIPTION:
# There are 10 machines connected in series.
# This subsystem of machines in series is repeated 5 times in parallel between 2 other common machines. 
# Finally, 5 of these parallel blocks are connected in series to form the full system. 

import simpy,sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
# LEVEL 1 — CLASS A: 10 machines in series
class A(Node):
    """A chain of  machines: M0 → M1 → ... → M9."""
    def __init__(self, env, name="A"):
        super().__init__(env, name)
        # Create machines
        self.seq = [Machine(env, f"{name}_M{i}", processing_delay=1) for i in range(10)]
        self.add_child_node(self.seq)
        # Create edges connecting them in series
        self.edges = []
        for i in range(9):
            buf = Buffer(env, f"{name}_edge[{i}]", capacity=10)
            self.add_child_edge(buf)
            buf.connect(self.seq[i], self.seq[i+1])
            self.edges.append(buf)
        # Expose endpoints
        self.entry = self.seq[0]
        self.exit = self.seq[-1]
# LEVEL 2 — CLASS B:
# 5 parallel A chains between two machines IN → OUT
class B(Node):
    """Five A-chains in parallel feeding from a common IN machine into a common OUT machine."""
    def __init__(self, env, name="B"):
        super().__init__(env, name)
        # Common input + output machines
        self.IN = Machine(env, f"{name}_IN", processing_delay=1)
        self.OUT = Machine(env, f"{name}_OUT", processing_delay=1)
        self.add_child_node([self.IN, self.OUT])
        self.subA = [A(env, name=f"{name}_A{i}") for i in range(5)]
        self.add_child_node(self.subA)
        # Buffers from IN → each A.entry
        self.in_edges = []
        for i in range(5):
            buf = Buffer(env, f"{name}_in_edge[{i}]", capacity=10)
            self.add_child_edge(buf)
            buf.connect(self.IN, self.subA[i].entry)
            self.in_edges.append(buf)
        # Buffers from each A.exit → OUT
        self.out_edges = []
        for i in range(5):
            buf = Buffer(env, f"{name}_out_edge[{i}]", capacity=10)
            self.add_child_edge(buf)
            buf.connect(self.subA[i].exit, self.OUT)
            self.out_edges.append(buf)
        self.entry = self.IN
        self.exit = self.OUT
# LEVEL 3 — SYSTEM:
# 5 B-blocks in series, with SOURCE feeding B0 and B4 feeding SINK
class System(Node):
    """5 B-blocks in series, with source feeding the first and sink after the last."""
    def __init__(self, env):
        super().__init__(env, "System")
        # External endpoints
        src = Source(env, "SRC", inter_arrival_time=1)
        sink = Sink(env, "SINK")
        self.source = src
        self.sink = sink
        # Create 5 serial B subsystems
        self.blocks = [B(env, name=f"B{i}") for i in range(5)]
        self.add_child_node([src, sink] + self.blocks)
        # Buffers for src → B0
        e0 = Buffer(env, "edge[0]", capacity=10)
        self.add_child_edge(e0)
        e0.connect(src, self.blocks[0].entry)
        # Buffers connecting B0 → B1 → B2 → B3 → B4
        edge_ctr = 1
        for i in range(4):
            buf = Buffer(env, f"edge[{edge_ctr}]", capacity=10)
            self.add_child_edge(buf)
            buf.connect(self.blocks[i].exit, self.blocks[i+1].entry)
            edge_ctr += 1
        # Buffer connecting last B to sink
        e_last = Buffer(env, f"edge[{edge_ctr}]", capacity=10)
        self.add_child_edge(e_last)
        e_last.connect(self.blocks[-1].exit, sink)
