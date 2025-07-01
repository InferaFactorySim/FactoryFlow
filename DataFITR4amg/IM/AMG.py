from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
#from langchain.chat_models import ChatOpenAI
from langserve import add_routes
from langchain.output_parsers.structured import ResponseSchema, StructuredOutputParser
import uvicorn
import os
from langchain_community.llms import Ollama
from dotenv import load_dotenv
import streamlit as st
import requests, re, os
import json
import google.generativeai as genai
import blockdiag.builder
import blockdiag.drawer
import blockdiag.parser
from langchain_google_genai.llms import GoogleGenerativeAI
import xml.etree.ElementTree as ET
import xml.dom.minidom
from PIL import Image, ImageDraw, ImageFont
import blockdiag.imagedraw.png

import base64

def render_image(filepath: str):
   """
   filepath: path to the image. Must have a valid file extension.
   """
   mime_type = filepath.split('.')[-1:][0].lower()
   with open(filepath, "rb") as f:
    content_bytes = f.read()
    content_b64encoded = base64.b64encode(content_bytes).decode()
    image_string = f'data:image/{mime_type};base64,{content_b64encoded}'
    st.image(image_string)




load_dotenv()

os.environ['OPENAI_API_KEY']=os.getenv("OPENAI_API_KEY")


def generate_blockdiag_code(components):
    try:
        components=str(components)
        components = components.replace("'", '"')
    except:
        st.write("error at replace",components)
    components = json.loads(components)
    #components = json.dumps(components)
    # if isinstance(components, str):
    #     components = json.loads(components)
    nodes = []
    edges = []

    for component in components:
        #st.write(component)
        component_id = component['id']
        if component['type'] == "ConveyorBelt":
            #label = f"Conveyorbelt: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}"
            label = f"Conveyor: {component_id}"
        elif component['type'] == "Machine":
            #label = f"Machine: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}"
            label = f"Machine: {component_id}"
        else:
            label = f"{component['type']}: {component_id}"
        
        nodes.append(f'{component_id} [label = "{label}"]')
        
        if 'inp' in component:
            if component['inp'] is not None and component['inp'].strip():
                for input_id in component['inp'].split():
                    edges.append(f'{input_id if input_id != "None" else f"None_{component_id}"} -> {component_id}')
            else:
                # Handle None or empty 'inp' explicitly
                edges.append(f'None_{component_id} -> {component_id}')

        # Process 'out' connections
        if 'out' in component:
            if component['out'] is not None and component['out'].strip():
                for output_id in component['out'].split():
                    edges.append(f'{component_id} -> {output_id if output_id != "None" else f"None_{component_id}"}')
            else:
                # Handle None or empty 'out' explicitly
                edges.append(f'{component_id} -> None_{component_id}')

    
    blockdiag_code = "blockdiag {\n"
    blockdiag_code += "    // Set labels to nodes.\n"
    blockdiag_code += "    " + "\n    ".join(nodes) + "\n"
    blockdiag_code += "    // Set labels to edges.\n"
    blockdiag_code += "    " + "\n    ".join(edges) + "\n"
    blockdiag_code += "}"
    #print("ll",blockdiag_code)
    return blockdiag_code


def generate_blockdiag_code_old(components):
    try:
        components=str(components)
        components = components.replace("'", '"')
    except:
        st.write("error at replace",components)
    components = json.loads(components)
    nodes = []
    edges = []

    for component in components:
        component_id = component['id']
        if component['type'] == "ConveyorBelt":
            label = f"Conveyorbelt: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}kW"
        elif component['type'] == "Machine":
            label = f"Machine: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}kW"
        else:
            label = f"{component['type']}: {component_id}"
        
        nodes.append(f'{component_id} [label = "{label}",size=24]')
        
        if 'inp' in component :
            for input_id in component['inp'].split():
                edges.append(f'{input_id} -> {component_id}')
        
        if 'out' in component  :
            for output_id in component['out'].split():
                edges.append(f'{component_id} -> {output_id}')
    
    blockdiag_code = "blockdiag {\n"
    blockdiag_code += "    // Set labels to nodes.\n"
    blockdiag_code += "    " + "\n    ".join(nodes) + "\n"
    blockdiag_code += "    // Set labels to edges.\n"
    blockdiag_code += "    " + "\n    ".join(edges) + "\n"
    blockdiag_code += "}"
    
    return blockdiag_code


def blockdiagdraw(diagram_definition):
    tree = blockdiag.parser.parse_string(diagram_definition)

    diagram = blockdiag.builder.ScreenNodeBuilder.build(tree)
    #blockdiag.imagedraw.png.ImageDrawEx.textsize = custom_textsize
     # Create a fontmap with larger font size
 

    # Draw the diagram to an image file
    #print("hola",tree)
    drawer = blockdiag.drawer.DiagramDraw('PNG', diagram, filename="diagram1.png")
  
    drawer.draw()
    drawer.save()


def validatedescriptionwithllm(description):
    load_dotenv()

    # Load Google API key from environment variable
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
   
    # Initialize the LLM using Google Generative AI (Gemini Pro)
    llm = GoogleGenerativeAI(google_api_key=GOOGLE_API_KEY, model="gemini-2.5-pro-exp-03-25")

    # First, validate if the description is related to a manufacturing system
    validation_prompt = f"""
    The following text describes a system. Does this description pertain to a manufacturing system? Reply with Yes or No.
   
    Description: {description}
    """

    # LLM call to validate the description
    validation_response = llm.predict(validation_prompt)
   
    # Extract and clean the response
    is_valid = validation_response.strip().lower() == "yes"
   
    if not is_valid:
        # If the description is not valid, return False
        return False 
    else:
        return True

def askllm(description,column_names,parameter_dict):
    load_dotenv()
    ##ollama llama2
    GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
    app=FastAPI(title="Langchain Server",version="1.0",decsription="A simple API Server")



    #llm=GoogleGenerativeAI(google_api_key=GOOGLE_API_KEY,model="gemini-2.5-pro-exp-03-25")
    llm=GoogleGenerativeAI(google_api_key=GOOGLE_API_KEY,model="gemini-2.5-flash-preview-05-20")
    #prompt2=ChatPromptTemplate.from_template("Write me an poem about {topic} for a 5 years child with 100 words")
    sample=[
        {
            "id": "Conveyor",
            "blocking": "False",
            "type": "ConveyorBelt",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "src_node": "Machine31",
            "dest_node": "Splitter21",
           
        },
         {
            "id": "Conveyor",
            "blocking": "True",
            "type": "ConveyorBelt",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "src_node": "Machine31",
            "dest_node": "sink",
            
        },
        
         {
            "id": "Buffer",
            "type": "Buffer",
            "delay":0,
            "src_node": "Store1",
            "dest_node": "Machine31",
           "mode": "FIFO",
            "store_capacity": 10, #Matching 'store_capacity' with relevant column name from
        },
        {
            "id": "mac1",
            "type": "Machine",
            "in_edges" : ["src"], # it is the starting component
            "out_edges": ["mac2"],
            "processing_delay": "{arrival_rate_column}",
        },
          {
            "id": "mac12",
            "type": "Machine",
            "out_edges" : ["sink"], # it is the ending component
            "processing_delay": "{arrival_rate_column}",
            "in_edges": ["mac21"],
            "power": "{machine_power_column}"#Matching 'power' with relevant column name from column_names list
        },
        {
            "id": "Machine31",
            "type": "Machine",
            "processing_delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "in_edges": ["Store1","Splitter21"],
            "out_edges": ["Conveyorbelt11"],
            "power": "{machine_power_column}"#Matching 'power' with relevant column name from column_names list
        },
        {
            "id": "Store1",
            "type": "buffer",

            "src_dest": "Machine31",
            "store_capacity": 10, #Matching 'store_capacity' with relevant column name from
            "dest_node": "Splitter21",
        },
        {
            "id": "Splitter21",
            "type": "Splitter",
            "delay":"{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "power": "{Splitter_power_column}"#Matching 'power' with relevant column name from column_names list
        }

    ]


    sample_chain ={'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 
       'node_kwargs_list': [ {'id': f'Machine{10 + i + 1}', 'type': 'Machine', 
          'processing_delay': f'{{M{ 10 + i + 1}_processing_delay}}', 
          'in_edges':[ f'Buffer{ 10 + i}'], 'out_edges': [f'Buffer{ 10 + i + 1}'],'work_capacity':1,'in_edge_selection':"FIRST_AVAILABLE",'OUT_edge_selection':"FIRST_AVAILABLE" } for i in range(10)], 'edge_kwargs_list': [{'id': f'Buffersrc_11', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine11','dest_node': f'Machine12' },
                           {'id': f'Buffer11_12', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine11','dest_node': f'Machine12' },
                           {'id': f'Buffer12_13', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer13_14', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer14_15', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer15_16', 'type': 'Buffer',  "store_capacity": 4, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer16_17', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer17_18', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer18_19', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer19_20', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer20_sink', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},], 'prefix': 'Machine', 'edge_prefix': 'Buffer', 'connection_pattern': 'chain', 
                           'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges',"work_capacity", "in_edge_selection", "out_edge_selection"],  # Node attributes
    'column_edges_names': ['id', 'type', 'store_capacity', 'src_node','dest_node', ],  # Edge attributes
                            'parameter_source': 'folder_location'}
                    

    
    sample_chains_in_parallel_data = {
    'count': 10,  # Each chain will have 10 machines
    'parallel_chains': 3,  # Representing 3 parallel chains
    'node_cls': 'Machine',  # Node class (Machine)
    'edge_cls': 'Buffer',    # Edge class (Buffer)
    
    # Whether to use a common source or not
    'common_source': True,  # Set True if all chains share the same source, False otherwise
    'common_sink': True,    # Set True if all chains share the same sink, False otherwise
    
    # Node kwargs list for each chain (replicating 10 machines per chain)
    'node_kwargs_list': [
        [{'id': f'Machine{chain * 10 + i + 1}', 'type': 'Machine', 
          'processing_delay': f'{{M{chain * 10 + i + 1}_processing_delay}}', 
          'in_edges':[ f'Buffer{chain * 10 + i}'], 'out_edges': [f'Buffer{chain * 10 + i + 1}'],'work_capacity':1,'in_edge_selection':"FIRST_AVAILABLE",'OUT_edge_selection':"FIRST_AVAILABLE" } for i in range(10)]
        for chain in range(3)  # Repeat for 3 parallel chains
    ],
    
    # Edge kwargs list for each chain (replicating 10 buffers per chain)
    'edge_kwargs_list': [ [{'id': f'Buffersrc_11', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine11','dest_node': f'Machine12' },
                           {'id': f'Buffer11_12', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine11','dest_node': f'Machine12' },
                           {'id': f'Buffer12_13', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer13_14', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer14_15', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer15_16', 'type': 'Buffer',  "store_capacity": 4, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer16_17', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer17_18', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer18_19', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer19_20', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},
                           {'id': f'Buffer20_sink', 'type': 'Buffer',  "store_capacity": 2, 'src_node': f'Machine12' , 'dest_node': f'Machine13'},]
        for chain in range(3)  # Repeat for 3 parallel chains
    ],
    
    'prefix': 'Machine',   # Prefix for machines (e.g., "Machine1")
    'edge_prefix': 'Buffer',  # Prefix for buffers (e.g., "Buffer1")
    'connection_pattern': 'chain',  # Connection pattern for each chain
    'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges',"work_capacity", "in_edge_selection", "out_edge_selection"],  # Node attributes
    'column_edges_names': ['id', 'type', 'store_capacity', 'src_node','dest_node', ],  # Edge attributes
    'parameter_source': 'folder_location',  # Location of parameters
}

    resp_schema_netlist = ResponseSchema(
    name="netlist",
    description=(
        "Generate a list of component dictionaries (`netlist`) based on the user's description of a manufacturing system or a dict of component details in the same name 'netlist depending on the input. "
        "Use the attribute names exactly as mentioned in the column names. Each dictionary represents a component such as a Machine, Buffer, ConveyorBelt, etc.\n\n"
        
        "If the description contains phrases like 'a chain of N machines and buffers', then build a chain of alternating node-edge pairs using the format provided in `sample_chain`.\n\n"
        
        "For all components, use placeholders from the column names and replace them with actual values using the `parameter_dict`. "
        "For example, if a component uses `\"delay\": \"{arrival_rate_column}\"`, replace `{arrival_rate_column}` with the corresponding value from `parameter_dict`.\n\n"

        "Always output in valid Python list-of-dictionaries format. Use double quotes for keys and string values. "
        "Here's an example format:\n"
        f"{sample}\n\n"
        "If the user is saying , 3 machines are connected in series or 3 machines are connected serially or 3 machines are connected as chain, etc it's a chain pattern, extract all the details from the description and the csv file like node prefix to be used, edge prfix to be used. Use this style to generate the answer:\n"
        f"{sample_chain} and store it inside 'netlist' name as the key\n\n "
        "If the user is saying , 10 machines are connected in series or 10 machines are connected serially or 10 machines are connected as chain, etc and that 3 such chains are present parallely with a common source and common sink, then it's a chain pattern, and one chain is repeated 4 times, extract all the details from the description and the csv file like node prefix to be used, edge prfix to be used. Use this style to generate the answer:\n"
        f"{sample_chains_in_parallel_data} and store it inside 'netlist' name as the key. it should have a key 'parallel', and create a list appropriately.\n\n "  
       f"For in_edge_selection and out_edge_selection, use 'FIRST_AVAILABLE' as the default value if not specified in the description or in the csv, if there is a data in csv, use that if it is 0,1,2, some sequence use 'ROUND_ROBIN'. Extract the buffer names as suggested by the user strictly. "
       f" please get the 'id' for all the node and buffers based on the description sprovided. "
))
    
    
    resp_schemas=[resp_schema_netlist]
    std_output_parser= StructuredOutputParser.from_response_schemas(resp_schemas)
    std_format_response_parser= std_output_parser.get_format_instructions()


    column_names_str = ", ".join(column_names)
    std_output_response_prompt_template = """Extract data from the description and column names and parameter_dictionary provided.

    Description: {Description}
    
    Column Names: {ColumnNames}

    parameter_dictionary: {parameter_dict}

    {format_instructions}
    """
    
    # Prepare the prompt for the first output parser (netlist and XML)
    std_promptforoutputparser = PromptTemplate(
        template=std_output_response_prompt_template,
        input_variables=["Description", "ColumnNames", "parameter_dict"],
        partial_variables={"format_instructions": std_format_response_parser}
    )
    
  
    #add_routes(app,prompt2|llm|std_output_parser,path="/llmpath")
    outputchain= std_promptforoutputparser|llm|std_output_parser
    #outputchain= std_promptforoutputparser|llm
    #opchain2=std_promptforoutputparserfinal|llm|std_output_parserfinal
    

    
    prompt_text = (
    f"Description: {description}\n"
    f"ColumnNames: {column_names_str}\n"
    f"parameter_dict: {parameter_dict}\n"
)

    
    

    

    structured_data = outputchain.invoke({"Description": description,"ColumnNames": column_names_str,"parameter_dict":parameter_dict})
    print("Structured Data:", structured_data)
    
    #--------------code for output and input token count
    # model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")  # Adjust the model name as needed
    # # # Tokenize the prompt text
    # tokens = model.count_tokens(prompt_text)
    # print(f"Token count: {tokens.total_tokens}")
    # st.write(f"Token count: {tokens.total_tokens}")
    # responsefromllm=model.generate_content(prompt_text)
    # usage = responsefromllm.usage_metadata
    # st.write("Response from LLM:", responsefromllm.text)
    # st.write("Raw Structured Data:-----", usage)
    # structured_data = responsefromllm.text
    # st.write("Structured Data:", structured_data)
    #---------------------------------------------
    

    if structured_data:
    
        components_str = structured_data['netlist']
        
        
        return components_str
        
        
        
 
            
           
         
