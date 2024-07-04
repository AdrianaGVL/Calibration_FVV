#######################
#  Created on: June 12, 2024
#  Author: Adriana GV
#######################

# Libraries
import h5py

# Read RAW data
filename=''
data = {}
with h5py.File(filename, "r") as fd:
    def recursively_read_group(group, data_dict):
        for key in group:
            item = group[key]
            if isinstance(item, h5py.Dataset):
                data_dict[key] = item[()]
                # Check for attributes, like 'uncertainty' on 'keypoints'
                if key == "keypoints" and "uncertainty" in item.attrs:
                    data_dict[f"{key}_uncertainty"] = item.attrs["uncertainty"]
            elif isinstance(item, h5py.Group):
                data_dict[key] = {}
                recursively_read_group(item, data_dict[key])
    
    recursively_read_group(fd, data)

# Imprimir los datos
for group_name, group_data in data.items():
    print(f"Group: {group_name}")
    for dataset_name, dataset_data in group_data.items():
        print(f"  Dataset: {dataset_name}")
        print(f"  Data: {dataset_data}")