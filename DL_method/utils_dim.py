################################################################################
#  Author: DEEP IMAGE MATCHING GitHub repository                               #
#  GitHub: https://github.com/3DOM-FBK/deep-image-matching.git                 #
################################################################################
#  Some modifications have been done in order to use with the restof the code  #
#  Created on: June 12, 2024                                                   #
#  Modifications author: Adriana GV                                            #
################################################################################

# Libraries
import h5py
import os
from tqdm import tqdm
import threading
import numpy as np
import shutil

def saveFeaturesOpenMVG(matches_folder, basename, keypoints):
    with open(f"{matches_folder}/{basename}.feat", "w") as feat:
        for x, y in keypoints:
            feat.write(f"{x} {y} 1.0 0.0\n")


def saveDescriptorsOpenMVG(matches_folder, basename, descriptors):
    with open(f"{matches_folder}/{basename}.desc", "wb") as desc:
        desc.write(len(descriptors).to_bytes(8, byteorder="little"))
        desc.write(
            ((descriptors + 1) * 0.5 * 255).round(0).astype(np.ubyte).tobytes()
        )

def saveMatchesOpenMVG(matches, out_folder):
    with open(f'{out_folder}/matches.putative.bin', "wb") as bin:
        bin.write((1).to_bytes(1, byteorder="little"))
        bin.write(len(matches).to_bytes(8, byteorder="little"))
        for index1, index2, idxs in matches:
            bin.write(index1.tobytes())
            bin.write(index2.tobytes())
            bin.write(len(idxs).to_bytes(8, byteorder="little"))
            bin.write(idxs.tobytes())
    shutil.copyfile(f"{out_folder}/matches.putative.bin", f"{out_folder}/matches.f.bin")


def add_keypoints(h5_path, image_path, matches_dir):
    keypoint_f = h5py.File(str(h5_path), "r")
    for filename in tqdm(list(keypoint_f.keys())):
        keypoints = keypoint_f[filename]["keypoints"].__array__()
        descriptors = keypoint_f[filename]["descriptors"].__array__()
        name = filename.split('.')[0]

        if len(keypoints.shape) >= 2:
            threading.Thread(
                target=lambda: saveFeaturesOpenMVG(matches_dir, name, keypoints)
            ).start()
            threading.Thread(target=lambda: saveDescriptorsOpenMVG(matches_dir, name, descriptors)).start()
    return



def add_matches(h5_path, matches_dir, filenames, ids):
    putative_matches = []
    match_file = h5py.File(str(h5_path), "r")
    added = set()
    n_keys = len(match_file.keys())
    n_total = (n_keys * (n_keys - 1)) // 2

    with tqdm(total=n_total) as pbar:
        for key_1 in match_file.keys():
            group = match_file[key_1]
            # Index to obtain the ID.
            try:
                match_1 = filenames.index(key_1)
            except:
                match_1 = 'None'

            if type(match_1) == int:
                id_1 = ids[match_1]

            for key_2 in group.keys():
                try:
                    match_2 = filenames.index(key_2)
                except:
                    match_2 = 'None'

                if type(match_2) == int:
                    id_2 = ids[match_2]

                    if (id_1, id_2) in added:
                        print(f"Pair ({id_1}, {id_2}) already added!")
                        continue
                    matches = group[key_2][()]
                    putative_matches.append(
                        [np.int32(id_1), np.int32(id_2), matches.astype(np.int32)]
                    )
                    with open(f"{matches_dir}/pairs.txt", "a") as p:
                        p.write(f'{id_1} {id_2}\n')
                    p.close
                    added.add((id_1, id_2))
                    pbar.update(1)
    match_file.close()
    saveMatchesOpenMVG(putative_matches, matches_dir)