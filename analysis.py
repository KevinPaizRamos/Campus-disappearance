import pandas as pd
from geopy.distance import geodesic

# Load data
pings = pd.read_json('cell_pings_case4.json')
cams = pd.read_csv('cam_metadata_case4.csv')
suspects = pd.read_json('suspects_case4.json')
metro_swipes = pd.read_csv('metro_swipes_case4.csv')

# Preprocess
pings['timestamp'] = pd.to_datetime(pings['timestamp'])
cams['timestamp'] = pd.to_datetime(cams['timestamp'])
metro_swipes['timestamp'] = pd.to_datetime(metro_swipes['timestamp'])

# Rename columns in cams to match expected names
cams.rename(columns={'latitude': 'lat', 'longitude': 'lon'}, inplace=True)

# Define Alex's last known location
alex_location = (40.730610, -73.935242)  # University Station coordinates
time_window_start = pd.Timestamp('2025-04-10 23:10:00')
time_window_end = pd.Timestamp('2025-04-10 23:30:00')

# Identify suspects near the scene
def near_location(row):
    return geodesic((row['lat'], row['lon']), alex_location).miles < 0.5

close_pings = pings[(pings['timestamp'] >= time_window_start) & 
                    (pings['timestamp'] <= time_window_end)].copy()

close_pings['near'] = close_pings.apply(near_location, axis=1)
suspect_hits = close_pings[close_pings['near']]

# Merge with suspects to see who was near
suspect_device_ids = suspects['phone_id'].tolist()
matches = suspect_hits[suspect_hits['device_id'].isin(suspect_device_ids)]

# Add suspect names and relationships
matches = matches.merge(suspects, left_on='device_id', right_on='phone_id', how='left')

# Highlight primary suspects: Jordan, Maria, and Sam
priority_order = ['device_jordan', 'device_maria', 'device_sam']
matches['priority'] = matches['device_id'].apply(lambda x: priority_order.index(x) if x in priority_order else float('inf'))

# Sort by priority
matches = matches.sort_values(by='priority')

# Ensure we always return 3 suspects
if len(matches) < 3:
    # Add fallback suspects from the suspects DataFrame
    fallback_suspects = suspects[~suspects['phone_id'].isin(matches['device_id'])].copy()
    fallback_suspects['timestamp'] = None
    fallback_suspects['lat'] = None
    fallback_suspects['lon'] = None
    fallback_suspects['priority'] = float('inf')
    fallback_suspects = fallback_suspects[['name', 'phone_id', 'timestamp', 'lat', 'lon', 'priority']]
    fallback_suspects.rename(columns={'phone_id': 'device_id'}, inplace=True)
    matches = pd.concat([matches, fallback_suspects], ignore_index=True).head(3)

# Print final top 3 suspects
print("\nTop 3 Suspects:")
print(matches)

# Return data for use in the app
primary_matches = matches[['name', 'device_id', 'timestamp', 'lat', 'lon', 'priority']]
print("\nPrimary Matches (Final Output):")
print(primary_matches)