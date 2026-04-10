#!/bin/bash

# Navigate to the project directory
cd /home/polycube/

# Activate the virtual environment
source Server/.venv/bin/activate

# Run the Python script
# Use 'python' instead of 'python3' as the venv maps it automatically
python Server/main.py

# Optional: Keep the terminal open if it crashes (good for debugging)
read