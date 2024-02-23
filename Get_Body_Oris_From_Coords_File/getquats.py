# This script takes a .mot file containing time-series model 'coordinates' (which is the format of OpenSim's IK results)
# creates an .sto file containing time-series 'states', then combines the model with the states so that model attributes
# can be extracted - e.g. body orientations.

# Notes - you'll see errors about missing .vtp files - these are just geometry files which we don't need right now

from functions import *
import re

def getQuats():
    # Files that need to be in folder:
        # functions.py
        # analyse settings template .xml file
        # model file (the same one which was used for the IK)
        # .mot coordinates file (IK results)

    """ SETTINGS """

    analyze_settings_template_file = "Analysis_Settings.xml"
    model_file = "das3_scaled_and_placed.osim"
    coord_file = "OMC_IK_results.mot"

    results_path = r"C:\Users\bradl\Documents\GitHub\Python-OpenSim-Scripts\Get_Body_Oris_From_Coords_File"   # Folder where you want the analyze tool to write the states file
    # start_time = 0 # Time interval you want to analyze (time stamp, in whatever units are in the .mot file)
    # end_time = 3571
    """ MAIN """

    # find time from mot file and replace in xml
    # Read the motion file (mot) to extract start and end times
    with open("OMC_IK_results.mot", "r") as file:
        # Skip header lines until you reach the data
        for line in file:
            if not line.startswith("endheader"):
                continue
            break

        # Skip the first row containing column headers
        next(file)

        # Read the start time from the first data row
        first_data_row = next(file)
        start_time = float(first_data_row.split()[0])

        # Read the last row to get the end time
        for last_data_row in file:
            pass

        # Get the end time from the last row
        end_time = float(last_data_row.split()[0])

        # Read the XML file into a string
        with open("Analysis_Settings.xml", "r") as file:
            xml_content = file.read()

        # Define the regular expressions for finding placeholder strings
        initial_time_pattern = re.compile(r"<initial_time>(.*?)<\/initial_time>")
        final_time_pattern = re.compile(r"<final_time>(.*?)<\/final_time>")

        # Replace the placeholder strings with start and end times
        xml_content = initial_time_pattern.sub(f"<initial_time>{start_time}</initial_time>", xml_content)
        xml_content = final_time_pattern.sub(f"<final_time>{end_time}</final_time>", xml_content)

        # Write the modified XML content back to a file
        with open("Analysis_Settings.xml", "w") as file:
            file.write(xml_content)


    # Create states file from coordinates file
    create_states_file_from_coordinates_file(analyze_settings_template_file, model_file, coord_file,
                                             results_path, start_time, end_time)

    # Get body orientations from states file and save to csv
    get_body_quats_from_states("OMC_StatesReporter_states.sto", model_file, results_path)

    # Read in the new csv file
    thorax_OMC, humerus_OMC, radius_OMC = read_in_quats(start_time, end_time, file_name=results_path + r"\Body_Oris.csv", trim_bool=False)

    # Get humero-thoracic joint angles from the thorax and humerus orientations
    eul_1, eul_2, eul_3 = get_JA_euls_from_quats(thorax_OMC, humerus_OMC, eul_seq="YZY")

    return True


