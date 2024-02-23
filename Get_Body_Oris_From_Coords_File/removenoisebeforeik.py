import matplotlib.pyplot as plt
import numpy as np



def removeNoise(original_trc):
    # Load data, skipping only the first two header rows
    marker_data = np.loadtxt(original_trc, skiprows=5)

    # Select the 54th column
    x = marker_data[:, 53]  # Python's 0-based indexing, so 53 corresponds to the 54th column
    y = marker_data[:, 54]
    z = marker_data[:, 55]

    # Create a plot for the 54th column
    plt.plot(x, marker='o', linestyle='-', color='b')
    plt.plot(y, marker='o', linestyle='-', color='b')
    plt.plot(z, marker='o', linestyle='-', color='b')

    # Initialize start and stop variables
    start = None
    stop = None

    # Define a function to handle mouse click events and set start and stop variables
    def on_click(event):
        nonlocal start, stop
        if event.button == 1:  # Left mouse button
            if start is None:
                start = int(event.xdata)
                print(f"Start set to {start}")
            elif stop is None:
                stop = int(event.xdata)
                print(f"Stop set to {stop}")
                plt.close()

    # Connect the mouse click event to the handler function
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)

    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title('Plot of the 54th column of marker_data')
    plt.grid(True)
    plt.show()

    # Print the values of start and stop
    print(f"Start: {start}")
    print(f"Stop: {stop}")


    # Get marker names and original header from the original TRC file
    with open(original_trc, "r") as trc:
        lines = trc.readlines()  # Read all lines at once
        header_lines = lines[:5]  # Assuming the header is contained in the first 5 lines
        data = lines[start:stop]  # Extract data lines based on start and stop variables

    cutfilename = original_trc[:-4] + "_cut.trc"
    # Write header with original header to the temporary TRC file
    with open(cutfilename, "w") as temp_file:
        temp_file.writelines(header_lines)
        temp_file.writelines(data)

    return cutfilename
