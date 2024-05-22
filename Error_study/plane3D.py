#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import yaml
import numpy as np
from scipy.odr import Model, Data, ODR
import statistics
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Options
interactive_plot = False

# Paths
# Config file
with open('./config_file.yml', 'r') as config_file:
    config = yaml.safe_load(config_file)
config_file.close

# Main Parameters & directories
main_path = config["working_path"]
scene = f'{main_path}/{config["scene"]}'
output_path = f'{scene}/{config["out_path"]}'
# App paths
known_reconst = f'{output_path}/{config["known_poses"]}'
results_path = f'{output_path}/{config["plane_path"]}'
# App files
jsons_path = './jsons_structures.json'
sfm_data_file = f'{known_reconst}/{config["known_sfm_data"]}'
chess_error_path = f'{results_path}/{config["plane_file"]}'

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

# JSON Structure
# Read the reconstruction data
with open(jsons_path) as j:
    json_model = json.load(j)
j.close

errors = json_model["Plane 3D"]
point_err = json_model["Points_to_Plane"]

points_3D = []
for coords in sfm_data["structure"]:
    x_point = coords["value"]["X"][0]
    y_point = coords["value"]["X"][1]
    z_point = coords["value"]["X"][2]
    point_3D = (x_point, y_point, z_point)
    points_3D.append(point_3D)

points = np.array(points_3D)

# Matrix
X = np.column_stack((points[:, 0], points[:, 1], np.ones(len(points))))

# ODR Regression
def model_func(beta, x):
    return beta[0]*x[0] + beta[1]*x[1] + beta[2]
data = Data(X.T, points[:, 2])
coefss = [1.0, 1.0, 1.0]
model = Model(model_func)
odr = ODR(data, model, beta0=coefss)
odr_result = odr.run()
A, B, C = odr_result.beta[:3]

# Error
errors["Plane equation"] = f"Plane equation: {A}x + {B}y + {C} = 0"
x_points, y_points, z_points = points[:, 0], points[:, 1], points[:, 2]
denominator = np.sqrt(A**2 + B**2 + 1)
distances = np.abs(A*x_points + B*y_points - z_points + C) / denominator
errors['Error with respect to the plane']["Mean"] = statistics.mean(distances)
errors['Error with respect to the plane']["Standard deviation"] = statistics.stdev(distances)
errors['Error with respect to the plane']["Max. value"] = max(distances)
errors['Error with respect to the plane']["Mix. value"] = min(distances)

# Error per point
for i, point in enumerate(points):
    A, B, C = odr_result.beta[:3]
    x_point, y_point, z_point = point
    denominator = np.sqrt(A**2 + B**2 + 1)
    point_err['Point ID'] = i
    point_err['Distance'] = np.abs(A*x_point + B*y_point - z_point + C) / denominator
    errors['Distance to the plane per point'].append(point_err.copy())

# Save data
with open(f'{chess_error_path}', 'w') as pqs:
    json.dump(errors, pqs, indent=4)
pqs.close

# Plane
x_min, x_max = points[:, 0].min(), points[:, 0].max()
y_min, y_max = points[:, 1].min(), points[:, 1].max()
x_grid, y_grid = np.meshgrid(np.linspace(x_min, x_max, 10), np.linspace(y_min, y_max, 10))
z_plane = A * x_grid + B * y_grid + C

# Save points as a Point cloud
trimesh.points.PointCloud(points).export(f'{results_path}/points.ply')

# Create the plane
faces = []
for i in range(len(x_grid) - 1):
    for j in range(len(x_grid[i]) - 1):
        v0 = i * len(x_grid[i]) + j
        v1 = v0 + 1
        v2 = v0 + len(x_grid[i])
        v3 = v2 + 1
        faces.append([v0, v1, v2])
        faces.append([v1, v3, v2])

# Save the plane
trimesh.Trimesh(vertices=np.column_stack((x_grid.flatten(), y_grid.flatten(), z_plane.flatten())),
                faces=faces).export(f'{results_path}/plane.ply')


if interactive_plot:
    # Figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot points
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], color='yellow', label='Points')

    # Obtain the plane
    x_min, x_max = points[:, 0].min(), points[:, 0].max()
    y_min, y_max = points[:, 1].min(), points[:, 1].max()
    X_plane, Y_plane = np.meshgrid(np.arange(x_min, x_max, 1), np.arange(y_min, y_max, 1))
    Z_plane = A * X_plane + B * Y_plane + C

    # Plot the plane
    ax.plot_surface(X_plane, Y_plane, Z_plane, alpha=0.5, color='black', label='Plane')

    # labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()

    # Update the view
    def update(elev, azim):
        ax.view_init(elev=elev, azim=azim)

    # Interactive animation 
    from matplotlib.animation import FuncAnimation
    ani = FuncAnimation(fig, update, frames=np.linspace(0, 360, 360), interval=50)

    plt.show()