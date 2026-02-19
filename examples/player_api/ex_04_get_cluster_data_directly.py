from pathlib import Path
from uuid import UUID
from arkparse.object_model.cluster_data.ark_cluster_data import ClusterData
from pathlib import Path

cluster_data_dir=Path.cwd() / "cluster_data" # <-- Adjust the path as needed

def get_files(path: Path) -> list[Path]:
    all = [f for f in path.iterdir() if f.is_file()]
    cluster_files = []
    for f in all:
        try:
            UUID(f.name)
            cluster_files.append(f)
        except:
            continue
    return cluster_files

for file in get_files(cluster_data_dir):
    cluster_data = ClusterData(file.parent, file.name)
    print("\nItems:")
    for item in cluster_data.items:
        print(item)

    print("\nDinos:")
    for dino in cluster_data.dinos:
        print(dino)
