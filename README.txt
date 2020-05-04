Please see below for required Python modules as well as instructions on how to install.
While you do not need to use a virtual environment for this, I would suggest
doing so as it can help with compatability of packages. 


Required modules:
pythonping 
ipaddress 
pprint 
scapy

COMMANDS TO PREPEARE YOUR ENVIRONMENT (Run from PowerShell)
############################################################################
Set-ExecutionPolicy Remote-Signed -Force 
python -m venv .
.\Scripts\Activate.ps1 
pip install --upgrade pip wheel setuptools 
pip install pythonping
pip install ipaddress 
pip install scapy
pip install pprint 
############################################################################



HOW TO RUN PINGSWEEP TOOL (Run from PowerShell):
############################################################################
.\Scripts\Activate.ps1 
python .\pingsweep.py 
