# Run SwitchMatter Locally

## Windows PowerShell

```powershell
cd .\MVP0
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. Create a SKU, complete or import the Functional Envelope, add supplier PDF or `.xlsx` BOM evidence, confirm component fields, run Legal Gates, and inspect the Step 3 verdict.

Run tests with:

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

## macOS or Linux

```bash
cd MVP0
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m streamlit run app.py
PYTHONPATH=src python -m unittest discover -s tests -v
```
