
import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt

file_path_m = r"Body_Oris.csv"
dfm = pd.read_csv(file_path_m)

# Extract the quaternion values for the chest and shoulder orientations
# q_chest = dfm[['Thorax_Q0', 'Thorax_Q1', 'Thorax_Q2', 'Thorax_Q3']].values
# q_shoulder = dfm[['Humerus_Q0', 'Humerus_Q1', 'Humerus_Q2', 'Humerus_Q3']].values

q_chest = dfm[['Thorax_Q1', 'Thorax_Q2', 'Thorax_Q3','Thorax_Q0']].values
q_shoulder = dfm[['Humerus_Q1', 'Humerus_Q2', 'Humerus_Q3','Humerus_Q0']].values

# Convert the quaternion values to rotation matrices
R_chest = R.from_quat(q_chest)
R_shoulder = R.from_quat(q_shoulder)

# # Calculate the quaternion representing the orientation of the shoulder relative to the chest
R_shoulder_chest = R_chest.inv() * R_shoulder


shoulder_chest_angles = R_shoulder_chest.as_euler('YZY', degrees=True)

# Create a time array with the adjusted size
time = np.arange(len(shoulder_chest_angles))

# Plot the YZY Euler sequence angles for the shoulder relative to the chest
plt.plot(time, shoulder_chest_angles[:, 0], label='Plane of Elevation')
plt.plot(time, shoulder_chest_angles[:, 1], label='Angle of Elevation')
# plt.plot(time, shoulder_chest_angles[:, 2], label='Rotation')
plt.xlabel('Time')
plt.ylabel('Angle (degrees)')
plt.title('YZY Euler Sequence Angles for shoulder angles (humerus Relative to Chest) - MM')
plt.legend()
plt.show()

