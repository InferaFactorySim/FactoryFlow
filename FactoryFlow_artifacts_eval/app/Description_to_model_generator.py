import streamlit as st
import time
from IM.AMG_with_langgraph import (
    run_amg_wrapper,
    run_manual_overrides,
)

from IM.timing_logger import log_time
import sys, os

# Make the local factorysimpy package importable
_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "src"))
if _src_path not in sys.path:
    sys.path.insert(0, _src_path)


# ============================================================
# STREAMLIT CONFIG
# ============================================================
st.set_page_config(page_title="FactorySimPy AMG", layout="wide")
st.set_option("client.toolbarMode", "viewer")



st.title("FactoryFlow")
st.write("Automated Discrete-event Simulation Model Generator for Manufacturing Systems")

# ============================================================
# BLOCK DIAGRAM
# ============================================================

def get_blockdiagram():
    """Helper to generate the figure from generated code."""
    
    unique_id = time.time_ns()
    temp_filename = f"temp_gen_model_{unique_id}.py"
    module_name = f"dynamic_mod_{unique_id}"

    if not st.session_state.amg_state or "code_from_amg" not in st.session_state:
        return None
    
    code = st.session_state["code_from_amg"]

    # Cleaning code blocks
    if code.startswith("```python"):
        code = code.replace("```python", "", 1)
    if code.endswith("```"):
        code = code.rsplit("```", 1)[0]
    clean_code = code.strip()

    # Adjust imports
    modified_code = clean_code.replace(
        "import factorysimpy",
        "import sys, os\n"
        "sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './src')))\n"
        "from factorysimpy.utils.utils import draw_blockdiagram\n"
    )
    
    # Write to the unique filename
    with open(temp_filename, "w", encoding="utf-8") as f:
        f.write(modified_code)

    try:
        # Import using the unique module name
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, temp_filename)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        draw_fn = getattr(mod, "draw_blockdiagram", None)
        if draw_fn is None:
            from factorysimpy.utils.utils import draw_blockdiagram as draw_fn
            
        fig = draw_fn(mod.TOP)
        return fig
    except Exception as e:
        st.error(f"Diagram Error: {e}")
        return None
    finally:
        # Remove the temporary file after importing
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        # Remove from sys.modules to save memory
        if module_name in sys.modules:
            del sys.modules[module_name]


# ============================================================
# SESSION STATE
# ============================================================


st.session_state.setdefault("edit_mode", False)

if "amg_state" not in st.session_state:
    st.session_state.amg_state = None
if "current_description" not in st.session_state:
    st.session_state.current_description = ""
if "code_from_amg" not in st.session_state:
    st.session_state.code_from_amg = ""


# ============================================================
# INITIAL STATE — ONLY DESCRIPTION
# ============================================================
if st.session_state.amg_state is None:
    st.subheader("📝 Description")

    description = st.text_area(
        "Describe the manufacturing system",
        value=st.session_state.current_description,
        height=260,
    )

    if st.button("Generate Model"):
        if description.strip():

            with st.spinner("Generating model..."):
                generate_start_time = time.perf_counter()
                new_state = run_amg_wrapper(DESCRIPTION=description)
                generate_end_time = time.perf_counter()

                log_time("LLM call- run_amg_wrapper", generate_end_time - generate_start_time, "app")
                st.session_state.code_from_amg = new_state.pop("code", "")
                
            # 🔑 COMMIT description into model state
                new_state["description"] = description
                st.session_state.amg_state = new_state
                st.session_state.current_description = description

                st.rerun()
        else:
            st.warning("Please enter a description.")

# ============================================================
# AFTER GENERATION — DESCRIPTION + ASSUMPTIONS + CODE
# ============================================================
else:
    # --------------------------------------------------------
    # DESCRIPTION + ASSUMPTIONS
    # --------------------------------------------------------
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📝 Description")

        st.session_state.current_description = st.text_area(
            "Editable description",
            value=st.session_state.current_description,
            height=450,
        )

    with col_right:
        st.subheader("📄 Assumptions")
        #1. Get the content
        content = st.session_state.amg_state.get("assumptions", "")

        # 2. Calculate lines (count newlines + 1)
        lines = content.count('\n') + 1

        # 3. Calculate height (e.g., 25px per line, with a minimum of 100 and max of 600)
        calculated_height = max(200, min(600, lines * 30))

        edited_assumptions = st.text_area(
            "Editable assumptions",
            value=content,
            height= 220 if calculated_height <= 220 else 2*calculated_height,
        )
    
    if st.button("Regenerate model with changes", use_container_width=True):
        st.info(
            "Regenerating with edits.\n\n"
        )
        st.write("Description changed:" , st.session_state.current_description != st.session_state.amg_state.get("description",""))
        st.write("Assumptions changed:" , edited_assumptions != st.session_state.amg_state.get("assumptions",""))
        
        with st.spinner("Applying overrides..."):
            regenerate_start_time = time.perf_counter()
            updated_state = run_manual_overrides(
                st.session_state.amg_state,
                old_description=st.session_state.amg_state.get("description", ""),
                new_description=st.session_state.current_description,
                user_assumptions=edited_assumptions,
            
            )
            regenerate_end_time = time.perf_counter()
            log_time("LLM call- run_manual_overrides", regenerate_end_time - regenerate_start_time, "app")
            
            st.session_state.code_from_amg = updated_state.pop("code", "")
            st.session_state.amg_state = updated_state

            # 🔑 COMMIT NEW description
            st.session_state.amg_state["description"] = (
                st.session_state.current_description
            )

            

            st.rerun()
    # --------------------------------------------------------
    # VISUALIZATION
    # --------------------------------------------------------
    st.markdown("---")
    diag_header_col, diag_download_col = st.columns([4, 1])
    with diag_header_col:
        st.subheader("📊 Model Diagram")
        code_content = st.session_state.get("code_from_amg","")
        if code_content.strip():
            with st.spinner("Generating model diagram..."):
                fig = get_blockdiagram()
                if fig:
                    st.graphviz_chart(fig.source)
                else:
                    st.info("No diagram available.")
    with diag_download_col:
        if fig:
            st.download_button(
                label="Download diagram",
                data=fig.pipe(format="png"),
                file_name=f"factory_model_diagram_{int(time.time())}.png",
                mime="image/png",
                help="Download the generated model diagram",
            )

    # --------------------------------------------------------
    # CODE
    # --------------------------------------------------------


    


    st.markdown("---")

    # Header row: title + download button
    header_col, edit_col , download_col = st.columns([4, 1, 1])

    with header_col:
        st.subheader("💻 Python Code")

    with edit_col:
        if st.session_state.edit_mode:
            # Update the state variable BEFORE rerunning/toggling edit_mode
            if st.button("Save Code", use_container_width=True):
                # 'code_editor' is the key we assigned to the text_area below
                if "code_editor" in st.session_state:
                    st.session_state.code_from_amg = st.session_state.code_editor
                
                st.session_state.edit_mode = False
                st.rerun()
        else:
            if st.button("Edit Code", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
    # to get assumptions + code in file
    description_text = st.session_state.amg_state.get("description")
    assumptions_text = st.session_state.amg_state.get("assumptions", "No assumptions generated.")
    code_text = st.session_state.get("code_from_amg","")

    # This combines them: Assumptions at the top, then two new lines, then the code
    file_content = f'"""\nModelDescription:\n{description_text}\n\n MODEL ASSUMPTIONS:\n{assumptions_text}\n"""\n\n{code_text}'
    
    
    with download_col:
        st.download_button(
            label="Download code",
            data=file_content,
            file_name=f"factory_model_{int(time.time())}.py",
            mime="text/x-python",
            help="Download the generated Python model",
        )
    if st.session_state.edit_mode:
        # Editable code area
        edited_code = st.text_area(
            "",
            value=st.session_state.get("code_from_amg",""),
            height=420,
            key="code_editor",
        )
        st.session_state.code_from_amg = edited_code

    else:
        st.code(st.session_state.get("code_from_amg",""))
    





