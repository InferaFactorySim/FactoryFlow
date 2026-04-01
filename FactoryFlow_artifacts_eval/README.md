- List of authors 
Lekshmi P and Neha Karanjkar

- Corresponding author for artifact evaluation
Lekshmi P (lekshmi20231101@iitgoa.ac.in)

- Title of the paper
On Integrating Resilience and Human Oversight into LLM-Assisted Modeling Workflows for Digital Twins

- Instructions to install and run the artifact



# 1. Copy the repository folder
# 2. Install dependencies
```bash
pip install -r requirements.txt
```
# 3. Create a file named `.env` inside `app/IM` folder with the following content:
```bash
GEMINI_API_KEY=your_api_key_here
```

# 4. Run the application
```bash
cd app
streamlit run Description_to_model_generator.py
```


- Dependencies and how to resolve/install them
FactorySimPy is included in the `src/` folder — no separate install needed.
All other dependencies are listed in `requirements.txt`.



- How to verify correct installation (if needed)
After running the Streamlit command above, the app should open in your browser at `http://localhost:8501`. If it loads without errors, installation is correct.

- Expected duration of the experiments (ideally, both for individual runs and for all the experimental phase)

| Phase | Duration |
|-------|----------|
| Per experiment (model comparison + error counting) | 8–10 minutes |
| Full experimental phase | ~35–40 hours |

- Hardware requirements (RAM, cores, GPU if needed...)
Basic configuration will be enough.
Preferably
RAM     : 8–16 GB
CPU     : Intel i5/i7 or AMD Ryzen 5/7 (4–8 cores)
Storage : 256–512 GB SSD
OS      : Windows 11 or Ubuntu 22.04
GPU     : Integrated only

- Software/hardware environment used in your experiments

Software used
operating system- 	Windows 11 Home Single Language 64 bit 
Python version 3.12


Hardware used
| Component | Details |
|-----------|---------|
| OS | Windows 11 Home Single Language 64-bit |
| CPU | AMD Ryzen 5 5500U with Radeon Graphics |
| Cores | 6 cores / 12 logical processors |
| RAM | 8 GB |
| Storage | Kingston 512 GB NVMe SSD |

No GPU required.




- License file
License file is included in the GitHub repository.

- DOI or stable repository link (e.g., Zenodo recommended)

