"""
Script to create ark_files.json by unpacking all .ark.gz files and listing .ark files.
Supports both:
- .ark.gz files that will be unpacked
- Already unpacked .ark files with timestamp format (LostColony_WP_DD.MM.YYYY_HH.MM.SS.ark)
"""
import gzip
import json
from pathlib import Path

history_dir = Path(__file__).parent

# Unpack all .ark.gz files
gz_files = list(history_dir.glob("*.ark.gz"))
print(f"Found {len(gz_files)} .ark.gz files")

for gz_path in gz_files:
    ark_path = gz_path.with_suffix("")  # Remove .gz extension
    if not ark_path.exists():
        print(f"Unpacking {gz_path.name}...")
        with gzip.open(gz_path, 'rb') as f_in:
            with open(ark_path, 'wb') as f_out:
                f_out.write(f_in.read())
    else:
        print(f"Already unpacked: {ark_path.name}")

# Get all .ark files (excluding .ark.gz) - includes both unpacked and manually added files
ark_files = sorted([
    str(p.resolve()) 
    for p in history_dir.glob("*.ark") 
    if not p.name.endswith(".gz")
])

# Count files that came from .gz vs standalone
gz_originated = sum(1 for f in ark_files if (Path(f).parent / (Path(f).name + ".gz")).exists())
standalone = len(ark_files) - gz_originated

print(f"\nFound {len(ark_files)} .ark files:")
print(f"  - {gz_originated} from .ark.gz files")
print(f"  - {standalone} standalone .ark files")

# Save to json
json_path = history_dir / "ark_files.json"
with open(json_path, 'w') as f:
    json.dump(ark_files, f, indent=4)

print(f"\nSaved {len(ark_files)} paths to {json_path.name}")
