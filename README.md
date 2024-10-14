# Start the panel
1. Create venv and install requirements  
python3 -m venv .venv  
source .venv/bin/activate  
python3 -m pip install -r requirements.txt

2. Change BIND_ADDRESS to current machine ip: async_server.py, line 23

3. Start  
python3 main.py [--ip]  


<p>Once the corresponding script is started on robot, it connects to the server and is shown in the default coordinates: (300, 300), (500, 300), (100, 300).
<p>The disconnect button disconnects the robot, which number is specified in "Robot N." field in "Start move" area.
<p>The "Build path" requires the robot №0 to exist and be connected, as it builds the path from its position to a random point.  