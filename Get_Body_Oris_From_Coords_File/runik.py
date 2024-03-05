import os
import opensim as osim
import numpy as np
from scipy.spatial.transform import Rotation as R
import tempfile
import shutil
from scipy.interpolate import interp1d
import sys
import re

def apply_transformations_sag(marker_data):
    # this calculates sagittal plane rotations
    print("Original marker data shape:", marker_data.shape)

    # # Apply a 180-degree rotation around the y-axis
    rotated = marker_data.copy()
    for i in range(len(rotated)):
        # Invert x-coordinates for each row (starting from the third column)
        rotated[i, 3::3] *= -1

    # Apply a 180-degree rotation around the z-axis
    for i in range(len(rotated)):
        # Invert z-coordinates for each row (starting from the fourth column)
        rotated[i, 5::3] *= -1
        # rotated[i, 5::5] *= -1

    print("After sagittal plane rotations:", rotated.shape)
    return rotated


from scipy.signal import butter, lfilter, resample


def butter_lowpass_filter(data, cutoff, fs, order=2):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data, axis=0)
    return y


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
    mm = False
    original_sampling_rate = 0
    # make sure sampling interval is set to 8.33333 in mm report for 120 hz
    target_sampling_rate = 120

    # Get marker names and original header from the original TRC file
    with open(trc_file, "r") as trc:
        header_lines = trc.readlines()[:5]  # Assuming the header is contained in the first 10 lines
        if not mm:
            print(header_lines)
            print(repr(header_lines[2]))

            # Split the string by tab characters (\t)
            parts = header_lines[2].split('\t')

            print("parts are")
            print(parts)
            print("end parts")
            original_sampling_rate = float(parts[0])

    # Apply transformations
    print(f"trc file is {trc_file}")
    if 'mm' in trc_file:
        # Do something else when 'sag' is in the variable name
        transformed_marker_data = marker_data
        mm = True
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

    if not mm:
        # Set the filter cutoff frequency and sampling frequency
        cutoff_freq = 5  # Adjust this value according to your requirements
        sampling_freq = 30  # Adjust based on your original sampling frequency

        # Pad the data with initial values
        padding_length = 10  # Adjust as needed
        padded_data = np.concatenate(
            [transformed_marker_data[0, 2:] * np.ones((padding_length, transformed_marker_data.shape[1] - 2)),
             transformed_marker_data[:, 2:]])

        # Apply the low-pass Butterworth filter to the marker data
        filtered_marker_data = butter_lowpass_filter(padded_data, cutoff_freq, sampling_freq)
        # Remove the padding from the filtered data
        filtered_marker_data = filtered_marker_data[padding_length:]

        # Stack the arrays (assuming transformed_marker_data[:, :2] contains the timestamps and frame numbers)
        filtered_data_with_timestamps = np.column_stack([transformed_marker_data[:, :2], filtered_marker_data])

        transformed_marker_data = filtered_data_with_timestamps


        # upsampling code ********
        # Extract timestamps and data
        timestamps = transformed_marker_data[:, 1]
        data = transformed_marker_data[:, 2:]

        # Define original and target sampling rates
        # original_sampling_rate = 29.68  # Hz
        # target_sampling_rate = 125.16  # Hz
        # target_sampling_rate = 129.32




        # Calculate new timestamps based on the target sampling rate
        original_duration = timestamps[-1] - timestamps[0]
        num_samples_original = len(timestamps)
        num_samples_target = int(num_samples_original * (target_sampling_rate / original_sampling_rate))
        new_timestamps = np.linspace(timestamps[0], timestamps[-1], num_samples_target)

        # Generate frame count starting from 1
        frames = np.arange(1, num_samples_target + 1)

        # Interpolate data to upsample
        upsampled_data = np.zeros((num_samples_target, data.shape[1]))
        for i in range(data.shape[1]):
            interpolator = interp1d(timestamps, data[:, i], kind='linear')
            upsampled_data[:, i] = interpolator(new_timestamps)

        # Combine frames, timestamps, and upsampled data
        upsampled_transformed_marker_data = np.column_stack((frames, new_timestamps, upsampled_data))

        transformed_marker_data = upsampled_transformed_marker_data

    print(f"transformed_marker_data shape is {transformed_marker_data.shape}")
    # Save transformed marker data to a temporary file in the same directory as the script
    temp_dir = os.path.dirname(os.path.abspath(__file__))
    temp_file_path = os.path.join(temp_dir, "temp_marker_data.trc")

    # Get marker names and original header from the original TRC file
    with open(trc_file, "r") as trc:
        header_lines = trc.readlines()[:5]  # Assuming the header is contained in the first 10 lines


    if not mm:
        print(header_lines)
        print(repr(header_lines[2]))

        # Split the string by tab characters (\t)
        parts = header_lines[2].split('\t')

        print("parts are")
        print(parts)
        print("end parts")

        parts[0] = str(target_sampling_rate)
        parts[1] = str(target_sampling_rate)
        parts[5] = str(target_sampling_rate)

        # Replace the third part with a new value
        if len(parts) > 2:
            parts[2] = str(upsampled_data.shape[0])

        # Join the parts back together with tab characters (\t)
        header_lines[2] = '\t'.join(parts)

        print(repr(header_lines[2]))
        print(upsampled_data.shape[0])

        # sys.exit()

    if mm == False:
        # transformed_marker_data[:, 1] /= 1000000 # Convert microseconds to seconds for the second column
        transformed_marker_data[:, 1] = transformed_marker_data[:, 1].astype(
            float) / 1000000  # Convert microseconds to seconds

    with open(temp_file_path, "w") as temp_file:
        temp_file.writelines(header_lines)
        np.savetxt(temp_file, transformed_marker_data, delimiter="\t",
                   fmt=["%d", "%.6f"] + ["%.6f"] * (transformed_marker_data.shape[1] - 2))

    if mm == False:
        trc_file_new = trc_file[:-4] + "_rot.trc"

        # Copy temp_file to trc_file_new
        shutil.copyfile(temp_file_path, trc_file_new)

    # Create Inverse Kinematics Tool
    ik_tool = osim.InverseKinematicsTool(settings_file)
    ik_tool.setModel(model)
    ik_tool.setMarkerDataFileName(temp_file_path)  # Pass the temporary file path
    ik_tool.setOutputMotionFileName(coord_file)  # Set the output motion file directly

    # Run Inverse Kinematics
    ik_tool.run()


def copyMot(cut_trc):


    # Split the path by '/'
    path_parts = cut_trc.split('/')

    # Take the last part of the path
    last_part = path_parts[-1]

    # Split the last part by '.'
    filename_parts = last_part.split('.')

    # Extract the desired part
    desired_part = filename_parts[0]

    # copy mot file for elbow angles processing
    print("desired_part is")
    print(desired_part)


    # Source file name
    source_file = "OMC_IK_results.mot"

    # Get the directory of the source file
    source_dir = os.path.dirname(cut_trc)

    # Destination directory
    destination_dir = os.path.join(source_dir, "mots")

    # Create destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Destination file name
    destination_file = os.path.join(destination_dir, desired_part + ".mot")

    # Copy the file
    shutil.copy(source_file, destination_file)

    print(f"File copied from '{source_file}' to '{destination_file}'.")


def runIk(cut_trc):
    # Now, call the function to generate the coord_file
    template_trc_file = cut_trc  # Update this with your template TRC file path
    model_file = "das3_scaled_and_placed.osim"
    coord_file = "OMC_IK_results.mot"  # Update this with your desired coord_file name/path
    settings_file = "runik.xml"  # Update this with your settings file path

    generate_coord_file_from_trc(template_trc_file, model_file, coord_file, settings_file)

    # copy generated mot file for elbow angles
    copyMot(cut_trc)


    return True

