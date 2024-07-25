# Start the panel
1. Create venv and install requirements
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt

2. Change BIND_ADDRESS to current machine ip: async_server.py, line 23

3. Start
python3 main.py
