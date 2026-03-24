import pandas as pd
import os

base_dir = "d:/GIT/mesa Gsoc/GSoC-learning-space/models/02_london_commuting_model"

# Load Census 2011 commute mode data
df = pd.read_csv(os.path.join(base_dir, 'data/raw/census2011_commute_mode_msoa.csv'))

# Keep only Total rows
df = df[df['Rural Urban'] == 'Total'].copy()

# Rename columns for convenience
df = df.rename(columns={
    'geography code': 'MSOA11CD',
    'Method of Travel to Work: All categories: Method of travel to work; measures: Value': 'total',
    'Method of Travel to Work: Work mainly at or from home; measures: Value': 'wfh',
    'Method of Travel to Work: Underground, metro, light rail, tram; measures: Value': 'underground',
    'Method of Travel to Work: Train; measures: Value': 'train',
    'Method of Travel to Work: Bus, minibus or coach; measures: Value': 'bus',
    'Method of Travel to Work: Taxi; measures: Value': 'taxi',
    'Method of Travel to Work: Motorcycle, scooter or moped; measures: Value': 'motorcycle',
    'Method of Travel to Work: Driving a car or van; measures: Value': 'car',
    'Method of Travel to Work: Passenger in a car or van; measures: Value': 'car_passenger',
    'Method of Travel to Work: Bicycle; measures: Value': 'bicycle',
    'Method of Travel to Work: On foot; measures: Value': 'walk',
    'Method of Travel to Work: Other method of travel to work; measures: Value': 'other',
    'Method of Travel to Work: Not in employment; measures: Value': 'not_employed',
})

# Filter London MSOAs (E02 codes starting with E020000xx to E020009xx)
london_msoa_codes = pd.read_csv(
    os.path.join(base_dir, 'data/processed/london_OD_travel2work.csv')
)
london_codes = set(london_msoa_codes['MSOA21CD_home']) | set(london_msoa_codes['MSOA21CD_work'])

# Note: 2011 MSOA codes vs 2021 MSOA codes - mostly same for London
df_london = df[df['MSOA11CD'].isin(london_codes)].copy()
print(f"London MSOAs matched: {len(df_london)}")

# Calculate active commuters (exclude WFH and not employed)
df_london['active_commuters'] = (
    df_london['total'] - df_london['wfh'] - df_london['not_employed']
)

# Group into 3 modes
df_london['mode_car'] = df_london['car'] + df_london['car_passenger'] + df_london['motorcycle'] + df_london['taxi']
df_london['mode_pt'] = df_london['underground'] + df_london['train'] + df_london['bus']
df_london['mode_active'] = df_london['bicycle'] + df_london['walk']

# Calculate proportions among active commuters
df_london['prop_car'] = df_london['mode_car'] / df_london['active_commuters']
df_london['prop_pt'] = df_london['mode_pt'] / df_london['active_commuters']
df_london['prop_active'] = df_london['mode_active'] / df_london['active_commuters']

# Keep relevant columns
result = df_london[['MSOA11CD', 'active_commuters', 
                     'prop_car', 'prop_pt', 'prop_active']].copy()

print(f"\nMode share summary (London average):")
print(f"  Car:    {result['prop_car'].mean():.1%}")
print(f"  PT:     {result['prop_pt'].mean():.1%}")
print(f"  Active: {result['prop_active'].mean():.1%}")
print(f"\nSample:")
print(result.head())

# Save
output_path = os.path.join(base_dir, 'data/processed/london_commute_mode_msoa.csv')
result.to_csv(output_path, index=False)
print(f"\nSaved to {output_path}")