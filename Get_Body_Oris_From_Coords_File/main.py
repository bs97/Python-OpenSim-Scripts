from removenoisebeforeik import *
from runik import *
from getquats import *
from angles import *

import tkinter as tk
from tkinter import filedialog

from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

import shutil


def plotSyncedAngles(time_mm,time_kinect,shoulder_chest_angles_mm_shifted,shoulder_chest_angles_kinect_shifted,elbow_angles_mm_shifted,elbow_angles_kinect_shifted):
    # Plot the YZY Euler sequence angles for the shoulder relative to the chest
    # dont plot srot angles and elbow rot,carry due to errors:

    plt.plot(time_mm, shoulder_chest_angles_mm_shifted[:, 0], label='plane of elevation mm')
    plt.plot(time_kinect, shoulder_chest_angles_kinect_shifted[:, 0], label='plane of elevation kinect')
    plt.xlabel('Frame')
    plt.ylabel('Angle (degrees)')
    plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to thorax)')
    plt.legend()

    # Construct new filename
    new_filename = f"shoulder_plane_of_elevation.png"
    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")

    plt.show()
    plt.close()

    plt.plot(time_mm, shoulder_chest_angles_mm_shifted[:, 1], label='angle of elevation mm')
    plt.plot(time_kinect, shoulder_chest_angles_kinect_shifted[:, 1], label='angle of elevation kinect')
    plt.xlabel('Frame')
    plt.ylabel('Angle (degrees)')
    plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to thorax)')
    plt.legend()

    # Construct new filename
    new_filename = f"shoulder_angleofelevation.png"
    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")

    plt.show()
    plt.close()

    plt.plot(time_mm, shoulder_chest_angles_mm_shifted[:, 2], label='rotation mm')
    plt.plot(time_kinect, shoulder_chest_angles_kinect_shifted[:, 2], label='rotation kinect')
    plt.xlabel('Frame')
    plt.ylabel('Angle (degrees)')
    plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to thorax)')
    plt.legend()

    # Construct new filename
    new_filename = f"shoulder_rotation.png"
    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")

    plt.show()
    plt.close()

    # Plot the YZY Euler sequence angles for the shoulder relative to the chest
    # dont plot srot angles and elbow rot,carry due to errors:

    # if plotangle < 2:
    plt.plot(time_mm, elbow_angles_mm_shifted[:, 0], label='elbow flexion mm')
    plt.plot(time_kinect, elbow_angles_kinect_shifted[:, 0], label='elbow flexion kinect')
    plt.xlabel('Frame')
    plt.ylabel('Angle (degrees)')
    plt.title('XYZ Euler Sequence Angles for elbow angles')
    plt.legend()


    # Construct new filename
    new_filename = f"elbow_flexion.png"
    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")
    plt.show()
    plt.close()


    plt.plot(time_mm, elbow_angles_mm_shifted[:, 1], label='supination pronation mm')
    plt.plot(time_kinect, elbow_angles_kinect_shifted[:, 1], label='supination pronation kinect')
    plt.xlabel('Frame')
    plt.ylabel('Angle (degrees)')
    plt.title('XYZ Euler Sequence Angles for elbow angles')
    plt.legend()

    # Construct new filename
    new_filename = f"elbow_sup_pro.png"
    # Create the 'charts' directory if it doesn't exist
    os.makedirs("charts", exist_ok=True)
    # Saving plot in /charts directory with new filename
    plt.savefig(f"charts/{new_filename}")

    plt.show()
    plt.close()


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

    # mmstartcut = 500
    # mmendcut = -500
    mmstartcut = 1
    mmendcut = -1
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


    plotSyncedAngles(time_mm,time_kinect,shoulder_chest_angles_mm_shifted,shoulder_chest_angles_kinect_shifted,elbow_angles_mm_shifted,elbow_angles_kinect_shifted)






print("done processing")

if __name__ == "__main__":
    main()