
# A linear sequence of 6 machines connected by buffers with a source with inter_arrival_time as 0.2 and sink. The processing delay of fifth machine should be 2.3 units.

# importing required libraries
import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
from factorysimpy.utils.utils import draw_blockdiagram
       

# defining the model
# linear model with n machines
class SystemModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        # creating nodes

        # initializing source
        self.src = Source(env, id="src")
        # adding source to child nodes
        self.add_child_node(self.src)
       
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        # adding machines to child nodes
        self.add_child_node(self.M)
       
        # initializing sink
        self.sink = Sink(env, id="sink")
        # adding sink to child nodes
        self.add_child_node(self.sink)

        
        # creating edges
        # initializing buffers
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        # adding edges to child edges
        self.add_child_edge(self.e)
    
        # connecting nodes with edges
        #src to first machine
        self.e[0].connect(self.src, self.M[0])
        # machines in between
        for i in range(n-1):
            self.e[i+1].connect(self.M[i],self.M[i+1])
        # last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)


        
        
# initiliating simpy environment
env= simpy.Environment()
# creating linear model with 6 machines
TOP = SystemModel(env,"TOP",n=6) 
# setting inter arrival time of source to 0.2
TOP.src.inter_arrival_time = 0.2
# setting processing delay of fifth machine to 2.3
TOP.M[4].processing_delay = 2.3
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id() 
# validating the model
TOP.validate()
# drawing block diagram
fig = draw_blockdiagram(TOP, "block_diagram")

import streamlit as st
st.graphviz_chart(fig.source)
# running the simulation for 25 time units
TOP.run_simulation(25)

        









