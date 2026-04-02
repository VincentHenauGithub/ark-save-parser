"""
Script to add a LostColony_WP.ark file to history with timestamp.
Copies the file and appends it to ark_files.json.
"""
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

history_dir = Path(__file__).parent

# Source ark file - can be passed as argument or use default
if len(sys.argv) > 1:
    source_path = Path(sys.argv[1])
else:
    # Default: look for LostColony_WP.ark in parent directory
    source_path = history_dir.parent / "LostColony_WP.ark"

if not source_path.exists():
    print(f"ERROR: Source file not found: {source_path}")
    print("Usage: python append_ark_to_history.py [path_to_ark_file]")
    sys.exit(1)

# Create timestamped filename: LostColony_WP_DD.MM.YYYY_HH.MM.SS.ark
timestamp = datetime.now().strftime("%d.%m.%Y_%H.%M.%S")
dest_name = f"LostColony_WP_{timestamp}.ark"
dest_path = history_dir / dest_name

# Copy file
print(f"Copying {source_path.name} -> {dest_name}")
shutil.copy2(source_path, dest_path)

# Update ark_files.json
json_path = history_dir / "ark_files.json"
if json_path.exists():
    with open(json_path, 'r') as f:
        ark_files = json.load(f)
else:
    ark_files = []

# Add new file and sort
ark_files.append(str(dest_path.resolve()))
ark_files = sorted(ark_files)

with open(json_path, 'w') as f:
    json.dump(ark_files, f, indent=4)

print(f"Added {dest_name} to {json_path.name}")
print(f"Total files in history: {len(ark_files)}")
