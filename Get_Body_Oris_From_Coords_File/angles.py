
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
import os
import sys
import shutil
def getElbowangles(trc_filename):



    # Split the path by '/'
    path_parts = trc_filename.split('/')

    # Take the last part of the path
    last_part = path_parts[-1]

    # Split the last part by '.'
    filename_parts = last_part.split('.')

    # Extract the desired part
    desired_part = filename_parts[0]

    # copy mot file for elbow angles processing
    print("desired_part is")
    print(desired_part)

    # Get the directory of the source file
    source_dir = os.path.dirname(trc_filename)

    # Destination directory
    destination_dir = os.path.join(source_dir, "mots")

    # Destination file name
    destination_file = os.path.join(destination_dir, desired_part + ".mot")

    print(f"elbow file is {destination_file}")

    # Assuming destination_file contains the path to the file
    data = np.loadtxt(destination_file, delimiter='\t', skiprows=11)

    # Now, 'data' contains the content of the file as a NumPy array
    print(data.shape)
    time = data[:, 0]
    el_x = data[:, 16]
    ps_y = data[:, 17]

    print(el_x)
    print(el_x.shape)

    # Combine el_x and ps_y to create angles of shape (2228, 2)
    angles = np.concatenate((el_x[:, np.newaxis], ps_y[:, np.newaxis]), axis=1)

    # Add an additional column of zeros to create angles of shape (2228, 3)
    angles = np.concatenate((angles, np.zeros((angles.shape[0], 1))), axis=1)

    return angles



def getAngles(trc_filename):
    file_path_m = r"Body_Oris.csv"
    dfm = pd.read_csv(file_path_m)


    q_chest = dfm[['Thorax_Q1', 'Thorax_Q2', 'Thorax_Q3','Thorax_Q0']].values
    q_shoulder = dfm[['Humerus_Q1', 'Humerus_Q2', 'Humerus_Q3','Humerus_Q0']].values

    # q_elbow = dfm[['Radius_Q1', 'Radius_Q2', 'Radius_Q3','Radius_Q0']].values

    # Convert the quaternion values to rotation matrices
    R_chest = R.from_quat(q_chest)
    R_shoulder = R.from_quat(q_shoulder)

    # R_elbow = R.from_quat(q_elbow)

    # # Calculate the quaternion representing the orientation of the shoulder relative to the chest
    R_shoulder_chest = R_chest.inv() * R_shoulder
    # R_elbow_shoulder = R_shoulder.inv() * R_elbow


    shoulder_chest_angles = R_shoulder_chest.as_euler('YZY', degrees=True)
    print("angles shape is (3009, 3)")

    elbow_angles = getElbowangles(trc_filename)

    # elbow_angles = R_elbow_shoulder.as_euler('XYZ', degrees=True)


    # Extract filename without path
    filename_without_path = os.path.basename(trc_filename)
    # Extract filename without extension
    filename_without_extension = os.path.splitext(filename_without_path)[0]

    # Create a time array with the adjusted size
    time = np.arange(len(shoulder_chest_angles))
    time_elbow = np.arange(len(elbow_angles))
    # Plot the YZY Euler sequence angles for the shoulder relative to the chest
    plt.plot(time, shoulder_chest_angles[:, 0], label='Plane of Elevation')
    plt.plot(time, shoulder_chest_angles[:, 1], label='Angle of Elevation')
    # plt.plot(time, shoulder_chest_angles[:, 2], label='Rotation')
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    variable_name = "shoulder angles (humerus Relative to Chest)"
    plt.title('YZY Euler Sequence Angles for ' + filename_without_extension)
    plt.legend()
    plt.show()
    plt.close()
    plt.plot(time_elbow, elbow_angles[:, 0], label='elbow flexion')
    plt.plot(time, elbow_angles[:, 1], label='supination pronation')
    # plt.plot(time, elbow_angles[:, 2], label='carrying angle')
    plt.xlabel('Time')
    plt.ylabel('Angle (degrees)')
    plt.title('XYZ Euler Sequence Angles for elbow angles (humerous Relative to radius)')
    plt.legend()
    plt.show()
    plt.close()


    # Construct new filename
    new_filename = f"{filename_without_extension}_yzy.png"

    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)

    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")


    return new_filename, shoulder_chest_angles, elbow_angles

