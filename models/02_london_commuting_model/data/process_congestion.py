import pandas as pd
import geopandas as gpd
import re
import os

base_dir = "d:/GIT/mesa Gsoc/GSoC-learning-space/models/02_london_commuting_model"

gdf = gpd.read_file(os.path.join(base_dir, 'data/processed/london_msoa_boundaries.geojson'))
congestion = pd.read_csv(os.path.join(base_dir, 'data/processed/tomtom_hourly_congestion.csv'))

# Extract borough from MSOA name
gdf['borough_name'] = gdf['MSOA21NM'].apply(
    lambda x: re.sub(r'\s+\d+$', '', x).strip()
)

# Pivot congestion to wide format: borough x hour
congestion_wide = congestion.pivot(
    index='borough', columns='hour', values='congestion_ratio'
)
congestion_wide.columns = [f'hour_{h}' for h in congestion_wide.columns]
congestion_wide = congestion_wide.reset_index()

# Merge MSOA with congestion
msoa_congestion = gdf[['MSOA21CD', 'MSOA21NM', 'borough_name']].merge(
    congestion_wide, left_on='borough_name', right_on='borough', how='left'
)

# Fill missing boroughs (outer London) with default low congestion
# Use average of outer London estimate: ~1.2 (much less than inner London ~1.6-1.9)
hour_cols = [f'hour_{h}' for h in range(24)]
for col in hour_cols:
    msoa_congestion[col] = msoa_congestion[col].fillna(1.2)

print(f"Total MSOAs: {len(msoa_congestion)}")
print(f"MSOAs with TomTom data: {msoa_congestion['borough'].notna().sum()}")
print(f"MSOAs using default: {msoa_congestion['borough'].isna().sum()}")
print("\nSample (Westminster MSOA):")
sample = msoa_congestion[msoa_congestion['borough_name'] == 'Westminster'].iloc[0]
print(sample[['MSOA21CD', 'MSOA21NM', 'hour_8', 'hour_12', 'hour_17']])

# Save
output_path = os.path.join(base_dir, 'data/processed/msoa_hourly_congestion.csv')
msoa_congestion[['MSOA21CD', 'MSOA21NM', 'borough_name'] + hour_cols].to_csv(
    output_path, index=False
)
print(f"\nSaved to {output_path}")