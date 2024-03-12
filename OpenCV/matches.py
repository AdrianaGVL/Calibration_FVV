#Libraries
import operator
import glob
from natsort import natsorted

# Paths
main_path = '/media/agv/JesusGTI/Calibration'
scene_path = f'{main_path}/iPhone_Recordings/C_chess/frames'    
savepath = f'{scene_path}/output/matches_for_known'

# All files
feats_files = natsorted(glob.glob(f'{savepath}/*.feat'))
print(len(feats_files))

# # Matches
# for j in range(len(feats_files)):
#     first_file = feats_files.pop(0)
#     data1, data2 = [], []

#     with open(f'{first_file}', 'r') as f:
#         pos = 0
#         file_file1 = first_file.split('/')[-1]
#         file_file1 = int(file_file1.split('.')[0]) - 1
#         for line in f:
#                 aux = []
#                 for coord in line.split(" "):
#                     aux.append(float(coord))
#                 aux.append(pos)
#                 data1.append(aux.copy())
#                 pos += 1
#     f.close

#     # Sort corners by colums and files
#     data1.sort(key = operator.itemgetter(0, 1))

#     for feat in feats_files:
#         with open(feat, 'r') as f:
#             pos = 0
#             file_file2 = feat.split('/')[-1]
#             file_file2 = int(file_file2.split('.')[0]) - 1
#             for line in f:
#                     aux = []
#                     for coord in line.split(" "):
#                         aux.append(float(coord))
#                     aux.append(pos)
#                     data2.append(aux.copy())
#                     pos += 1
#         f.close

#         # Sort corners by colums and files
#         data2.sort(key = operator.itemgetter(0, 1))

#         with open(f"{savepath}/pairs.txt", "a+") as p:
#             p.write(f'{file_file1} {file_file2}\n')
#         p.close

#         with open(f"{savepath}/matches.f.txt", "a+") as m:
#             m.write(f'{file_file1} {file_file2}\n')
#             for i in range(len(data1)):
#                 m.write(f'{data1[i][2]} {data2[i][2]}\n')
#         m.close