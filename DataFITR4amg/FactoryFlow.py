#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 23 11:14:15 2023

@author: lekshmi
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import DataFITR.DataFITR4amg.IM.AMG as AMG
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
#sys.path.append('/home/lekshmi/Downloads/my_app/IM') 
sys.path.append('./IM') 
sys.path.append(os.path.abspath(os.path.dirname('AMGUI.py')))
#import modular_IM
from IM import modular_IM
from IM import kde_silverman_both
from IM import datagenforDataFITR
from IM import SimulationEngine

#from IM.SimulationEngine import simulation_engine

from IM import makenetlist
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
def my_function(data,distlist,distributions,typ='continuous',dist='my1 distribution',bins=100,gof="ks",kde_bin=50):
    #st.write("Please wait while I fit your data")
    #modelGUI=modular_IM.modelmatch()
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
    discrete=['binom','poisson','geom']
    return discrete

def codefilewrite(inpvar,output):
    folder_name = 'gencodeforAMG'
    file_name = inpvar + "_code.py"  # Construct file name dynamically based on inpvar
    folder_path = os.path.join(os.getcwd(), folder_name)  # Get current working directory and append folder name
    
    # Check if the folder exists, if not, create it
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Construct the full file path
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'w') as file:
        file.write(output)






def is_CSV(filename):
   #st.write(filename.split("."))
   return filename.split(".")[1]

def to_csv(df):
    data_csv = df.to_csv(path_or_buf=None, sep=',', index=False) 
    return data_csv

        
def checkdatatype(df):
    for i in df.columns:
        if (df[i]).dtype  not in[ 'float','int']:
            return 0
    return 1







def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def finddatatype_autofill(data):
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

def structanddraw(netlist):
    #st.write("NN",netlist)
    struct_diag=AMG.generate_blockdiag_code(netlist)
    #st.write(struct_diag)
    AMG.blockdiagdraw(struct_diag)   
     
    
    
    
    
def IM_uni(df):
   
    table_cols_fit=pd.DataFrame(columns=['column','dist','funcname'])  
    #st.header("Data Fitting")
    cols=list(['KStest','Chi squared Test','SSE'])
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
                Discrete_Popular=['binom','poisson','geom']
            

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
              
                restyp,finresult,plotdata,pval=my_function(df[inpvar],distlist,distributions,datatyp,inpvar,bins,'ks')
                if restyp=='constant':
                    
                    constdict={"column":inpvar,"value":[pval],'type':['constant']}
                    constdf=pd.DataFrame(constdict)
                    constantname=inpvar+'constant'
                    table_cols_fit
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
    st.subheader("Summary of the fitted columns")                 
    st.write(table_cols_fit[['column','dist']])  
    #st.write(table_cols_fit)
    return table_cols_fit

    
                                
                
                        
                    
                    
                
                            
                    
                    






def main():
    
    st.set_page_config(page_title="Automatic Model Generator",page_icon="📈",layout="wide")
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
            table_cols_fit = IM_uni(datatofit)
            #st.write(datatofit)
            st.subheader('FactoryFlow: LLM-based tool for converting descriptions to DES models')
            #st.write("Enter the verbal description of the system. Use the parameter names from the csv file to describe the components of the system. The tool will generate a DES model of the system.")
            #st.write("The tool will generate a DES model of the system. The model can be simulated using the simulation engine.")
            #input_text=st.text_input("Write an essay on")
            if "descriptionvalidbutton_clicked" not in st.session_state:
                st.session_state.descriptionvalidbutton_clicked=False

            input_text1=st.text_area("Enter system description",height=200)
            
            if st.button("Generate NetList"):
                st.session_state.descriptionvalidbutton_clicked=True
            if st.session_state.descriptionvalidbutton_clicked:
                if input_text1 and AMG.validatedescriptionwithllm(input_text1): 
                #st.write("valid_description",valid_description)
            
                    #st.write(list(datatofit.columns))
                    
                    struct_text=AMG.askllm(input_text1,list(datatofit.columns),table_cols_fit)
                    #struct_text=complist
                    if struct_text:
                                    #st.write(struct_text)
                        if 'struct_data' not in st.session_state:
                            st.session_state.struct_data = struct_text
                            #st.write("st.session_state.struct_data",st.session_state.struct_data)
                        #st.write("st.session_state.struct_data",st.session_state.struct_data)
                        if 'struct_data' in st.session_state:
                            # Call the structanddraw function with the existing data
                            structanddraw(st.session_state.struct_data)
                            
                            # Display a text area with the current data
                            user_input = st.text_area("Model description as a structured text:", st.session_state.struct_data,height=200)
                            
                            if user_input != st.session_state.struct_data:
                                # Update the session state with the new data
                                st.session_state.struct_data = user_input
                                # Call the function again with the new data
                                structanddraw(st.session_state.struct_data)
                        else:
                            st.write("No data available.")

                                    
                            
                        if os.path.exists("diagram1.png"):
                            AMG.render_image("diagram1.png")
                        
                        if st.session_state.struct_data:
                            makenetlist_obj=IM.makenetlist.Netlist()
                            comp=st.session_state.struct_data
                            comp = comp.replace("'", '"')
                            comp = json.loads(comp)
                            comp_dict = makenetlist_obj.initialize_components(comp)
                            comp_graph = makenetlist_obj.graph
                            #st.write(makenetlist_obj)

                            if "generatemodel_clicked" not in st.session_state:
                                    st.session_state.generatemodel_clicked=False

                            if st.button("Build model"):
                                st.session_state.generatemodel_clicked=True

                            if st.session_state.generatemodel_clicked and st.session_state.descriptionvalidbutton_clicked:
                                st.write("Generating code for the model")
                                Simulation = IM.SimulationEngine.simulation_engine(comp_dict,comp_graph)
                                st.write(Simulation)

                           
                            
                            
                            
                            
                            
                           
                
        
                else:
                    st.error("Please enter a valid description")
            
        
    
            
            
            
            
                 
if __name__=='__main__':
    main()




    
    

        

        



 
    

    

            



    


