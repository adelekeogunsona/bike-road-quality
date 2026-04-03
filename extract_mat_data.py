"""
Extracts sensor data from the MATLAB .mat file and saves as CSV.

The .mat file uses MATLAB timetable objects which scipy can't read directly,
so we dig into the __function_workspace__ binary blob and pull out the 
float64 arrays by scanning for the miDOUBLE data type tag.

Only needs to be run once - after this just use the CSVs.
"""
import scipy.io
import numpy as np
import pandas as pd
import struct
import os

MAT_FILE = 'sensorlog_20260329_142428.mat'
OUTPUT_DIR = 'data/sample'


def find_double_arrays(workspace_bytes):
    """Find all float64 arrays in the workspace binary."""
    arrays = []
    pos = 0
    ws = workspace_bytes
    
    while pos < len(ws) - 16:
        tag_type = struct.unpack_from('<I', ws, pos)[0]
        tag_size = struct.unpack_from('<I', ws, pos + 4)[0]
        
        # miDOUBLE = 9 in MAT5 format
        if tag_type == 9 and 16 < tag_size < 5000000:
            n_doubles = tag_size // 8
            if n_doubles > 10:
                arr = np.frombuffer(ws, dtype=np.float64, count=n_doubles, offset=pos+8)
                arrays.append(arr.copy())
        pos += 1
    
    return arrays


def main():
    print(f"Loading {MAT_FILE}...")
    data = scipy.io.loadmat(MAT_FILE, squeeze_me=True)
    workspace = data['__function_workspace__'].flatten().tobytes()
    
    print("Scanning binary for numeric arrays...")
    arrays = find_double_arrays(workspace)
    print(f"Found {len(arrays)} arrays")
    
    # array layout (figured out by inspecting the values):
    # [0-3]   Acceleration: timestamp, x, y, z  (98591 samples, ~54Hz)
    # [4-7]   MagneticField: timestamp, x, y, z  (18255 samples, ~10Hz)
    # [8-11]  Orientation: timestamp, azimuth, pitch, roll  (18466 samples)
    # [12-15] AngularVelocity: timestamp, x, y, z  (18466 samples)
    # [16-22] Position: timestamp, lat, lon, alt, speed, course, accuracy  (1717 samples, ~1Hz)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # acceleration
    ts = arrays[0]
    pd.DataFrame({
        'timestamp': pd.to_datetime(ts, unit='ms'),
        'ax': arrays[1], 'ay': arrays[2], 'az': arrays[3]
    }).to_csv(f'{OUTPUT_DIR}/acceleration.csv', index=False)
    print(f"  acceleration: {len(arrays[1])} samples")
    
    # magnetic field
    ts = arrays[4]
    pd.DataFrame({
        'timestamp': pd.to_datetime(ts, unit='ms'),
        'mx': arrays[5], 'my': arrays[6], 'mz': arrays[7]
    }).to_csv(f'{OUTPUT_DIR}/magnetic_field.csv', index=False)
    print(f"  magnetic_field: {len(arrays[5])} samples")
    
    # orientation
    ts = arrays[8]
    pd.DataFrame({
        'timestamp': pd.to_datetime(ts, unit='ms'),
        'azimuth': arrays[9], 'pitch': arrays[10], 'roll': arrays[11]
    }).to_csv(f'{OUTPUT_DIR}/orientation.csv', index=False)
    print(f"  orientation: {len(arrays[9])} samples")
    
    # angular velocity
    ts = arrays[12]
    pd.DataFrame({
        'timestamp': pd.to_datetime(ts, unit='ms'),
        'wx': arrays[13], 'wy': arrays[14], 'wz': arrays[15]
    }).to_csv(f'{OUTPUT_DIR}/angular_velocity.csv', index=False)
    print(f"  angular_velocity: {len(arrays[13])} samples")
    
    # position
    ts = arrays[16]
    pos_df = pd.DataFrame({
        'timestamp': pd.to_datetime(ts, unit='ms'),
        'latitude': arrays[17], 'longitude': arrays[18],
        'altitude': arrays[19], 'speed': arrays[20],
        'course': arrays[21], 'horizontal_accuracy': arrays[22]
    })
    pos_df.to_csv(f'{OUTPUT_DIR}/position.csv', index=False)
    print(f"  position: {len(pos_df)} samples")
    
    print(f"\nSaved to {OUTPUT_DIR}/")
    print(f"Lat: {pos_df['latitude'].min():.4f} - {pos_df['latitude'].max():.4f}")
    print(f"Lon: {pos_df['longitude'].min():.4f} - {pos_df['longitude'].max():.4f}")


if __name__ == '__main__':
    main()
