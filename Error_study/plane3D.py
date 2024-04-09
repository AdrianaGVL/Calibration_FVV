#######################
#  Created on: April 1, 2024
#  Author: Adriana GV
#######################

# Libraries
import json
import numpy as np
import statistics
import trimesh
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Options
interactive_plot = False

# Paths
scene = 'Video_Chess_D'
main_path = '/Users/agv/Estudios/Universidad/Máster/TFM/3D_Reconstruction'
scene_path = f'{main_path}/{scene}'
results_path = f'{scene_path}/output'
sfm_data_file = f'{results_path}/Reconstruction_for_known/cloud_and_poses.json'
chess_error_path = f'{results_path}/errors_chess.json'

# Read the reconstruction data
with open(sfm_data_file) as f:
    sfm_data = json.load(f)
f.close

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

# Regression LS
coefficients, _, _, _ = np.linalg.lstsq(X, points[:, 2], rcond=None)
A, B, C = coefficients[:3]

# JSON structure
errors = {
    "Plane equation": '',
    "Error with respect to the plane":{
        "Mean": '',
        "Standard deviation": '',
        "Max. value": '',
        "Mix. value": ''
    },
    "Distance to the plane per point": []
}
point_err = {
    "Point ID": '',
    "Distance": ''
}

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
    A, B, C = coefficients[:3]
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
z_plane = coefficients[0] * x_grid + coefficients[1] * y_grid + coefficients[2]

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
    Z_plane = coefficients[0] * X_plane + coefficients[1] * Y_plane + coefficients[2]

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