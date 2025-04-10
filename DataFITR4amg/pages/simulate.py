import streamlit as st
import tempfile
import subprocess
def main():
    st.set_page_config(page_title="AMG",page_icon="📈",layout="wide")
    
    #st.sidebar.subheader("Simulation environment")
    
    #st.sidebar.image("/home/lekshmi/Downloads/DataFitter/MISC/datafitrlogo.PNG", use_column_width=True)
    #st.sidebar.image("./MISC/datafitrlogo.PNG", use_column_width=True)
    st.subheader("Simulation environment")
    st.markdown("---")
    
    
    
    data_col,button_col=st.columns(2)
    
    
    
    
    data_col,button_col=st.columns(2)
    with data_col:
        
        datainput_formMVG=st.radio("Select a code source",
                ('Upload a code file','Use generated code',))
        if datainput_formMVG=='Use generated code':
            #numdatagen=st.slider("Enter the number of datapoints to generate", 50, 5000,2000)
            #st.write(st.session_state)
            try:
                code= st.session_state['simpycode']
                code=code.replace('```python','')
                code=code.replace('```','')
                st.session_state['simpycode']=code
            except:
                st.warning("Please upload a python file to proceed")
                return
       
        else:
            st.write("The expected format is a python file is as shown below. ")
            #st.image("./MISC/sampledata.PNG",width=500)
            #st.markdown("""
            #The tool expects the data to be in a csv format where the column name is the name of the process variable and the rows are the observations.
            #""")
    with button_col:
        if datainput_formMVG=='Upload a Code':
            try:
                
                st.markdown('''Please upload a python file with the variables to proceed.''')
                uploaded_file = st.file_uploader("Choose a file.",type="python")
                
                if uploaded_file is None:
                    st.warning("Please upload a csv file to proceed")
                    return
                    
                        
                else:
                    
                    st.session_state.data_generatedMVG=True
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w') as temp_file:
                        temp_file.write(st.session_state.simpycode)
                        temp_file_name = temp_file.name
                    

                    result = subprocess.run(['python', temp_file_name], capture_output=True, text=True)
                    st.write(result.stdout)
                    
            except:
                st.warning("Please upload a csv file which adheres to the format mentioned in the documentation.")
                #uploaded_file = st.file_uploader("Choose a file.")
                #IM_uni(dfMVG)    
                
        
            
            #IM_uni(dfMVG)
    
        else:
            
            #st.session_state.data_generatedMVG=False
            if st.button(("Reload generated code" if "data_generatedMVG" in st.session_state else "Use generated code")):
                
                #dfMVG=datagenforDataFITR.multivariate_Gaussian_sample(numdatagen) 
                st.session_state.data_generatedMVG=True
                #st.session_state.dataMVG=dfMVG
                st.code(st.session_state.simpycode,language='python')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w') as temp_file:
                        temp_file.write(st.session_state.simpycode)
                        temp_file_name = temp_file.name
                    

                result = subprocess.run(['python', temp_file_name], capture_output=True, text=True)
                #st.write(result.stdout)
        
                with st.expander("View logging information for the simulation run"):
                    st.write(result.stdout)
                    st.write(result.stderr)
                #st.download_button('Download generated data as a CSV file', to_csv(dfMVG), 'sample_multivariate_gaussian_data.csv', 'text/csv')
                
  
      
    
if __name__=='__main__':
    main()
    
    