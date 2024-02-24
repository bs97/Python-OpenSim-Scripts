from removenoisebeforeik import *
from runik import *
from getquats import *
from angles import *

import tkinter as tk
from tkinter import filedialog

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
def collect():
    # original_trc = "1sagsflexkinect28jan.trc"

    root = tk.Tk()
    root.withdraw()  # Hide the main tkinter window

    # Prompt user to select a file
    original_trc = filedialog.askopenfilename(title="Select TRC file")

    if "mm" in original_trc:
        print("The filename contains 'mm'.")
        cutfilename = original_trc
    else:
        cutfilename = removeNoise(original_trc)

        print(f"cut file name is {cutfilename}")


    if runIk(cutfilename):
        print("inverse kinematics complete ")
    else:
        print("return IK failed")


    if getQuats():
        print("orientations of bodies complete")
    else:
        print("return orientations failed")

    plotfilename, shoulder_chest_angles = getAngles(cutfilename)
    print(f"angles plot saved to charts/{plotfilename}")

    return shoulder_chest_angles

def main():
    shoulder_chest_angles_kinect = collect()
    shoulder_chest_angles_mm = collect()

    print(f"type of shoulder_chest_angles_k is {type(shoulder_chest_angles_kinect)}")
    print(f"shape of shoulder_chest_angles_k is {shoulder_chest_angles_kinect.shape}")

    print(f"type of shoulder_chest_angles_mm is {type(shoulder_chest_angles_mm)}")
    print(f"shape of shoulder_chest_angles_mm is {shoulder_chest_angles_mm.shape}")

    mmstartcut = 500
    mmendcut = -500
    shoulder_chest_angles_mm = shoulder_chest_angles_mm[mmstartcut:mmendcut]


    correlationangle = 1

    common_len = min(len(shoulder_chest_angles_mm), len(shoulder_chest_angles_kinect))

    # Compute cross-correlation between the signals using numpy.correlate
    cross_corr = np.correlate(
        shoulder_chest_angles_mm[:common_len, correlationangle],
        # Consider only the first column (change if needed)
        shoulder_chest_angles_kinect[:common_len, correlationangle],
        # Consider only the first column (change if needed)
        mode="full"
    )
    print("cor is shoulder")

    # Find the index of the maximum correlation value (offset)
    max_corr_idx = np.argmax(cross_corr)

    # Compute the offset in the time domain (index units)
    offset = max_corr_idx - common_len + 1

    shoulder_chest_angles_mm_shifted = shoulder_chest_angles_mm
    shoulder_chest_angles_kinect_shifted = shoulder_chest_angles_kinect

    # elbow_angles_kinect_shifted = elbow_angles_kinect
    # elbow_angles_mm_shifted = elbow_angles_mm
    print("Offset (in time steps):", offset)

    if offset < 0:
        shoulder_chest_angles_kinect_shifted = shoulder_chest_angles_kinect[
                                               abs(offset):abs(offset) + len(shoulder_chest_angles_mm)]
        # elbow_angles_kinect_shifted = elbow_angles_kinect[abs(offset):abs(offset) + len(elbow_angles_mm)]
        print("offset k")
    else:
        shoulder_chest_angles_mm_shifted = shoulder_chest_angles_mm[
                                           abs(offset):abs(offset) + len(shoulder_chest_angles_kinect)]
        # elbow_angles_mm_shifted = elbow_angles_mm[abs(offset):abs(offset) + len(elbow_angles_kinect)]
        print("offset mm")

    # Update the time arrays
    time_mm = np.arange(len(shoulder_chest_angles_mm_shifted))
    time_kinect = np.arange(len(shoulder_chest_angles_kinect_shifted))

    print("shapes before")
    print(shoulder_chest_angles_mm_shifted.shape)
    print(shoulder_chest_angles_kinect_shifted.shape)

    # Assuming you have the two numpy ndarrays: shoulder_chest_angles_mm_shifted and shoulder_chest_angles_kinect_shifted

    # Step 1: Find the length of each array
    length_mm = shoulder_chest_angles_mm_shifted.shape[0]
    length_kinect = shoulder_chest_angles_kinect_shifted.shape[0]

    # Step 2: Determine the longer array
    if length_mm > length_kinect:
        longer_array_namea = "shoulder_chest_angles_mm_shifted"
        shorter_array_namea = "shoulder_chest_angles_kinect_shifted"
        longer_arraya = shoulder_chest_angles_mm_shifted
        shorter_arraya = shoulder_chest_angles_kinect_shifted

        # longer_array_nameb = "elbow_angles_mm_shifted"
        # shorter_array_nameb = "elbow_angles_kinect_shifted"
        # longer_arrayb = elbow_angles_mm_shifted
        # shorter_arrayb = elbow_angles_kinect_shifted
        print("mm longer")
    else:
        longer_array_namea = "shoulder_chest_angles_kinect_shifted"
        shorter_array_namea = "shoulder_chest_angles_mm_shifted"
        longer_arraya = shoulder_chest_angles_kinect_shifted
        shorter_arraya = shoulder_chest_angles_mm_shifted

        # longer_array_nameb = "elbow_angles_kinect_shifted"
        # shorter_array_nameb = "elbow_angles_mm_shifted"
        # longer_arrayb = elbow_angles_kinect_shifted
        # shorter_arrayb = elbow_angles_mm_shifted
        print("kinect longer")

    # Step 3: Slice the longer array to match the length of the shorter array
    sliced_longer_arraya = longer_arraya[:len(shorter_arraya)]
    # sliced_longer_arrayb = longer_arrayb[:len(shorter_arrayb)]

    # Replace the information in the original arrays
    globals()[longer_array_namea] = sliced_longer_arraya
    globals()[shorter_array_namea] = shorter_arraya

    # globals()[longer_array_nameb] = sliced_longer_arrayb
    # globals()[shorter_array_nameb] = shorter_arrayb

    print("shapes after FINAL ")
    print(shoulder_chest_angles_mm_shifted.shape)
    print(shoulder_chest_angles_kinect_shifted.shape)

    # print(elbow_angles_mm_shifted.shape)
    # print(elbow_angles_kinect_shifted.shape)

    # Update the time arrays
    time_mm = np.arange(len(shoulder_chest_angles_mm_shifted))
    time_kinect = np.arange(len(shoulder_chest_angles_kinect_shifted))
    print("angles after array cut (same size)")

    for plotangle in range(3):
        # Plot the YZY Euler sequence angles for the shoulder relative to the chest
        # dont plot srot angles and elbow rot,carry due to errors:

        # if plotangle < 2:
        plt.plot(time_mm, shoulder_chest_angles_mm_shifted[:, plotangle], label='Angle of Elevation mm')
        plt.plot(time_kinect, shoulder_chest_angles_kinect_shifted[:, plotangle], label='Angle of Elevation kinect')
        plt.xlabel('Time')
        plt.ylabel('Angle (degrees)')
        plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to Chest)')
        plt.legend()
        plt.show()



print("done processing")

if __name__ == "__main__":
    main()