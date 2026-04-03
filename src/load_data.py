import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample')


def load_position():
    return pd.read_csv(os.path.join(DATA_DIR, 'position.csv'), parse_dates=['timestamp'])

def load_acceleration():
    return pd.read_csv(os.path.join(DATA_DIR, 'acceleration.csv'), parse_dates=['timestamp'])

def load_magnetic_field():
    return pd.read_csv(os.path.join(DATA_DIR, 'magnetic_field.csv'), parse_dates=['timestamp'])

def load_orientation():
    return pd.read_csv(os.path.join(DATA_DIR, 'orientation.csv'), parse_dates=['timestamp'])

def load_angular_velocity():
    return pd.read_csv(os.path.join(DATA_DIR, 'angular_velocity.csv'), parse_dates=['timestamp'])


def load_all():
    return {
        'position': load_position(),
        'acceleration': load_acceleration(),
        'magnetic_field': load_magnetic_field(),
        'orientation': load_orientation(),
        'angular_velocity': load_angular_velocity()
    }


def print_summary(data):
    print("=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)
    
    for name, df in data.items():
        duration = (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]).total_seconds()
        rate = len(df) / duration if duration > 0 else 0
        print(f"\n{name}:")
        print(f"  Samples: {len(df)}")
        print(f"  Duration: {duration:.1f} sec ({duration/60:.1f} min)")
        print(f"  ~{rate:.1f} Hz")
    
    pos = data['position']
    print(f"\nRoute bounds:")
    print(f"  Lat: {pos['latitude'].min():.4f} to {pos['latitude'].max():.4f}")
    print(f"  Lon: {pos['longitude'].min():.4f} to {pos['longitude'].max():.4f}")
