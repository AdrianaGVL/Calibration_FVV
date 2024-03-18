#Libraries
import operator
import glob
from natsort import natsorted
import json

# Paths
main_path = '/media/agv/JesusGTI/Calibration'
scene_path = f'{main_path}/iPhone_Recordings/C_chess'    
savepath = f'{scene_path}/output/matches_for_known'
sfm_data_file = f'{scene_path}/output/sfm_data.json'

# All files
feats_files = natsorted(glob.glob(f'{savepath}/*.feat'))

# ID given by OpenMVG
sfm_data = ''
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

filenames = []
ids = []
for view in sfm_data["views"]:
    filename = view["value"]["ptr_wrapper"]["data"]["filename"]
    filenames.append(filename)
    id = view["value"]["ptr_wrapper"]["data"]["id_view"]
    ids.append(id)

# Matches
for j in range(len(feats_files)):
    first_file = feats_files.pop(0)
    file1_id, file2_id = '', ''
    data1 = []

    with open(f'{first_file}', 'r') as f:
        pos = 0
        file_file = first_file.split('/')[-1]
        file_file = file_file.split('.')[0]
        file_file = f'{file_file}.jpeg'

        # Index to obtain the ID.
        try:
            match = filenames.index(file_file)
        except:
            match = 'None'

        if type(match) == int:
            file1_id = ids[match]

        for line in f:
                aux = []
                for coord in line.split(" "):
                    aux.append(float(coord))
                    if len(aux)==2:
                        break
                aux.append(pos)
                data1.append(aux.copy())
                pos += 1
    f.close

    # Sort corners by columns and files
    # data1.sort(key = operator.itemgetter(0, 1))

    for feat in feats_files:
        data2 = []
        with open(feat, 'r') as f:
            pos = 0
            file_file = feat.split('/')[-1]
            file_file = file_file.split('.')[0]
            file_file = f'{file_file}.jpeg'

            # Index to obtain the ID.
            try:
                match = filenames.index(file_file)
            except:
                match = 'None'

            if type(match) == int:
                file2_id = ids[match]

            for line in f:
                    aux = []
                    for coord in line.split(" "):
                        aux.append(float(coord))
                        if len(aux) == 2:
                            break
                    aux.append(pos)
                    data2.append(aux.copy())
                    pos += 1
        f.close

        # Sort corners by columns and files
        # data2.sort(key = operator.itemgetter(0, 1))

        with open(f"{savepath}/pairs.txt", "a") as p:
            p.write(f'{file1_id} {file2_id}\n')
        p.close

        with open(f"{savepath}/matches.putative.txt", "a") as m:
            m.write(f'{file1_id} {file2_id}\n')
            m.write(f'{len(data1)}\n')
            for i in range(len(data1)):
                m.write(f'{data1[i][2]} {data2[i][2]}\n')
        m.close