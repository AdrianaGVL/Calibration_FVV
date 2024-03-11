import os
import cv2

# Paths
main_path = '/media/agv/JesusGTI/Calibration'
scene_path = f'{main_path}/iPhone_Recordings/C_chess/frames'    
savepath = f'{scene_path}/output/matches_for_known'

data = ''
with open(savepath, 'rb') as f:
    data = f.read()
f.close

# decoded_data = data.decode('utf-8')
print(data.hex())

bytes_data = bytes.fromhex(data.hex())

# Convertir los bytes en una lista de enteros
int_data = [int(byte) for byte in bytes_data]

print(int_data)