#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 11:14:15 2023

@author: lekshmi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import DataFITR.DataFITR4amg.IM.AMG as AMG
import ast
from IM import AMG
import json
#from IM.makenetlist import Netlist

import matplotlib.pyplot as plt
from scipy import stats

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pickle
import sys,io,os
import streamlit as st
import pandas as pd
import scipy.stats as stats,time
from io import StringIO
import re

#sys.path.append('/home/lekshmi/Downloads/my_app/IM') 
sys.path.append('./IM') 
sys.path.append(os.path.abspath(os.path.dirname('AMGUI.py')))
#import modular_IM
from IM import modular_IM
from IM import kde_silverman_both
from IM import datagenforDataFITR
from IM import SimulationEngine
from IM import simultest
from IM import simulationengine_m3
from IM.model_visualiser import visualize_graph

#from IM.SimulationEngine import simulation_engine

from IM import makenetlist
#from IM import model_visualiser
#from IM.makenetlist import Netlist
#import kde_silverman_both
#fromm IM import wrapper
import math
import re
import IM
from IM import listparamsofdistributions
import numpy as np
#from statsmodels.tsastattools import adfuller
import seaborn as sns
from scipy.stats import pearsonr #to calculate correlation coefficient



#@st.cache(suppress_st_warning=(True))
def my_function(data,distlist,distributions,typ,dist='my1 distribution',bins=100,gof="ks",kde_bin=50):
    #st.write("Please wait while I fit your data")
    #modelGUI=modular_IM.modelmatch()
    #st.write(data[0:5],type(data[0]))
    if len(np.unique(np.array(data)))==1:
        #st.write("chakkakakakkaka")
        restyp='constant'
        result=list()
        plotdata="nill"
        pval=data[0]
        return  restyp,result, plotdata,pval
    #st.write("hdhhdhdhdhdh")
    modelGUI=modular_IM.modelmatch(data ,typ,dist,bins,gof,distlist,distributions,kde_bin)
    #st.write(modelGUI.data)
    plotdata,pval=modelGUI.bestfit(distlist,distributions)
    result,SSEresult=modelGUI.printresult()
    #result.rename({'key_0': 'Test'}, axis=1, inplace=True)
    
    #st.write(pd.DataFrame(plotdata))
    restyp='nonconstant'
    
    
    
    #st.write(plotdata)
    #st.write("checkode")
    #st.write(list(result.index))
    #st.write(result)
    return restyp,result,plotdata,pval


    

#@st.cache(suppress_st_warning=(True))
def getbinsize():
    bin_size=st.text_input("Enter an approriate bin size for the data to plot histogram")
    if bin_size:
        return bin_size
    else:
        st.write("Enter a binsize to proceed")
        
#@st.cache(suppress_st_warning=(True))
def getcontinuousdist():
    Continuous_All=[]
    all_dist = [getattr(stats, d) for d in dir(stats) if isinstance(getattr(stats, d), stats.rv_continuous)]
    filtered = [x for x in all_dist if ((x.a <= 0) & (x.b == math.inf))]
    filtered=all_dist
    pat = r's.[a-zA-Z0-9_]+_g'
    
    for i in filtered:
        s = str(i)
        #print(s)
        span=re.search(pat, s).span()
        dist=s[span[0]+2:span[1]-2]
        Continuous_All.append(dist)
        
    for i in ['levy_stable','studentized_range','kstwo','skew_norm','vonmises','trapezoid','reciprocal','geninvgauss','able']:
        if i in Continuous_All: 
            Continuous_All.remove(i)
    return Continuous_All
#@st.cache
def getdiscretedist():
    discrete=['binom','geom']
    return discrete


def format_code_with_generator(output):
    import re
    lines = output.strip().splitlines()
    if len(lines) < 1:
        raise ValueError("Output must have at least one line.")

    last_assign = lines[-1]
    match = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)', last_assign)
    if not match:
        raise ValueError("Last line must be an assignment.")
    varname, rhs = match.group(1), match.group(2)

    # Check for np.random.binomial or similar (discrete)
    is_np_random = bool(re.search(r'np\.random\.(binomial|poisson|randint|geometric|hypergeometric|negative_binomial)', rhs))
    # Check for scipy.stats continuous distribution
    is_scipy_cont = bool(re.search(r'scipy\.stats\.\w+\(', rhs)) or bool(re.search(r'stats\.\w+\(', rhs))

    result = []
    result.append("def generate_data():")
    for line in lines[:-1]:
        result.append("    " + line)
    result.append("    " + last_assign)
    result.append("    while True:")
    if is_np_random:
        # Remove the size argument if present
        rhs_no_size = re.sub(r',\s*[^,()]+(?=\s*\))', '', rhs, count=1)
        result.append(f"        yield  {rhs_no_size}")
    elif is_scipy_cont:
        result.append(f"        yield {varname}.rvs()")
    else:
        result.append(f"        yield int({varname})")
    return "\n".join(result)
def format_code_with_generator1(output):
    
    lines = output.strip().splitlines()
    #st.write(output)
    if len(lines) < 1:
        raise ValueError("Output must have at least one line.")

    # Find the last assignment line (e.g., M1_delay=...)
    last_assign = lines[-1]
    match = re.match(r'\s*([A-Za-z_][A-Za-z0-9_]*)\s*=', last_assign)
    if not match:
        raise ValueError("Last line must be an assignment.")
    varname = match.group(1)

    # Compose the new code
    result = []
    result.append("def generate_data():")
    for line in lines[:-1]:
        result.append("    " + line)
    # Add the last assignment line
    result.append("    " + last_assign)
    result.append("    while True:")
    if len(lines) == 1:
        result.append(f"        yield {varname}")
    else:
        result.append(f"        yield {varname}.rvs()")
    return "\n".join(result)


def codefilewrite(inpvar,output):
    formatted_code = format_code_with_generator(output)
    folder_name = 'gencodeforAMG'
    file_name = inpvar + "_code.py"  # Construct file name dynamically based on inpvar
    folder_path = os.path.join(os.getcwd(), folder_name)  # Get current working directory and append folder name
    
    # Check if the folder exists, if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Construct the full file path
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(formatted_code)



def is_CSV(filename):
   #st.write(filename.split("."))
   return filename.split(".")[1]

def to_csv(df):
    data_csv = df.to_csv(path_or_buf=None, sep=',', index=False) 
    return data_csv

        
def checkdatatype1(df):
    for i in df.columns:
        if (df[i]).dtype  not in[ 'float','int','int64','int32','float64','float32']:
            st.write("Column ",i," is not a numerical column. Please convert the categorical columns to numerical values")
            return 0
    return 1
def checkdatatype(df):
    for i in df.columns:
        if not pd.api.types.is_numeric_dtype(df[i]):
            st.write("Column ",i," is not a numerical column. Please convert the categorical columns to numerical values")
            return 0
    return 1







def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def finddatatype_autofill_old(data):
    #g=[True if i**2== (int(i))**2 else False  for i in data]
    g=[True if (float(i)-abs(i))==0 else False  for i in data]
    #st.write(g)
    k="na"
    #st.write(data.dtype)
    if data.dtype in ['int64',  'int32']:
        k= 'Integer-Valued'
    elif False in g:
        k= 'Real-Valued'
    else:
        k= 'Real-Valued'
    return k


def finddatatype_autofill(data):
    import pandas as pd
    # If all values are integer (even if dtype is float), treat as integer-valued
    if pd.api.types.is_integer_dtype(data):
        return 'Integer-Valued'
    # If float, but all values are integer-like (e.g., 1.0, 2.0)
    elif pd.api.types.is_float_dtype(data) and (data.dropna() == data.dropna().astype(int)).all():
        return 'Integer-Valued'
    else:
        return 'Real-Valued'

def structanddraw(netlist):
    #st.write("NN",netlist)
    struct_diag=AMG.generate_blockdiag_code(netlist)
    #st.write(struct_diag)
    AMG.blockdiagdraw(struct_diag)   
     
    
    
    
    
def IM_uni(df):
   
    table_cols_fit=pd.DataFrame(columns=['column','dist','funcname'])  
    #st.header("Data Fitting")
    cols=list(['Chi squared Test','SSE','KStest'])
    goodnessoffit=st.selectbox("Select a goodness of fit measure to choose the best fit distribution",cols,key='goodnessoffit')
    if checkdatatype(df)==0:
 
        st.warning("All categorical columns should be converted to numerical values")
        return
    
    
    
    #st.header("Input Modeling for non correlated and time independent data")
    #st.caption("Use this if the data is non correlated and time independent")
    #st.markdown('<p class="big-font">Fit non correlated and time independent data', unsafe_allow_html=True)
        
    datadetailscol,histcol=st.columns(2)
    
    with datadetailscol:
        #check#dataname = st.text_input("Enter a name for the dataset",value="sample.csv",key='dataname')  
        #st.subheader("Fitting data columnwise")
        #st.warning("Choose a data column from the CSV file to fit/model")
        
        #inpvar = st.selectbox("Data column to fit", df.columns)
        
        for col in df.columns:
            inpvar=col
            datatype_col=finddatatype_autofill(df[inpvar])
            
            if datatype_col:
                #st.write("The datatype of the column is ",datatype_col)
        
        
        
                datatype_list=['Real-Valued','Integer-Valued']
                default_ind=datatype_list.index(datatype_col)
                #st.write(default_ind)
                
                Continuous_All=listparamsofdistributions.getcontinuousdist()
                Continuous_Popular=['expon','norm','lognorm','triang','uniform','weibull_min','gamma']
                Discrete_Popular=['binom','geom']
            

                #st.write("datatype_col",datatype_col)
                #st.sidebar.write("Dataset name:",dataname)
                datatyp='na'
                distlist=[]
                distributions=[]
                if datatype_col=='Real-Valued':
                    datatyp='continuous'
                    distlist_userselect = Continuous_Popular
                    distlist.append('continuous')
                    distributions.append(Continuous_Popular)
                else:
                    datatyp='discrete'
                    distlist_userselect = Discrete_Popular
                    distlist.append('discrete')
                    distributions.append(Discrete_Popular)
        
               
                
                datalen=len(df[inpvar])
                defaultbins=min((1+np.ceil(np.log(datalen))),max(100,datalen/10))
                bins=int(defaultbins)
                #st.write(distlist, distributions)
                restyp,finresult,plotdata,pval=my_function(df[inpvar],distlist,distributions,datatyp,inpvar,bins,'ks')
                if restyp=='constant':
                    
                    constdict={"column":inpvar,"value":[pval],'type':['constant']}
                    constdf=pd.DataFrame(constdict)
                    constantname=inpvar+'constant'
                    #table_cols_fit
                    output=str(inpvar)+"= "+str(pval)
                    codefilewrite(inpvar,output)
                    
                    
                else:
                    
                    result_df = finresult.sort_values(by = goodnessoffit)
                    up_df=result_df.copy() 
                    st.session_state['df']=up_df          
                    distlist=list(up_df['Test'])
                    df_plot=pd.DataFrame(plotdata)
                
                    if distlist[0]=='kde':
                        
                        output=listparamsofdistributions.gencodekde(df_plot['data'],inpvar)
                        #st.code(output)
                        output=output.replace('d=',inpvar+"=")
                        output=output.replace('kernel.pkl',inpvar+"_kernel.pkl")
                        
                        codefilewrite(inpvar,output)
                        
                        code=inpvar+"code"
                        st.session_state[code]=output
                                                
                        
                        kernel = stats.gaussian_kde(df_plot['data'])
                        folder_name = 'gencodeforAMG'
                        file_name = inpvar + "_kernel.pkl"  # Construct file name dynamically based on inpvar
                        folder_path = os.path.join(os.getcwd(), folder_name)  # Get current working directory and append folder name
                        
                        # Check if the folder exists, if not, create it
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        
                        # Construct the full file path
                        pickle_file_path = os.path.join(folder_path, file_name)

                        # Open a file in binary write mode and serialize the kernel object
                        with open(pickle_file_path, 'wb') as file:
                            pickle.dump(kernel, file)

                     
                    else:
                        output=listparamsofdistributions.gencode(distlist[0], datatyp, df_plot['data'])
                        #st.code(output)
                        output=output.replace('data=',inpvar+"=")
                        codefilewrite(inpvar,output)
                        code=inpvar+"code"
                        st.session_state[code]=output
                        picklfilename=inpvar+'pickle'
                        if picklfilename in st.session_state:
                            del st.session_state[picklfilename]
                filename_code=inpvar+"_code.py"
                new_rows = pd.DataFrame([[inpvar, distlist[0],filename_code]], columns=['column', 'dist', 'funcname'])
                table_cols_fit = pd.concat([table_cols_fit, new_rows], ignore_index=True)
   
    #st.write(table_cols_fit)
    return table_cols_fit

    
                                
                
                        
                    
                    
                
                            
                    
                    






def main():
    
    #st.markdown(r"""<style> .stDeployButton {visibility: hidden;}  </style>""", unsafe_allow_html=True)
    st.set_option("client.toolbarMode", "viewer")
    st.markdown(
    """
    <style>
      /* Target the Streamlit text_area widget */
      div.stTextArea > div > textarea {
        font-size: 2px !important;
        line-height: 1.4 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
    #st.set_page_config(page_title="Automatic Model Generator",page_icon="📈",layout="wide")
    st.header("InferaFactorySim")
    st.write('Automatic Model Generator for Manufacturing Systems')
  
    st.write("This is an LLM-based(Gemini-2.5-pro) app to generate a DES model of a manufacturing system from its verbal description")
    #st.markdown("---")
    st.subheader("Datafitting for FactoryFlow")
    st.markdown('''
   User can fit the columns and use that parameter while generating model''', unsafe_allow_html=True)
   


    

    #st.sidebar.image("./MISC/datafitrlogo.PNG", use_column_width=True)
    
    #st.sidebar.subheader("Fitting Time Independent Data")
    
    
    data_col,button_col=st.columns(2)
    with data_col:
        
        datainput_form=st.radio("Select a data source",
                ('Upload a CSV','Use a sample synthetic data','Use an open data set'))
        if datainput_form=='Use a sample synthetic data':
            numdatagen=st.slider("Enter the number of datapoints to generate", 50, 5000,2000)
        elif datainput_form=="Use an open data set":
            st.write("Generating datapoints from open dataset")
        else:
            st.write("The expected format is as shown below. ")
            #st.image("./MISC/sampledata.PNG",width=500)
            st.markdown("""
            The tool expects the data to be in a csv format where the column name is the name of the process variable and the rows are the observations. Categorical data should be converted into numerical values.
            """)
    
        
            
        
    with button_col:
        if datainput_form=='Upload a CSV':
            try:
                st.markdown('''Please upload a CSV file with the variables to fit and proceed.''')
                uploaded_file = st.file_uploader("Choose a file.",type="csv")
                #st.session_state.data_generated=False
                if uploaded_file is None:
                    st.warning("Please upload a csv file to proceed")
                    #return
                    
                        
                else:
                    df1 = pd.read_csv(uploaded_file)
                    st.session_state.data_generated=True
                    st.session_state.data=df1
                    startcheck=df1.describe(include="all")
                    
            except:
                st.warning("Please upload a csv file which adheres to the format mentioned in the documentation.")
                #uploaded_file = st.file_uploader("Choose a file.")
                #IM_uni(df1)    
                
        
            
            #IM_uni(df1)
    
        elif datainput_form=='Use a sample synthetic data': 
            #st.session_state.data_generated=False
            if st.button(("Regenerate a sample synthetic data" if "data_generated" in st.session_state else "Generate a sample synthetic data")):
                
                df1=datagenforDataFITR.univariate_sample(numdatagen)
                st.session_state.data_generated=True
                st.session_state.data=df1
                #st.download_button('Download generated data as a CSV file', to_csv(df1), 'sample_data.csv', 'text/csv')
                with st.expander("View raw data"):
                    st.write(df1)
                st.download_button('Download generated data as a CSV file', to_csv(df1), 'sample_data.csv', 'text/csv')
            
        else:
            st.info("This dataset is an open data from Kaggle. A categorical column in the dataset is converted into numerical values")
            st.markdown("[Click here for details of the dataset](https://www.kaggle.com/datasets/gabrielsantello/parts-manufacturing-industry-dataset)")
            if st.button(("Reload open data" if "data_generated" in st.session_state else "Load open data")):
                
                df1=pd.read_csv("./MISC/opendata.csv")
                st.session_state.data_generated=True
                st.session_state.data=df1
                
                with st.expander("View open data"):
                    st.write(df1)
                st.download_button('Download open data as a CSV file', to_csv(df1), 'open_data.csv', 'text/csv')
            
     
            
    #st.session_state.button_clicked=False        
    #if 'data_generated' in st.session_state:    
        
            
            
       
    #st.write(st.session_state.data_generated)
    if  'data_generated' in st.session_state:
        #st.write(st.session_state.data_generated)
        
        if st.button("Fit data column wise and use parameters for AMG"):
            st.session_state.button_clicked=True
    if 'button_clicked' in st.session_state:
            datatofit=st.session_state['data']

            start_time = time.time()
            #just for scalability study, it will repeat this fitting process otherwise for every other change in the UI
            #if 'fitted_data' not in st.session_state:
            if 'datafitted' not in st.session_state:
                table_cols_fit = IM_uni(datatofit)
                st.session_state['datafitted'] = table_cols_fit
           
            st.subheader("Summary of the fitted columns")                 
            st.write(st.session_state['datafitted'] [['column','dist']])  
            #st.session_state['fitted_data'] = table_cols_fit
            end_time = time.time()
            st.write("Data fitting completed")
            st.write(f"Time taken to fit the data ({len(st.session_state['datafitted'] )} quantities): ", end_time - start_time, " seconds")
            print(f"Time taken: {end_time - start_time:.4f} seconds")
            #st.write(datatofit)
            st.subheader('FactoryFlow')
            #st.write("Enter the verbal description of the system. Use the parameter names from the csv file to describe the components of the system. The tool will generate a DES model of the system.")
            #st.write("The tool will generate a DES model of the system. The model can be simulated using the simulation engine.")
            #input_text=st.text_input("Write an essay on")
            if "descriptionvalidbutton_clicked" not in st.session_state:
                st.session_state.descriptionvalidbutton_clicked=False

            input_text1=st.text_area("Enter system description",height=200)
            
            if st.button("Create model"):
                st.session_state.descriptionvalidbutton_clicked=True
            if st.session_state.descriptionvalidbutton_clicked:
                #if input_text1 and AMG.validatedescriptionwithllm(input_text1):
                if input_text1: 
                #st.write("valid_description",valid_description)
            
                    #st.write(list(datatofit.columns))
                    #complist= [{'id': 'M1', 'type': 'Processor', 'delay': 'M1_delay', 'inp': 'Source', 'out': 'C12', 'power': 'M1_energy'}, {'id': 'C12', 'type': 'ConveyorBelt', 'blocking':'False' ,'delay': 'C12_delay', 'inp': 'M1', 'out': 'M2', 'power': 'C12_energy'},{'id': 'M2', 'type': 'Processor', 'delay': 'M2_delay', 'inp': 'C12', 'out': 'C23', 'power': 'M2_energy'},{'id': 'C23', 'type': 'ConveyorBelt','blocking':'True' ,'delay': 'C23_delay', 'inp': 'M2', 'out': 'M3', 'power': 'C23_energy'},{'id': 'M3', 'type': 'Processor', 'delay': 'M3_delay', 'inp': 'C23', 'out': 'Sink', 'power': 'M3_energy'},{'id': 'Source', 'type': 'Source',   'out': 'M1'}, {'id': 'Sink', 'type': 'Sink',   'in': 'M3'}]
                    #complist={
#         "count": 3,  # Number of node-edge pairs in the chain
#         "node_cls": "Machine",  # Class for nodes (e.g., Machine)
#         "edge_cls": "Buffer",   # Class for edges (e.g., Buffer)
#         "node_kwargs":None,
#         "edge_kwargs": {
    
#             "store_capacity": 4,
#             "delay": 0,
#             "mode": "LIFO"
#         },  # Default edge parameters
#         "node_kwargs_list": [{
#     "id":"M1",
#     "node_setup_time": 0,
#     "work_capacity": 1,
#     "processing_delay": 0.8,
#     "in_edge_selection": "FIRST_AVAILABLE",
#     "out_edge_selection": "FIRST_AVAILABLE"
# },{
#    "id":"M2",
#     "node_setup_time": 0,
#     "work_capacity": 1,
#     "processing_delay": 0.8,
#     "in_edge_selection": "FIRST_AVAILABLE",
#     "out_edge_selection": "FIRST_AVAILABLE"
# },{
#    "id":"M3",
#     "node_setup_time": 0,
#     "work_capacity": 1,
#     "processing_delay": 0.8,
#     "in_edge_selection": "FIRST_AVAILABLE",
#     "out_edge_selection": "FIRST_AVAILABLE"
# }],  # If provided, use as a list of dicts for each node
#         "edge_kwargs_list": None,  # If provided, use as a list of dicts for each edge
#         "prefix": "Node",          # Prefix for node IDs
#         "edge_prefix": "Edge",     # Prefix for edge IDs
#         "connection_pattern": "chain",  # Explicitly state the pattern
#         "column_nodes_names": ["id", "type", "delay", "inp", "out", "power"],  # For LLM reference
#         "parameter_source": "folder_location"  # Where to get parameter values
#         }         
                    #complist= {'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 'node_kwargs_list': [{'id': 'Machine1', 'type': 'Machine', 'processing_delay': '{M1_processing_delay}', 'inp': 'Buffer1', 'out': 'Buffer2'}, {'id': 'Machine2', 'type': 'Machine', 'processing_delay': '{M2_processing_delay}', 'inp': 'Bu ', 'inp': 'Buffer10', 'out': 'Buffer11'}], 'edge_kwargs_list': [{'id': 'Buffer1', 'type': 'Buffer', 'inp': 'Source', 'out': 'Machine1'}, {'id': 'Buffer2', 'type': 'Buffer', 'inp': 'Machine1', 'out': 'Machine2'}, {'id': 'Buffer3', 'type': 'Buffer', 'inp': 'Machine2', 'out': 'Machine3'}, {'id': 'Buffer4','processing_delay': '{M10_processing_delay}', 'inp': 'Buffer10', 'out': 'Buffer11'}],  'edge_kwargs_list': [{'id': 'Buffer1', 'type': 'Buffer', 'inp': 'Source', 'out': 'Machine1'}, {'id': 'Buffer2', 'type': 'Buffer', 'inp': 'Machine1', 'out': 'Machine2'}, {'id': 'Buffer3', 'type': 'Buffer', 'inp': 'Machine2', 'out': 'Machine3'}, {'id': 'Buffer4', 'type': 'Buffer', 'inp': 'Machine3', 'out': 'Machine4'}, {'id': 'Buffer5', 'type': 'Buffer', 'inp': 'Machine4', 'out': 'Machine5'}, {'id': 'Buffer6', 'type': 'Buffer', 'inp': 'Machine5', 'out': 'Machine6'}, {'id': 'Buffer7', 'type': 'Buffer', 'inp': 'Machine6', 'out': 'Machine7'}, {'id': 'Buffer8', 'type': 'Buffer', 'inp': 'Machine7', 'out': 'Machine8'}, {'id': 'Buffer9', 'type': 'Buffer', 'inp': 'Machine8', 'out': 'Machine9'}, {'id': 'Buffer10', 'type': 'Buffer', 'inp': 'Machine9', 'out': 'Machine10'}, {'id': 'Buffer11', 'type': 'Buffer', 'inp': 'Machine10', 'out': 'Sink'}], 'prefix': 'Machine', 'edge_prefix': 'Buffer', 'connection_pattern': 'chain', 'column_nodes_names': ['id', 'type', 'processing_delay', 'inp', 'out'], 'parameter_source': 'folder_location'}
                    
#                     #complist={'count': 10, 'node_cls': 'Machine', 'edge_cls': 'Buffer', 'node_kwargs_list': [
# {'id': 'M1', 'type': 'Machine', 'processing_delay': '{M1_processing_delay}', 'in_edges': ['B_src_1'], 'out_edges': ['B_1_2'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 
# {'id': 'M2', 'type': 'Machine', 'processing_delay': '{M2_processing_delay}', 'in_edges': ['B_1_2'], 'out_edges': ['B_2_3'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M3', 'type': 'Machine', 'processing_delay': '{M3_processing_delay}', 'in_edges': ['B_2_3'], 'out_edges': ['B_3_4'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 
# {'id': 'M4', 'type': 'Machine', 'processing_delay': '{M4_processing_delay}', 'in_edges': ['B_3_4'], 'out_edges': ['B_4_5'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'},

#  {'id': 'M5', 'type': 'Machine', 'processing_delay': '{M5_processing_delay}', 'in_edges': ['B_4_5'], 'out_edges': ['B_5_6_1'], 'work_capacity': 3, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 

# {'id': 'M6', 'type': 'Machine', 'processing_delay': '{M6_processing_delay}', 'in_edges': ['B_5_6_1'], 'out_edges': ['B_6_7'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M7', 'type': 'Machine', 'processing_delay': '{M7_processing_delay}', 'in_edges': ['B_6_7'], 'out_edges': ['B_7_8'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M8', 'type': 'Machine', 'processing_delay': '{M8_processing_delay}', 'in_edges': ['B_7_8'], 'out_edges': ['B_8_9'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M9', 'type': 'Machine', 'processing_delay': '{M9_processing_delay}', 'in_edges': ['B_8_9'], 'out_edges': ['B_9_10'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, {'id': 'M10', 'type': 'Machine', 'processing_delay': '{M10_processing_delay}', 'in_edges': ['B_9_10'], 'out_edges': ['B_10_sink'], 'work_capacity': 1, 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}], 'edge_kwargs_list': [{'id': 'B_src_1', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'src', 'dest_node': 'M1'}, {'id': 'B_1_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M1', 'dest_node': 'M2'}, {'id': 'B_2_3', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M2', 'dest_node': 'M3'}, {'id': 'B_3_4', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M3', 'dest_node': 'M4'}, {'id': 'B_4_5', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M4', 'dest_node': 'M5'}, {'id': 'B_5_6_1', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_2', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M5', 'dest_node': 'M6'}, {'id': 'B_5_6_3', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'},

#  {'id': 'B_5_6_4', 'type': 'Buffer', 'store_capacity': 4, 'src_node': 'M5', 'dest_node': 'M6'}, 
# {'id': 'B_6_7', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M6', 'dest_node': 'M7'},
#  {'id': 'B_7_8', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M7', 'dest_node': 'M8'}, {'id': 'B_8_9', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M8', 'dest_node': 'M9'}, {'id': 'B_9_10', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M9', 'dest_node': 'M10'}, {'id': 'B_10_sink', 'type': 'Buffer', 'store_capacity': 2, 'src_node': 'M10', 'dest_node': 'sink'}], 'prefix': 'Machine', 'edge_prefix': 'Buffer', 'connection_pattern': 'chain', 'column_nodes_names': ['id', 'type', 'processing_delay', 'in_edges', 'out_edges', 'work_capacity', 'in_edge_selection', 'out_edge_selection'], 'column_edges_names': ['id', 'type', 'store_capacity', 'src_node', 'dest_node'], 'parameter_source': 'folder_location'}

                    #complist= [{'id':'Source','type': 'Source', 'out_edges': ['RawMaterial_buffer']}, 
#  {'id':'RawMaterial_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Source', 'dest_node': 'Primaryprocessor', 'mode': 'FIFO', 'store_capacity': 10}, 
 
# {'id':'Primaryprocessor','type': 'Machine', 'processing_delay': '{PrimaryProcessor_delay}', 'in_edges': ['RawMaterial_buffer','Reworked_material_buffer'], 'out_edges': ['Intermediate_buffer'], 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'},

#  {'id':'Intermediate_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Primaryprocessor', 'dest_node': 'Splitter', 'mode': 'FIFO', 'store_capacity': 10}, 
#  {'id':'Splitter','type': 'Splitter', 'delay': '{Splitter_delay}', 'in_edges': ['Intermediate_buffer'], 'out_edges': ['Qualitychecker_buffer', 'Rework_buffer'], 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'},
#    {"id":'Qualitychecker_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Splitter', 'dest_node': 'Inspection', 'mode': 'FIFO', 'store_capacity': 10}, 
#    {'id':'Inspection','type': 'Machine', 'processing_delay': '{Inspection_delay}', 'in_edges': ['Qualitychecker_buffer'], 'out_edges': ['Final_buffer'], 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 
   
#    {'id':'Final_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Inspection', 'dest_node': 'Sink1', 'mode': 'FIFO', 'store_capacity': 10}, 
#    {'id':'Rework_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Splitter', 'dest_node': 'Rework', 'mode': 'FIFO', 'store_capacity': 10},
#      {'id':'Rework','type': 'Machine', 'processing_delay': '{Rework_delay}', 'in_edges': ['Rework_buffer'], 'out_edges': ['Faulty_buffer','Reworked_material_buffer'], 'in_edge_selection': 'FIRST_AVAILABLE', 'out_edge_selection': 'FIRST_AVAILABLE'}, 

#      {'id':'Reworked_material_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Rework', 'dest_node': 'Primaryprocessor', 'mode': 'FIFO', 'store_capacity': 10},
#      {'id':'Faulty_buffer','type': 'Buffer', 'delay': 0, 'src_node': 'Rework', 'dest_node': 'Sink2', 'mode': 'FIFO', 'store_capacity': 10}, {'id':'Sink2','type': 'Sink', 'in_edges': ['Faulty_buffer']}, {'id':'Sink1','type': 'Sink', 'in_edges': ['Final_buffer']}]

                    #struct_text=complist

                    llm_start= time.time()
                    struct_text=AMG.askllm(input_text1,list(datatofit.columns),st.session_state['datafitted'])
                    llm_end= time.time()
                    st.write("Time taken by LLM to generate the model description: ", llm_end - llm_start, " seconds")
                    st.session_state.asked_llm=True
                    if struct_text:
                                    #st.write(struct_text)
                        if 'struct_data' not in st.session_state:
                            st.session_state.struct_data = struct_text
                            #st.write("st.session_state.struct_data",st.session_state.struct_data)
                        #st.write("st.session_state.struct_data",st.session_state.struct_data)
                        if 'struct_data' in st.session_state:
                            # Call the structanddraw function with the existing data
                            #structanddraw(st.session_state.struct_data)----------14june
                            #before_any=st.session_state.struct_data
                            #st.write(before_any)
                            # Display a text area with the current data
                            
                            #st.write(st.session_state.struct_data)
                            
                            IM.model_visualiser.visualize_graph(st.session_state.struct_data)
                            #   data=st.session_state.struct_data)
                            #st.write("The model is visualized below. You can edit the model description and regenerate the model.")
                            #st.subheader("Model description editor")
                            #st.caption("Intermediate model description (component list)")
                            #st.badge("Model description editor")
                            with st.expander("Click to expand", expanded=False):
                                        #user_input = st.text_area("Your text here", height=200)
                                        st.write(llm_start, llm_end)
                                        user_input = st.text_area("Intermediate model description (component list)", st.session_state.struct_data,height=350)
                            
                            
                            
                            if user_input != st.session_state.struct_data:
                                # Update the session state with the new data
                                #st.session_state.struct_data = user_input # Change is later for user changes to take effect
                                # Call the function again with the new data
                                
                                #mermaid_data_to_visualise=IM.model_visualiser.generate_chain_diagram(st.session_state.struct_data)
                                IM.model_visualiser.visualize_graph(st.session_state.struct_data)
                                
                                #structanddraw(st.session_state.struct_data)
                        else:
                            st.write("No data available.")


                        
                       

                                    
                            
                        if os.path.exists("diagram_for_factoryflow.png"):
                             st.caption("System block diagram")
                             AMG.render_image("diagram_for_factoryflow.png")

                        # if st.button("Generate simulation model"):
                        #     st.session_state.descriptionvalidbutton_clicked=False

                        #print(type(st.session_state.struct_data), type(ast.literal_eval(st.session_state.struct_data)))
                        
                        if type(st.session_state.struct_data)== str and isinstance(ast.literal_eval(st.session_state.struct_data) , list) or isinstance(st.session_state.struct_data , list):
                            

                            if "synthesize_clicked" not in st.session_state:
                                    st.session_state.synthesize_clicked=False

                            if st.button("Generate simulation model"):
                                st.session_state.synthesize_clicked=True

                            if st.session_state.synthesize_clicked and st.session_state.descriptionvalidbutton_clicked:
                                st.write("Generating code for the model")
                                Simulation = IM.SimulationEngine.simulation_engine_m1(st.session_state.struct_data)
                                st.write(Simulation)

                        elif type(st.session_state.struct_data)== str and isinstance(ast.literal_eval(st.session_state.struct_data) , dict):
                
                            data= ast.literal_eval(st.session_state.struct_data)
                            print("here")
                            if "synthesize_clicked" not in st.session_state:
                                    st.session_state.synthesize_clicked=False

                            if st.button("Synthesize model"):
                                st.session_state.synthesize_clicked=True

                            if st.session_state.synthesize_clicked and st.session_state.descriptionvalidbutton_clicked:
                                st.write("Generating code for the model")
                                #Simulation = IM.SimulationEngine.simulation_engine_m2(data)

                                if "parallel_chains" in data and "count" in data:
                                    Simulation = IM.simulationengine_m3.simulation_engine_m3(data)
                                elif "count" in data:
                                    Simulation = IM.simultest.simulation_engine_m2(data)
                                else:
                                    st.write("The data format is not supported for simulation engine")
                                st.write(Simulation)
                        else:
                            st.error("Please enter a valid data format")
                            #st.write("st.session_state.struct_data",st.session_state.struct_data)


                            
                            
                            
                            
                            
                           
                
        
                else:
                    st.error("Please enter a valid description")
            
        
    
            
            
            
            
                 
if __name__=='__main__':
    main()




    
    

        

        



 
    

    

            



    


