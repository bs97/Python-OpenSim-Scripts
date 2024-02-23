from removenoisebeforeik import *
from runik import *
from getquats import *
from angles import *

import tkinter as tk
from tkinter import filedialog

def main():

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

    plotfilename = getAngles(cutfilename)
    print(f"angles plot saved to charts/{plotfilename}")



if __name__ == "__main__":
    main()