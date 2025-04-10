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
            label = f"Conveyorbelt: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}"
        elif component['type'] == "Machine":
            label = f"Machine: {component_id}\\nDelay: {component['delay']}s\\nPower: {component['power']}"
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
        
        nodes.append(f'{component_id} [label = "{label}"]')
        
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



    llm=GoogleGenerativeAI(google_api_key=GOOGLE_API_KEY,model="gemini-2.5-pro-exp-03-25")
    #prompt2=ChatPromptTemplate.from_template("Write me an poem about {topic} for a 5 years child with 100 words")
    sample=[
        {
            "id": "Conveyorbelt",
            "type": "ConveyorBelt",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "inp": "Machine31",
            "out": "Split21",
            "power": "{conveyor_power_column}"#Matching 'power' with relevant column name from column_names list
        },
         {
            "id": "Buffer",
            "type": "Buffer",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "inp": "Store1",
            "out": "Machine31",
            "power": "{Machine31_power_column}"#Matching 'power' with relevant column name from column_names list
        },
        {
            "id": "mac1",
            "type": "Processor",
            "inp" : "None", # it is the starting component
            "out": "mac2",
            "power": "{machine_power_column}"#Matching 'power' with relevant column name from column_names list
        },
          {
            "id": "mac12",
            "type": "Processor",
            "out" : "None", # it is the ending component
            "inp": "mac21",
            "power": "{machine_power_column}"#Matching 'power' with relevant column name from column_names list
        },
        {
            "id": "Machine31",
            "type": "Processor",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "inp": "Store1 Split21",
            "out": "Conveyorbelt11",
            "power": "{machine_power_column}"#Matching 'power' with relevant column name from column_names list
        },
        {
            "id": "Store1",
            "type": "Store",
            "delay": "{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "power": "{store_power_column}"#Matching 'power' with relevant column name from column_names list

        },
        {
            "id": "Split21",
            "type": "Split",
            "delay":"{arrival_rate_column}", #Matching 'delay' with relevant column name from column_names list
            "power": "{split_power_column}"#Matching 'power' with relevant column name from column_names list
        }
    ]
    #resp_schema_xmlstruc=ResponseSchema(name="xmlstruc", description="xml structure created using the components extracted from description given by user. An example is" + str(sample))
    resp_schema_xmlstruc=ResponseSchema(name="xmlstruc", description="xml structure created using the components extracted from description given by user. ")
    resp_schema_netlist=ResponseSchema(name="netlist", description="python netlist without any names just as a list of dictionary objects created using the components and column names given in the description given by user output should be in format as a list of dictionary objects with component's attributes as keys and attribute's value as value 2. a xml code created using the components extracted from description given by user.Always use the same attribute names given in the description Let all variables be put inside double quotes. An example is" + str(sample)+"Using the provided column names and parameter dictionary, generate a list of component dictionaries where each component has its delay, power, etc. attributes replaced with actual values from the Fit Parameters dictionary. If a component’s attribute refers to a placeholder like {arrival_rate_column}, replace it with the corresponding value from the parameter dictionary.")
    resp_schema_simpycode=ResponseSchema(name="simpycode", description="Python Simpy based code to simulate the manufacturing plant described by the user using the components in the description for doing discrete-event simulation. This can be done using the update netlist provided by the user and add logging using print statements in python after every step of simulation.")
    resp_schemas=[resp_schema_xmlstruc,resp_schema_netlist]
    std_output_parser= StructuredOutputParser.from_response_schemas(resp_schemas)
    std_format_response_parser= std_output_parser.get_format_instructions()


    std_output_parserfinal= StructuredOutputParser.from_response_schemas([resp_schema_simpycode])
    std_format_response_parserfinal= std_output_parserfinal.get_format_instructions()
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
    
    # Prepare the prompt for Simpy code generation
    std_promptforoutputparserfinal = PromptTemplate(
        template=std_output_response_prompt_template,
        input_variables=["Description", "ColumnNames"],
        partial_variables={"format_instructions": std_format_response_parserfinal}
    )
    #add_routes(app,prompt2|llm|std_output_parser,path="/llmpath")
    outputchain= std_promptforoutputparser|llm|std_output_parser
    opchain2=std_promptforoutputparserfinal|llm|std_output_parserfinal
   
    structured_data = outputchain.invoke({"Description": description,"ColumnNames": column_names_str,"parameter_dict":parameter_dict})
    # Debugging: Log the raw structured data to inspect its format
    print("Raw Structured Data:", structured_data)
    if structured_data:
    
        components_str = structured_data['netlist']
        
        
        return components_str
        
        
        
 
            
           
         
