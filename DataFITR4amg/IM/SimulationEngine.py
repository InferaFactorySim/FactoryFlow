import simpy
import os
import sys

# Add the FactorySimPy/src folder to the Python path
#print("FactorySimPy path:", os.path.abspath('../../FactorySimPy/src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FactorySimPy/src')))

# Verify if the Sink module exists in the specified path
# if not os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FactorySimPy/src')), 'Monitor.py')):
#     raise ImportError("The module 'Monitor' could not be found in the specified path.")
#print("ho/a",os.path.abspath('../FactorySimPy/src'))


#from Monitor import SystemMonitor, ProcessorMonitor
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink
#from factorysimpy.constructs.chain import connect_chain_with_source_sink, connect_nodes_with_buffers  

import importlib.util
def load_processing_delay_from_file(file_name, delay_folder):
    """Dynamically loads a Python file from a given folder and retrieves the processing delay function."""
    file_path = os.path.join(delay_folder, file_name)
    if os.path.exists(file_path):
        module_name = file_name.replace(".py", "")  # Remove the .py extension
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Assume the file has a function named `generate_data()` that returns the processing delay
        delay_func = getattr(module, "generate_data", None)
        if delay_func and callable(delay_func):
            return delay_func()
        else:
            raise AttributeError(f"Function 'generate_data' not found in {file_name}.")
    else:
        raise FileNotFoundError(f"File {file_name} not found in folder {delay_folder}.")
    

import importlib.util
def load_processing_delay_from_file(file_name, delay_folder):
    """Dynamically loads a Python file from a given folder and retrieves the processing delay function."""
    file_path = os.path.join(delay_folder, file_name)
    if os.path.exists(file_path):
        module_name = file_name.replace(".py", "")  # Remove the .py extension
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Assume the file has a function named `generate_data()` that returns the processing delay
        delay_func = getattr(module, "generate_data", None)
        if delay_func and callable(delay_func):
            return delay_func()
        else:
            raise AttributeError(f"Function 'generate_data' not found in {file_name}.")
    else:
        raise FileNotFoundError(f"File {file_name} not found in folder {delay_folder}.")




def get_node_by_id(nodes, node_id):
    for node in nodes:
        if getattr(node, 'id', None) == node_id:
            return node
    return None

def simulation_engine_m1(data):
    print("Starting simulation engine M1...")
    
    # Set the delay folder dynamically
    #delay_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gencodeforAMG_10'))
    delay_folder =     os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../gencodeforAMG'))
    
    env = simpy.Environment()
    #print(data)

    # Extract prefix from data (if it exists), otherwise default to 'Machine'
    

    # Extract node_cls and edge_cls from data, otherwise default to Machine and Buffer
    node_cls = data.get('node_cls', Machine)
    edge_cls = data.get('edge_cls', Buffer)
    machines=[]
    buffers=[]
    
    for i in range(len(data)):
        if data[i]['type'] == 'Machine':
            machine_id = data[i]['id']
            processing_delay_file = f"{machine_id}_processing_delay_code.py"
            in_edge_selection_file = f"{machine_id}_in_edge_selection_code.py"
            out_edge_selection_file = f"{machine_id}_out_edge_selection_code.py"
            
            processing_delay = load_processing_delay_from_file(processing_delay_file, delay_folder)
            #in_edge_selection= load_processing_delay_from_file(in_edge_selection_file, delay_folder)
            
            out_edge_selection= load_processing_delay_from_file(out_edge_selection_file, delay_folder)  

            in_edge_selection="FIRST_AVAILABLE"
            #out_edge_selection="FIRST_AVAILABLE"
        #print(original_node_kwargs[i])
            
                
            work_capacity= int(data[i].get('work_capacity', None))

            node_setup_time= data[i].get('node_setup_time', 0)
        
            machines.append(Machine(env, id=machine_id, work_capacity=work_capacity,processing_delay=processing_delay,in_edge_selection=in_edge_selection, out_edge_selection=out_edge_selection ))
     
        elif data[i]['type'] == 'Buffer':
            buffer_id = data[i]['id']
            store_capacity= int(data[i].get('store_capacity', 2))
            delay= data[i].get('delay', 0)
            mode= data[i].get('mode', 'FIFO')
            src_node= data[i].get('src_node', None)
            dest_node= data[i].get('dest_node', None)
        
            b=Buffer(env,id=buffer_id,store_capacity=store_capacity,delay=delay, mode=mode) 
            
            src_node=get_node_by_id(machines, src_node)
            #print(dest_node)
            dest_node=get_node_by_id(machines, dest_node)
            #print(dest_node)
                
            b.connect(src_node,dest_node)  

            buffers.append(b)
    
    
        
    src=Source(env, id="src", inter_arrival_time=0.2, blocking=True, out_edge_selection="FIRST_AVAILABLE")
    sink= Sink(env,id="sink")
    machines.insert(0,src)
    machines.append(sink)
    #print([i.id for i in machines])
        
        
        


    




    sim_time = 10000
    

    import time

    start_time = time.time()

    

    env.run(until=sim_time)
    end_time = time.time()


    print(f"Simulation {sim_time} ran for {end_time - start_time:.2f} seconds.")

    for machine in machines:

        machine.update_final_state_time(sim_time)

    # Print out statistics for source, machines, and sink
    print(f"SRC {src.id} state times: {src.stats}")
    print(f"SINK {sink.id} received {sink.stats['num_item_received']} items.")
    print(f"Throughput: {sink.stats['num_item_received'] / env.now:.2f} items per time unit.")

    tot_cycletime = sink.stats["total_cycle_time"]
    tot_items = sink.stats["num_item_received"]
    print(f"Cycletime: {tot_cycletime / tot_items if tot_items > 0 else 0:.2f}")

    print(f"Source {src.id} generated {src.stats['num_item_generated']} items.")

    for machine in machines[1:-1]:
        print(f"\nMachine {machine.id} state times: {machine.stats['total_time_spent_in_states']}")
        print(f"Total items processed: {machine.stats['num_item_processed']}")
        print(machine.time_per_work_occupancy)

    for buf in buffers:
        print(f"Time-averaged number of items in {buf.id}: {buf.stats['time_averaged_num_of_items_in_buffer']}")

    return sink.stats['num_item_received'] / env.now

def simulation_engine_m2(data):
    print("Starting simulation engine M2...")
    
    # Set the delay folder dynamically
    delay_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gencodeforAMG'))
    
    if "count" in data:
        count = data['count']
        env = simpy.Environment()

        # Extract prefix from data (if it exists), otherwise default to 'Machine'
        prefix = data.get('prefix', 'Machine')

        # Extract node_cls and edge_cls from data, otherwise default to Machine and Buffer
        node_cls = data.get('node_cls', Machine)
        edge_cls = data.get('edge_cls', Buffer)

        node_kwargs_list = []
        
        for i in range(count):
            machine_id = f"M{i + 1}"
            processing_delay_file = f"{machine_id}_processing_delay_code.py"
            
            try:
                processing_delay = load_processing_delay_from_file(processing_delay_file, delay_folder)
            except FileNotFoundError:
                print(f"Warning: {processing_delay_file} not found, using default delay of 1.0")
                processing_delay = 1.0  # Default delay if file is not found
            except Exception as e:
                print(f"Error loading {processing_delay_file}: {e}")
                processing_delay = 1.0  # Default delay if error occurs

            node_kwargs = {
                "id": machine_id,
                "node_setup_time": 0,
                "work_capacity": 1,
                "processing_delay": processing_delay,
                "in_edge_selection": "FIRST_AVAILABLE",
                "out_edge_selection": "FIRST_AVAILABLE"
            }

            node_kwargs_list.append(node_kwargs)

        edge_kwargs_list = []
        for i in range(count + 1):
            buffer_id = f"Buffer{i + 1}"
            edge_kwargs = {
                "id": buffer_id,
                "type": "Buffer",  # 'type' is inferred, not passed directly in the kwargs
                "inp": f"Machine{i}" if i > 0 else "Source",  # Connect first buffer to source
                "out": f"Machine{i+1}" if i < count else "Sink"  # Connect last buffer to sink
            }

            edge_kwargs_list.append(edge_kwargs)

        source_kwargs = data.get('source_kwargs', {})
        sink_kwargs = data.get('sink_kwargs', {})

        # Now we can call connect_chain_with_source_sink with the correct arguments
        nodes, edges, src, sink = connect_chain_with_source_sink(
            env, count, Machine, Buffer, Source, Sink,
            node_kwargs_list, edge_kwargs_list, source_kwargs, sink_kwargs,
            
        )

        machines, buffers = connect_nodes_with_buffers(nodes, edges, src, sink)

        sim_time = 100
        env.process(src.generate_item())  # Start source generating items
        for machine in machines:
            env.process(machine.process_item())  # Start processing items in machines

        env.run(until=sim_time)

        for machine in machines[1:-1]:
            machine.update_final_state_time(sim_time)

        # Print out statistics for source, machines, and sink
        print(f"SRC {src.id} state times: {src.stats}")
        print(f"SINK {sink.id} received {sink.stats['num_item_received']} items.")
        print(f"Throughput: {sink.stats['num_item_received'] / env.now:.2f} items per time unit.")

        tot_cycletime = sink.stats["total_cycle_time"]
        tot_items = sink.stats["num_item_received"]
        print(f"Cycletime: {tot_cycletime / tot_items if tot_items > 0 else 0:.2f}")

        print(f"Source {src.id} generated {src.stats['num_item_generated']} items.")

        for machine in machines[1:-1]:
            print(f"\nMachine {machine.id} state times: {machine.stats}")
            print(f"Total items processed: {machine.stats['num_item_processed']}")

        for buf in buffers:
            print(f"Time-averaged number of items in {buf.id}: {buf.stats['time_averaged_num_of_items_in_buffer']}")

        return sink.stats['num_item_received'] / env.now


def connect_chain(env, count, node_cls, edge_cls,
                  node_kwargs=None, edge_kwargs=None,
                  node_kwargs_list=None, edge_kwargs_list=None,
                  prefix="Node", edge_prefix="Edge"):
    nodes = []
    edges = []
    
    for i in range(count):
        if node_kwargs_list:
            kwargs = node_kwargs_list[i].copy()
        elif node_kwargs is not None:
            kwargs = node_kwargs.copy()
        else:
            kwargs = {"processing_delay": 0.8, "blocking": True}.copy()

        node_name = f"{prefix}_{i + 1}"
        if "id" in kwargs:
            node_name = kwargs.pop("id")

        print(f"Creating node {node_name} with kwargs: {kwargs}", flush=True)
        node = node_cls(env=env, id=node_name, **kwargs)
        nodes.append(node)

    for i in range(count + 1):
        if edge_kwargs_list:
            kwargs = edge_kwargs_list[i].copy()
        elif edge_kwargs is not None:
            kwargs = edge_kwargs.copy()
        else:
            kwargs = {"delay": 0}.copy()

        edge_name = f"{edge_prefix}_{i + 1}"
        if "id" in kwargs:
            edge_name = kwargs.pop("id")

        edge = edge_cls(env=env, id=edge_name, **kwargs)
        edges.append(edge)

    return nodes, edges


def connect_chain_with_source_sink(env, count, node_cls, edge_cls,
                                    node_kwargs=None, edge_kwargs=None,
                                    node_kwargs_list=None, edge_kwargs_list=None,
                                    prefix="Node", edge_prefix="Edge",
                                    source_cls=None, sink_cls=None,
                                    source_kwargs=None, sink_kwargs=None):
    nodes, edges = connect_chain(env, count, node_cls, edge_cls,
                                 node_kwargs, edge_kwargs,
                                 node_kwargs_list, edge_kwargs_list,
                                 prefix, edge_prefix)
    
    if source_cls:
        source_kwargs = source_kwargs if source_kwargs else {"inter_arrival_time": 1, "blocking": True}.copy()
        src_name = "Source"
        if "id" in source_kwargs:
            src_name = source_kwargs["id"]
            del source_kwargs["id"]
        source = source_cls(env=env, id=src_name, **source_kwargs)
        nodes.insert(0, source)
    else:
        source = None

    if sink_cls:
        sink_kwargs = sink_kwargs if sink_kwargs else {}.copy()
        sink_name = "Sink"
        if "id" in sink_kwargs:
            sink_name = sink_kwargs["id"]
            del sink_kwargs["id"]
        sink = sink_cls(env=env, id=sink_name, **sink_kwargs)
        nodes.append(sink)
    else:
        sink = None

    return nodes, edges, source, sink


def connect_nodes_with_buffers(machines, buffers, src, sink):
    """
    Connects source, machines, buffers, and optionally a sink in the following order:
    src -> buffer1 -> machine1 -> buffer2 -> machine2 -> ... -> bufferN -> sink

    Args:
        src: Source node
        machines: List of machine nodes
        buffers: List of buffer edges (should be len(machines) - 1) including source and sink
        sink: Optional sink node

    Returns:
        List of all nodes and buffers in connection order
    """
    assert len(buffers) == len(machines) - 1, "Number of buffers must be one more than number of machines"

    # Connect intermediate machines and buffers
    for i in range(1, len(machines)):
        buffers[i - 1].connect(machines[i - 1], machines[i])

    return machines, buffers
