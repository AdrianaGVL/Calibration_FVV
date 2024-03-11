#Libraries
import os
import json

# Path
main_path = '/media/agv/JesusGTI/Calibration'
scene_path = f'{main_path}/iPhone_Recordings/C_chess/frames'
cv_path = f'{scene_path}/output/matches_for_known'
mvg_path = f'{scene_path}/output/matches'
sfm_data_path = f'{scene_path}/output/sfm_data_with_info.json'

# List files
cv_feats = os.listdir(cv_path)
mvg_feat = list(filter(lambda file: file.endswith('.feat'), os.listdir(mvg_path))) # Only .feat files are requiered

# Images that OpenCV hasn't used
not_cv = list(set(mvg_feat) - set(cv_feats))
print(len(not_cv))

# Remove those file from the sfm_data views
if not not_cv:
    print('OpenCV has used the same frames as OpenMVG did\n')
else:
    sfm_data = ''
    views_to_remove = []
    extrinsic_to_remove = []
    with open(sfm_data_path) as f:
        sfm_data = json.load(f)
    f.close
    for view in sfm_data["views"]:
        frame = view["value"]["ptr_wrapper"]["data"]["filename"]
        frame_key = view["key"]
        feat_frames = frame.split('.')[0]
       # If the file is in not common frames, will be remove from the views
        try:
            match = not_cv.index(f'{feat_frames}.feat')
        except:
            match = 'None'
        
        if type(match) == int:
            continue
        else:
            views_to_remove.append(view)
            for ext in sfm_data["extrinsics"]:
                if frame_key == ext["key"]:
                    extrinsic_to_remove.append(ext)

    for notUsefull in views_to_remove:
        sfm_data["views"].remove(notUsefull)

    for notUsefull2 in extrinsic_to_remove:
        sfm_data["extrinsics"].remove(notUsefull2)

    # Once the loop is finished, a new JSON will be created with the common info
    with open(f'{scene_path}/output/sfm_data_common.json', 'w') as f:
        json.dump(sfm_data, f, indent=4)
    f.close