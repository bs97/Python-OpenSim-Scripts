from removenoisebeforeik import *
from runik import *
from getquats import *
from angles import *

import tkinter as tk
from tkinter import filedialog

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

import shutil
def collect():
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

    plotfilename, shoulder_chest_angles, elbow_angles = getAngles(cutfilename)
    print(f"angles plot saved to charts/{plotfilename}")

    return shoulder_chest_angles, elbow_angles

def main():
    shoulder_chest_angles_kinect, elbow_angles_kinect = collect()
    shoulder_chest_angles_mm, elbow_angles_mm = collect()

    mmstartcut = 500
    mmendcut = -500
    shoulder_chest_angles_mm = shoulder_chest_angles_mm[mmstartcut:mmendcut]
    elbow_angles_mm = elbow_angles_mm[mmstartcut:mmendcut]

    correlationangle = 0

    common_len = min(len(shoulder_chest_angles_mm), len(shoulder_chest_angles_kinect))

    # Compute cross-correlation between the signals using numpy.correlate
    cross_corr = np.correlate(
        shoulder_chest_angles_mm[:common_len, correlationangle],
        shoulder_chest_angles_kinect[:common_len, correlationangle],
        mode="full"
    )

    # Find the index of the maximum correlation value (offset)
    max_corr_idx = np.argmax(cross_corr)

    # Compute the offset in the time domain (index units)
    offset = max_corr_idx - common_len + 1

    shoulder_chest_angles_mm_shifted = shoulder_chest_angles_mm
    shoulder_chest_angles_kinect_shifted = shoulder_chest_angles_kinect
    elbow_angles_mm_shifted = elbow_angles_mm
    elbow_angles_kinect_shifted = elbow_angles_kinect

    if offset < 0:
        shoulder_chest_angles_kinect_shifted = shoulder_chest_angles_kinect[
                                               abs(offset):abs(offset) + len(shoulder_chest_angles_mm)]
        elbow_angles_kinect_shifted = elbow_angles_kinect[
                                               abs(offset):abs(offset) + len(elbow_angles_mm)]
    else:
        shoulder_chest_angles_mm_shifted = shoulder_chest_angles_mm[
                                           abs(offset):abs(offset) + len(shoulder_chest_angles_kinect)]
        elbow_angles_mm_shifted = elbow_angles_mm[abs(offset):abs(offset) + len(elbow_angles_kinect)]

    time_mm = np.arange(len(shoulder_chest_angles_mm_shifted))
    time_kinect = np.arange(len(shoulder_chest_angles_kinect_shifted))

    print("angles after array cut (same size)")

    for plotangle in range(3):
        # Plot the YZY Euler sequence angles for the shoulder relative to the chest
        # dont plot srot angles and elbow rot,carry due to errors:

        # if plotangle < 2:
        print(f"plot angle is{plotangle}")
        plt.plot(time_mm, shoulder_chest_angles_mm_shifted[:, plotangle], label='shoulder mm')
        plt.plot(time_kinect, shoulder_chest_angles_kinect_shifted[:, plotangle], label='shoulder kinect')
        plt.xlabel('Frame')
        plt.ylabel('Angle (degrees)')
        plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to Chest)')
        plt.legend()
        plt.show()


    for plotangle in range(2):
        # Plot the YZY Euler sequence angles for the shoulder relative to the chest
        # dont plot srot angles and elbow rot,carry due to errors:

        # if plotangle < 2:
        plt.plot(time_mm, elbow_angles_mm_shifted[:, plotangle], label='elbow angles mm')
        plt.plot(time_kinect, elbow_angles_kinect_shifted[:, plotangle], label='elbow angles kinect')
        plt.xlabel('Frame')
        plt.ylabel('Angle (degrees)')
        plt.title('YZY Euler Sequence Angles for elbow angles (radius Relative to humerous)')
        plt.legend()
        plt.show()







print("done processing")

if __name__ == "__main__":
    main()