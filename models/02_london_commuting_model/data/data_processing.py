# import pandas as pd
# import geopandas as gpd
# import os

# script_dir = os.path.dirname(os.path.abspath(__file__))

# # --- OD data ---
# raw_path = os.path.join(script_dir, 'raw', 'msoa_OD_travel2work.csv')
# df = pd.read_csv(raw_path)

# london_od = df[
#     (df['county_home'] == 'GREATER_LONDON_AUTHORITY') &
#     (df['county_work'] == 'GREATER_LONDON_AUTHORITY')
# ].copy()

# london_od.to_csv(os.path.join(script_dir, 'processed', 'london_OD_travel2work.csv'), index=False)
# print(f"OD pairs saved: {len(london_od)}")

# # --- Boundary data ---
# gdf = gpd.read_file(os.path.join(script_dir, 'raw', 'msoa_boundaries_2021.geojson'))

# # Get London MSOA codes from OD data
# london_msoa_codes = set(london_od['MSOA21CD_home']) | set(london_od['MSOA21CD_work'])

# # Filter to London MSOAs
# london_gdf = gdf[gdf['MSOA21CD'].isin(london_msoa_codes)].copy()

# london_gdf.to_file(
#     os.path.join(script_dir, 'processed', 'london_msoa_boundaries.geojson'),
#     driver='GeoJSON'
# )
# print(f"London MSOAs saved: {len(london_gdf)}")
# print(f"Columns: {london_gdf.columns.tolist()}")
# print(london_gdf[['MSOA21CD', 'MSOA21NM', 'LAT', 'LONG']].head())

import pandas as pd
import numpy as np
import os
import re

base_dir = "d:/GIT/mesa Gsoc/GSoC-learning-space/models/02_london_commuting_model"
data_dir = os.path.join(base_dir, 'data')

# ── 1. Process BRES ──────────────────────────────────────────────
bres_raw = pd.read_csv(
    os.path.join(data_dir, 'raw', 'bres_msoa_2024.csv'),
    skiprows=8, header=0
)
bres_raw = bres_raw.dropna(axis=1, how='all')
bres_raw = bres_raw.loc[:, ~bres_raw.columns.str.contains('^Unnamed')]

# Extract MSOA code from first column "E02002483 : Hartlepool 001"
bres_raw['MSOA21CD'] = bres_raw['2021 super output area - middle layer'].str.extract(r'(E\d+)')
bres_raw = bres_raw.dropna(subset=['MSOA21CD'])

# Replace * with 0 (suppressed small values)
industry_cols = [c for c in bres_raw.columns if c[0].isdigit()]
for col in industry_cols:
    bres_raw[col] = pd.to_numeric(bres_raw[col], errors='coerce').fillna(0)

# Rename industry columns to short names
col_map = {
    '1 : Agriculture, forestry & fishing (A)': 'agri',
    '2 : Mining, quarrying & utilities (B,D and E)': 'mining',
    '3 : Manufacturing (C)': 'mfg',
    '4 : Construction (F)': 'construction',
    '5 : Motor trades (Part G)': 'motor',
    '6 : Wholesale (Part G)': 'wholesale',
    '7 : Retail (Part G)': 'retail',
    '8 : Transport & storage (inc postal) (H)': 'transport',
    '9 : Accommodation & food services (I)': 'food',
    '10 : Information & communication (J)': 'ict',
    '11 : Financial & insurance (K)': 'finance',
    '12 : Property (L)': 'property',
    '13 : Professional, scientific & technical (M)': 'prof',
    '14 : Business administration & support services (N)': 'admin',
    '15 : Public administration & defence (O)': 'public_admin',
    '16 : Education (P)': 'education',
    '17 : Health (Q)': 'health',
    '18 : Arts, entertainment, recreation & other services (R,S,T and U)': 'arts',
}
bres_raw = bres_raw.rename(columns=col_map)
bres_cols = list(col_map.values())

# Filter London MSOAs
london_od = pd.read_csv(os.path.join(data_dir, 'processed/london_OD_travel2work.csv'))
london_codes = set(london_od['MSOA21CD_home']) | set(london_od['MSOA21CD_work'])
bres_london = bres_raw[bres_raw['MSOA21CD'].isin(london_codes)][['MSOA21CD'] + bres_cols].copy()
bres_london['total_employment'] = bres_london[bres_cols].sum(axis=1)

# 去重：每个MSOA保留employment更大的那行
bres_london = bres_london.sort_values('total_employment', ascending=False)
bres_london = bres_london.drop_duplicates(subset='MSOA21CD', keep='first')
bres_london = bres_london.reset_index(drop=True)

print(f"BRES London MSOAs after dedup: {len(bres_london)}")
print(f"E02000001: {bres_london[bres_london['MSOA21CD']=='E02000001']['total_employment'].values}")

# ── 2. Process TS063 (Occupation) ────────────────────────────────
occ_raw = pd.read_csv(
    os.path.join(data_dir, 'raw', 'census2021_occupation_msoa.csv')
)

occ_raw = occ_raw.rename(columns={
    'geography code': 'MSOA21CD',
    'Occupation (current): Total: All usual residents aged 16 years and over in employment the week before the census': 'total',
    'Occupation (current): 1. Managers, directors and senior officials': 'soc1',
    'Occupation (current): 2. Professional occupations': 'soc2',
    'Occupation (current): 3. Associate professional and technical occupations': 'soc3',
    'Occupation (current): 4. Administrative and secretarial occupations': 'soc4',
    'Occupation (current): 5. Skilled trades occupations': 'soc5',
    'Occupation (current): 6. Caring, leisure and other service occupations': 'soc6',
    'Occupation (current): 7. Sales and customer service occupations': 'soc7',
    'Occupation (current): 8. Process, plant and machine operatives': 'soc8',
    'Occupation (current): 9. Elementary occupations': 'soc9',
})

occ_cols = ['soc1','soc2','soc3','soc4','soc5','soc6','soc7','soc8','soc9']
occ_london = occ_raw[occ_raw['MSOA21CD'].isin(london_codes)][['MSOA21CD', 'total'] + occ_cols].copy()

# Calculate proportions
for col in occ_cols:
    occ_london[f'prop_{col}'] = occ_london[col] / occ_london['total'].replace(0, np.nan)

occ_london = occ_london.fillna(0)
print(f"\nTS063 London MSOAs: {len(occ_london)}")
print(f"Sample:\n{occ_london[['MSOA21CD'] + [f'prop_{c}' for c in occ_cols]].head()}")

# ── 3. Define SOC → Industry affinity weights ────────────────────
# Each SOC maps to preferred industries (higher weight = stronger preference)
soc_industry_affinity = {
    'soc1': {'finance': 3, 'prof': 3, 'public_admin': 2, 'ict': 2, 'property': 1},
    'soc2': {'ict': 3, 'finance': 2, 'education': 3, 'health': 2, 'prof': 2},
    'soc3': {'ict': 3, 'prof': 2, 'mfg': 1, 'admin': 2, 'finance': 1},
    'soc4': {'public_admin': 3, 'finance': 2, 'admin': 3, 'retail': 1, 'education': 1},
    'soc5': {'mfg': 3, 'construction': 3, 'transport': 2, 'motor': 2, 'wholesale': 1},
    'soc6': {'health': 3, 'food': 2, 'arts': 2, 'education': 1, 'retail': 1},
    'soc7': {'retail': 3, 'food': 2, 'arts': 1, 'admin': 1, 'wholesale': 1},
    'soc8': {'mfg': 3, 'transport': 3, 'mining': 2, 'construction': 1, 'wholesale': 1},
    'soc9': {'construction': 2, 'transport': 2, 'food': 2, 'retail': 2, 'agri': 1},
}

# ── 4. Compute work destination weights per home MSOA per SOC ────
# For each home MSOA and each SOC, compute attraction score for each work MSOA
# attraction(home_i, work_j, soc_k) = Σ_industry [affinity(soc_k, industry) * employment(work_j, industry)]

# Build work MSOA industry matrix
work_industry = bres_london.set_index('MSOA21CD')[bres_cols]

# For each SOC, compute industry-weighted employment attraction per work MSOA
soc_work_attraction = {}
for soc, affinities in soc_industry_affinity.items():
    weights = pd.Series({ind: affinities.get(ind, 0.1) for ind in bres_cols})
    # weighted sum across industries
    attraction = work_industry.mul(weights, axis=1).sum(axis=1)
    # normalize to sum=1 for use as probability weights
    total = attraction.sum()
    if total > 0:
        attraction = attraction / total
    soc_work_attraction[soc] = attraction.to_dict()

print(f"\nSOC work attraction computed for {len(soc_work_attraction)} SOC groups")
print("Sample SOC1 top 5 work MSOAs:")
soc1_series = pd.Series(soc_work_attraction['soc1']).sort_values(ascending=False)
print(soc1_series.head())

# ── 5. Save outputs ──────────────────────────────────────────────
# Save occupation proportions
occ_out = occ_london[['MSOA21CD'] + [f'prop_{c}' for c in occ_cols]]
occ_out.to_csv(os.path.join(data_dir, 'processed/london_occupation_msoa.csv'), index=False)
print(f"\nSaved occupation data: {len(occ_out)} MSOAs")

# Save BRES employment by industry
bres_london.to_csv(os.path.join(data_dir, 'processed/london_bres_msoa.csv'), index=False)
print(f"Saved BRES data: {len(bres_london)} MSOAs")

# Save SOC work attraction weights
import json
with open(os.path.join(data_dir, 'processed/soc_work_attraction.json'), 'w') as f:
    json.dump(soc_work_attraction, f)
print("Saved SOC work attraction weights")

