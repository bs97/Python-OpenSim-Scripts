import os
import opensim as osim
import numpy as np
from scipy.spatial.transform import Rotation as R
import tempfile

def apply_transformations_sag(marker_data):
    # this calculates frontal plane rotations
    print("Original marker data shape:", marker_data.shape)

    # Apply a 180-degree rotation around the y-axis
    transformed_marker_data = marker_data.copy()
    for i in range(len(transformed_marker_data)):
        # Invert x-coordinates for each row
        transformed_marker_data[i, 1::2] *= -1

    print("After 180-degree rotation around y-axis:", transformed_marker_data.shape)

    rotated = transformed_marker_data.copy()

    # Apply a 180-degree rotation around the z-axis
    rotated = marker_data.copy()
    for i in range(len(rotated)):
        # Invert x-coordinates for each row
        rotated[i, 2::3] *= -1
    return marker_data

    print("After 180-degree rotation around z-axis:", transformed_marker_data.shape)

def apply_transformations_front(marker_data):
    # this calculates frontal plane rotations
    print("Original marker data shape:", marker_data.shape)

    # Apply a 180-degree rotation around the z-axis
    transformed_marker_data = marker_data.copy()
    for i in range(len(transformed_marker_data)):
        # Invert x-coordinates for each row
        transformed_marker_data[i, 2::3] *= -1

    print("After 180-degree rotation around z-axis:", transformed_marker_data.shape)


    # Apply a -90 degree rotation around the y-axis
    rotated = transformed_marker_data.copy()
    for i in range(len(rotated)):
        # Extract x, y, and z coordinates
        x_indices = list(range(2, len(rotated[i]) - 1, 3))
        y_indices = list(range(3, len(rotated[i]), 3))
        z_indices = list(range(4, len(rotated[i]) + 1, 3))

        x_coords = rotated[i, x_indices]
        y_coords = rotated[i, y_indices]
        z_coords = rotated[i, z_indices]

        # Apply the rotation
        rotated[i, x_indices] = -z_coords  # New x-coordinates
        # rotated[i, y_indices] = y_coords  # Unchanged y-coordinates
        rotated[i, y_indices] = -y_coords  # Unchanged y-coordinates
        rotated[i, z_indices] = x_coords  # New z-coordinates

    print("After -90 degree rotation around y-axis:", rotated.shape)

    return rotated

def generate_coord_file_from_trc(trc_file, model_file, coord_file, settings_file):

    # Load the model
    model = osim.Model(model_file)

    # Read marker data from TRC file
    marker_data = np.loadtxt(trc_file, skiprows=5)  # Adjust skiprows based on TRC file format

    # Apply transformations
    print(f"trc file is {trc_file}")
    if 'mm' in trc_file:
        # Do something else when 'sag' is in the variable name
        transformed_marker_data = marker_data
        print("mm data no transformation required ")
    elif 'front' in trc_file:
        # Do something when 'front' is in the variable name
        transformed_marker_data = apply_transformations_front(marker_data)
        print("frontal plane ")
    elif 'sag' in trc_file:
        # Do something else when 'sag' is in the variable name
        transformed_marker_data = apply_transformations_sag(marker_data)
        print("sag plane ")
    else:
        # Neither 'front' nor 'sag' in the variable name
        print("Plane not defined")




    # Save transformed marker data to a temporary file in the same directory as the script
    temp_dir = os.path.dirname(os.path.abspath(__file__))
    temp_file_path = os.path.join(temp_dir, "temp_marker_data.trc")

    # Get marker names and original header from the original TRC file
    with open(trc_file, "r") as trc:
        header_lines = trc.readlines()[:5]  # Assuming the header is contained in the first 10 lines

    # Write header with original header to the temporary TRC file
    with open(temp_file_path, "w") as temp_file:
        temp_file.writelines(header_lines)
        np.savetxt(temp_file, transformed_marker_data, delimiter="\t", fmt="%.6f")

    # Create Inverse Kinematics Tool
    ik_tool = osim.InverseKinematicsTool(settings_file)
    ik_tool.setModel(model)
    ik_tool.setMarkerDataFileName(temp_file_path)  # Pass the temporary file path
    ik_tool.setOutputMotionFileName(coord_file)  # Set the output motion file directly

    # Run Inverse Kinematics
    ik_tool.run()
# Now, call the function to generate the coord_file
template_trc_file = "1sagsabdmm.trc"  # Update this with your template TRC file path
model_file = "das3_scaled_and_placed.osim"
coord_file = "OMC_IK_results.mot"  # Update this with your desired coord_file name/path
settings_file = "runik.xml"  # Update this with your settings file path

generate_coord_file_from_trc(template_trc_file, model_file, coord_file, settings_file)

