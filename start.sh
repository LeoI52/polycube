#!/bin/bash
# Give the desktop a moment to breathe
sleep 5

echo "--- Starting Script ---"
# Use absolute paths for EVERYTHING
cd /home/polycube/polycube/Server || echo "Could not find Server directory"

# Activate venv
if [ -f "/home/polycube/polycube/Server/.venv/bin/activate" ]; then
    source /home/polycube/polycube/Server/.venv/bin/activate
    echo "Virtual Environment Activated"
else
    echo "ERROR: Virtual environment not found!"
fi

# Run python
python3 /home/polycube/polycube/Server/main.py

echo "--- Script Stopped ---"
# This keeps the window open so you can read the error!
read -p "Press Enter to close..."