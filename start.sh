#!/bin/bash
# Increase sleep slightly just in case the Desktop is slow to load
sleep 15

# Use the full path to the project folder
cd /home/polycube/Server

# Activate using the absolute path to the activate script
source /home/polycube/Server/.venv/bin/activate

# Run the script. 
# Adding 'python3' with the full path to the script is safer.
python3 /home/polycube/Server/main.py

# Keep the window open so you can read the error if it crashes
echo "Process finished. Press enter to close."
read