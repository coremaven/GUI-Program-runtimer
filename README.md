# Script Timer Application

A tool to control script/program execution with timer functionality.

<img width="500" height="572" alt="Screenshot" src="https://github.com/user-attachments/assets/4d3b3b50-e651-47d6-947c-0018d8b9693a" />

## Features

This application provides three timer functions for controlling script execution:

1. **Close after time**: Runs a script/program for a specified number of minutes, then automatically closes it
2. **Run every x time**: Repeats execution of a script/program at specified intervals (minutes)
3. **Start at specific time**: Executes a script/program at a specific time of day (optionally repeating daily)

## Requirements

- Python 3.6+
- PyQt5 (for GUI version)

## Installation

### For the GUI version:
```bash
# Install PyQt5
pip install PyQt5

# Or in a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install PyQt5
```

## Usage

### Running the GUI version:
```bash
python script_timer.py
```

### Running the simple version (no GUI):
```bash
python simple_script_timer.py
```

## How to Use

1. Run the script
2. Click "Select Script" to choose a program/script to control
3. Configure one of the three functions:
   - **Close after time**: Set duration in minutes and click Start
   - **Run every x time**: Set interval in minutes and click Start 
   - **Start at specific time**: Set time and optionally check "Repeat daily", then click Start

## Files

1. `script_timer.py` - The full PyQt5 GUI version
2. `simple_script_timer.py` - A console-based version without GUI dependencies
3. `README.md` - This file

## Notes

- All time values are specified in minutes (not seconds)
- The application works with any executable file or script
- Processes are automatically terminated when stopped
