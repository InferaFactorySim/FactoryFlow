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




def get_node_by_id(nodes, node_id):
    for node in nodes:
        if getattr(node, 'id', None) == node_id:
            return node
    return None

def simulation_engine_m2(data):
    print("Starting simulation engine M2...")
    
    # Set the delay folder dynamically
    #delay_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../gencodeforAMG_10'))
    delay_folder =     os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../gencodeforAMG_10'))
    if "count" in data:
        count = data['count']
        env = simpy.Environment()
        #print(data)

        # Extract prefix from data (if it exists), otherwise default to 'Machine'
       

        # Extract node_cls and edge_cls from data, otherwise default to Machine and Buffer
        node_cls = data.get('node_cls', Machine)
        edge_cls = data.get('edge_cls', Buffer)
        machines=[]
        
        original_node_kwargs = data.get('node_kwargs_list', [])
        for i in range(len(original_node_kwargs)):
         
            machine_id = original_node_kwargs[i]['id']
            processing_delay_file = f"{machine_id}_processing_delay_code.py"
            in_edge_selection_file = f"{machine_id}_in_edge_selection_code.py"
            out_edge_selection_file = f"{machine_id}_out_edge_selection_code.py"
            
            processing_delay = load_processing_delay_from_file(processing_delay_file, delay_folder)
            #in_edge_selection= load_processing_delay_from_file(in_edge_selection_file, delay_folder)
            
            out_edge_selection= load_processing_delay_from_file(out_edge_selection_file, delay_folder)  

            in_edge_selection="FIRST_AVAILABLE"
            #out_edge_selection="FIRST_AVAILABLE"
            #print(original_node_kwargs[i])
            if original_node_kwargs[i]['type']== 'Machine':
                
                   
                    work_capacity= int(original_node_kwargs[i].get('work_capacity', None))

                    node_setup_time= original_node_kwargs[i].get('node_setup_time', 0)
                
                    machines.append(Machine(env, id=machine_id, work_capacity=work_capacity,processing_delay=processing_delay,in_edge_selection=in_edge_selection, out_edge_selection=out_edge_selection ))

        src=Source(env, id="src", inter_arrival_time=0.2, blocking=True, out_edge_selection="FIRST_AVAILABLE")
        sink= Sink(env,id="sink")
        machines.insert(0,src)
        machines.append(sink)
        #print([i.id for i in machines])
            
            
           

        buffers=[]
        original_edge_kwargs = data.get('edge_kwargs_list', [])
        #print(original_edge_kwargs)
        for i in range(len(original_edge_kwargs)):

            buffer_id = original_edge_kwargs[i]['id']
            #print(buffer_id)
            store_capacity= int(original_edge_kwargs[i].get('store_capacity', 2))
            delay= original_edge_kwargs[i].get('delay', 0)
            mode= original_edge_kwargs[i].get('mode', 'FIFO')
            src_node= original_edge_kwargs[i].get('src_node', None)
            dest_node= original_edge_kwargs[i].get('dest_node', None)
            if original_edge_kwargs[i]['type']== 'Buffer':
                b=Buffer(env,id=buffer_id,store_capacity=store_capacity,delay=delay, mode=mode) 
              
                src_node=get_node_by_id(machines, src_node)
                print(dest_node)
                dest_node=get_node_by_id(machines, dest_node)
                print(dest_node)
                    
                b.connect(src_node,dest_node)  

                buffers.append(b)



      




        sim_time = 10000
        

        import time

        start_time = time.time()

        

        env.run(until=sim_time)
        end_time = time.time()


        print(f"Simulation {sim_time} ran for {end_time - start_time:.2f} seconds.")

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
            print(f"\nMachine {machine.id} state times: {machine.stats['total_time_spent_in_states']}")
            print(f"Total items processed: {machine.stats['num_item_processed']}")
            print(machine.time_per_work_occupancy)
            print("per_thread_total_time_in_processing_state", machine.per_thread_total_time_in_processing_state)
            print("per_thread_total_time_in_blocked_state", machine.per_thread_total_time_in_blocked_state)

        for buf in buffers:
            print(f"Time-averaged number of items in {buf.id}: {buf.stats['time_averaged_num_of_items_in_buffer']}")

        return sink.stats['num_item_received'] / env.now





# data={'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 'node_kwargs_list': [
# {'id': 'M1', 'type': 'Machine', 'processing_delay': '{M1_processing_delay}', 'in_edges': ['B_src_1'], 'out_edges': ['B_1_2'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 
# {'id': 'M2', 'type': 'Machine', 'processing_delay': '{M2_processing_delay}', 'in_edges': ['B_1_2'], 'out_edges': ['B_2_3'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M3', 'type': 'Machine', 'processing_delay': '{M3_processing_delay}', 'in_edges': ['B_2_3'], 'out_edges': ['B_3_4'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 
# {'id': 'M4', 'type': 'Machine', 'processing_delay': '{M4_processing_delay}', 'in_edges': ['B_3_4'], 'out_edges': ['B_4_5'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'},

#  {'id': 'M5', 'type': 'Machine', 'processing_delay': '{M5_processing_delay}', 'in_edges': ['B_4_5'], 'out_edges': ['B_5_6_1'], 'work_capacity': 3, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 

# {'id': 'M6', 'type': 'Machine', 'processing_delay': '{M6_processing_delay}', 'in_edges': ['B_5_6_1'], 'out_edges': ['B_6_7'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M7', 'type': 'Machine', 'processing_delay': '{M7_processing_delay}', 'in_edges': ['B_6_7'], 'out_edges': ['B_7_8'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M8', 'type': 'Machine', 'processing_delay': '{M8_processing_delay}', 'in_edges': ['B_7_8'], 'out_edges': ['B_8_9'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M9', 'type': 'Machine', 'processing_delay': '{M9_processing_delay}', 'in_edges': ['B_8_9'], 'out_edges': ['B_9_10'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M10', 'type': 'Machine', 'processing_delay': '{M10_processing_delay}', 'in_edges': ['B_9_10'], 'out_edges': ['B_10_sink'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}], 'edge_kwargs_list': [{'id': 'B_src_1', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'src', 'dest_node': 'M1'}, {'id': 'B_1_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M1', 'dest_node': 'M2'}, {'id': 'B_2_3', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M2', 'dest_node': 'M3'}, {'id': 'B_3_4', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M3', 'dest_node': 'M4'}, {'id': 'B_4_5', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M4', 'dest_node': 'M5'}, {'id': 'B_5_6_1', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_3', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'},

#  {'id': 'B_5_6_4', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, 
# {'id': 'B_6_7', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M6', 'dest_node': 'M7'},
#  {'id': 'B_7_8', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M7', 'dest_node': 'M8'}, {'id': 'B_8_9', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M8', 'dest_node': 'M9'}, {'id': 'B_9_10', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M9', 'dest_node': 'M10'}, {'id': 'B_10_sink', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M10', 'dest_node': 'sink'}], 'prefix': 'Machine', 'edge_prefix': 'Buffer', 'connection_pattern': 'chain', 'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges', 'work_capacity', 'in_edge_selection', 'out_edge_selection'], 'column_edges_names': ['id', 'type', 'store_capacity', 'src_node', 'dest_node'], 'parameter_source': 'folder_location'}




data={'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 
      'node_kwargs_list': [
          {'id': 'M1', 'type': 'Machine', 'processing_delay': '{M1_processing_delay}', 'in_edges': ['B_src_1'], 'out_edges': ['B_1_2'], 'work_capacity': 1, 'in_edge_selection': '{M1_in_edge_selection}', 'out_edge_selection': '{M1_out_edge_selection}'},
         {'id': 'M2', 'type': 'Machine', 'processing_delay': '{M2_processing_delay}', 'in_edges': ['B_1_2'], 'out_edges': ['B_2_3'], 'work_capacity': 1, 'in_edge_selection': '{M2_in_edge_selection}', 'out_edge_selection': '{M2_out_edge_selection}'}, 
         {'id': 'M3', 'type': 'Machine', 'processing_delay': '{M3_processing_delay}', 'in_edges': ['B_2_3'], 'out_edges': ['B_3_4'], 'work_capacity': 1, 'in_edge_selection': '{M3_in_edge_selection}', 'out_edge_selection': '{M3_out_edge_selection}'}, 
         {'id': 'M4', 'type': 'Machine', 'processing_delay': '{M4_processing_delay}', 'in_edges': ['B_3_4'], 'out_edges': ['B_4_5'], 'work_capacity': 1, 'in_edge_selection': '{M4_in_edge_selection}', 'out_edge_selection': '{M4_out_edge_selection}'}, 
         {'id': 'M5', 'type': 'Machine', 'processing_delay': '{M5_processing_delay}', 'in_edges': ['B_4_5'], 'out_edges': ['B_5_6_1', 'B_5_6_2', 'B_5_6_3', 'B_5_6_4'], 'work_capacity': 3, 'in_edge_selection': '{M5_in_edge_selection}', 'out_edge_selection': '{M5_out_edge_selection}'}, 
         {'id': 'M6', 'type': 'Machine', 'processing_delay': '{M6_processing_delay}', 'in_edges': ['B_5_6_1', 'B_5_6_2', 'B_5_6_3', 'B_5_6_4'], 'out_edges': ['B_6_7'], 'work_capacity': 1, 'in_edge_selection': '{M6_in_edge_selection}', 'out_edge_selection': '{M6_out_edge_selection}'},  
         {'id': 'M7', 'type': 'Machine', 'processing_delay': '{M7_processing_delay}', 'in_edges': ['B_6_7'], 'out_edges': ['B_7_8'], 'work_capacity': 1, 'in_edge_selection': '{M7_in_edge_selection}', 'out_edge_selection': '{M7_out_edge_selection}'},
         {'id': 'M8', 'type': 'Machine', 'processing_delay': '{M8_processing_delay}', 'in_edges': ['B_7_8'], 'out_edges': ['B_8_9'], 'work_capacity': 1, 'in_edge_selection': '{M8_in_edge_selection}', 'out_edge_selection': '{M8_out_edge_selection}'}, 
         {'id': 'M9', 'type': 'Machine', 'processing_delay': '{M9_processing_delay}', 'in_edges': ['B_8_9'], 'out_edges': ['B_9_10'], 'work_capacity': 1, 'in_edge_selection': '{M9_in_edge_selection}', 'out_edge_selection': '{M9_out_edge_selection}'}, 
         {'id': 'M10', 'type': 'Machine', 'processing_delay': '{M10_processing_delay}', 'in_edges': ['B_9_10'], 'out_edges': ['B_10_sink'], 'work_capacity': 1, 'in_edge_selection': '{M10_in_edge_selection}', 'out_edge_selection': '{M10_out_edge_selection}'}], 
     'edge_kwargs_list': [
         {'id': 'B_src_1', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'src', 'dest_node': 'M1'},
           {'id': 'B_1_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M1', 'dest_node': 'M2'}, 
           {'id': 'B_2_3', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M2', 'dest_node': 'M3'},
             {'id': 'B_3_4', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M3', 'dest_node': 'M4'},
               {'id': 'B_4_5', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M4', 'dest_node': 'M5'},
                 {'id': 'B_5_6_1', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'},
                   {'id': 'B_5_6_2', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'},
                     {'id': 'B_5_6_3', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, 
                     {'id': 'B_5_6_4', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'},
                       {'id': 'B_6_7', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M6', 'dest_node': 'M7'}, 
                       {'id': 'B_7_8', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M7', 'dest_node': 'M8'},
                         {'id': 'B_8_9', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M8', 'dest_node': 'M9'}, 
                         {'id': 'B_9_10', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M9', 'dest_node': 'M10'},
                           {'id': 'B_10_sink', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M10', 'dest_node': 'sink'}], 'prefix': 'M', 'edge_prefix': 'B', 'connection_pattern': 'chain', 'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges', 'work_capacity', 'in_edge_selection', 'out_edge_selection'], 'column_edges_names': ['id', 'type', 'store_capacity', 'src_node', 'dest_node'], 'parameter_source': 'folder_location'}


#data ={'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 'node_kwargs_list': [{'id': 'M1', 'type': 'Machine', 'processing_delay': '{M1_processing_delay}', 'in_edges': ['B_src_1'], 'out_edges': ['B_1_2'], 'work_capacity': 1, 'in_edge_selection': '{M1_in_edge_selection}', 'out_edge_selection': '{M1_out_edge_selection}'}, {'id': 'M2', 'type': 'Machine', 'processing_delay': '{M2_processing_delay}', 'in_edges': ['B_1_2'], 'out_edges': ['B_2_3'], 'work_capacity': 1, 'in_edge_selection': '{M2_in_edge_selection}', 'out_edge_selection': '{M2_out_edge_selection}'}, {'id': 'M3', 'type': 'Machine', 'processing_delay': '{M3_processing_delay}', 'in_edges': ['B_2_3'], 'out_edges': ['B_3_4'], 'work_capacity': 1, 'in_edge_selection': '{M3_in_edge_selection}', 'out_edge_selection': '{M3_out_edge_selection}'}, {'id': 'M4', 'type': 'Machine', 'processing_delay': '{M4_processing_delay}', 'in_edges': ['B_3_4'], 'out_edges': ['B_4_5'], 'work_capacity': 1, 'in_edge_selection': '{M4_in_edge_selection}', 'out_edge_selection': '{M4_out_edge_selection}'}, {'id': 'M5', 'type': 'Machine', 'processing_delay': '{M5_processing_delay}', 'in_edges': ['B_4_5'], 'out_edges': ['B_5_6_1', 'B_5_6_2', 'B_5_6_3', 'B_5_6_4'], 'work_capacity': 3, 'in_edge_selection': '{M5_in_edge_selection}', 'out_edge_selection': '{M5_out_edge_selection}'}, {'id': 'M6', 'type': 'Machine', 'processing_delay': '{M6_processing_delay}', 'in_edges': ['B_5_6_1', 'B_5_6_2', 'B_5_6_3', 'B_5_6_4'], 'out_edges': ['B_6_7'], 'work_capacity': 1, 'in_edge_selection': '{M6_in_edge_selection}', 'out_edge_selection': '{M6_out_edge_selection}'}, {'id': 'M7', 'type': 'Machine', 'processing_delay': '{M7_processing_delay}', 'in_edges': ['B_6_7'], 'out_edges': ['B_7_8'], 'work_capacity': 1, 'in_edge_selection': '{M7_in_edge_selection}', 'out_edge_selection': '{M7_out_edge_selection}'}, {'id': 'M8', 'type': 'Machine', 'processing_delay': '{M8_processing_delay}', 'in_edges': ['B_7_8'], 'out_edges': ['B_8_9'], 'work_capacity': 1, 'in_edge_selection': '{M8_in_edge_selection}', 'out_edge_selection': '{M8_out_edge_selection}'}, {'id': 'M9', 'type': 'Machine', 'processing_delay': '{M9_processing_delay}', 'in_edges': ['B_8_9'], 'out_edges': ['B_9_10'], 'work_capacity': 1, 'in_edge_selection': '{M9_in_edge_selection}', 'out_edge_selection': '{M9_out_edge_selection}'}, {'id': 'M10', 'type': 'Machine', 'processing_delay': '{M10_processing_delay}', 'in_edges': ['B_9_10'], 'out_edges': ['B_10_sink'], 'work_capacity': 1, 'in_edge_selection': '{M10_in_edge_selection}', 'out_edge_selection': '{M10_out_edge_selection}'}], 'edge_kwargs_list': [{'id': 'B_src_1', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'src', 'dest_node': 'M1'}, {'id': 'B_1_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M1', 'dest_node': 'M2'}, {'id': 'B_2_3', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M2', 'dest_node': 'M3'}, {'id': 'B_3_4', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M3', 'dest_node': 'M4'}, {'id': 'B_4_5', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M4', 'dest_node': 'M5'}, {'id': 'B_5_6_1', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_3', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_4', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_6_7', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M6', 'dest_node': 'M7'}, {'id': 'B_7_8', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M7', 'dest_node': 'M8'}, {'id': 'B_8_9', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M8', 'dest_node': 'M9'}, {'id': 'B_9_10', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M9', 'dest_node': 'M10'}, {'id': 'B_10_sink', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M10', 'dest_node': 'sink'}], 'prefix': 'M', 'edge_prefix': 'B', 'connection_pattern': 'chain', 'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges', 'work_capacity', 'in_edge_selection', 'out_edge_selection'], 'column_edges_names': ['id', 'type', 'store_capacity', 'src_node', 'dest_node'], 'parameter_source': 'folder_location'}
#simulation_engine_m2(data)