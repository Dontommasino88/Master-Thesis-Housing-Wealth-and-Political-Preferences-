# =========================================================
# MASTER THESIS PIPELINE
# HOUSING WEALTH & VOTING BEHAVIOUR IN THE NETHERLANDS
# Tom Huijgens | Utrecht University | 2026
#
# This script processes Dutch general election results
# (2010-2025) and merges them with CBS neighbourhood-level
# socioeconomic data (WOZ values + controls) to produce
# the master panel dataset used in the regression analysis.
#
# Steps:
# 1. Load and clean election results per year
# 2. Geolocate polling stations
# 3. Spatial join: polling stations -> CBS neighbourhoods
# 4. Construct vote shares per neighbourhood-year
# 5. Merge with WOZ + controls from Stata
# 6. Construct housing wealth variables (log_woz, CAGR)
# 7. Save master panel dataset
# =========================================================

# =========================================================
# 0. IMPORTS
# =========================================================

import os
import pandas as pd
import geopandas as gpd
import numpy as np

# =========================================================
# 1. COORDINATE CLEANING FUNCTIONS
#
# Polling station coordinates sometimes contain formatting
# errors. These functions extract valid lat/lon values
# within Dutch geographic boundaries.
# =========================================================

def fix_lat(x):
    """Extract valid latitude (50-54 degrees N = Netherlands)."""
    try:
        digits = ''.join(filter(str.isdigit, str(x)))
        if len(digits) < 6:
            return np.nan
        val = float(digits[:2] + '.' + digits[2:8])
        if 50 <= val <= 54:
            return val
        return np.nan
    except:
        return np.nan


def fix_lon(x):
    """Extract valid longitude (3-7 degrees E = Netherlands)."""
    try:
        digits = ''.join(filter(str.isdigit, str(x)))
        if len(digits) < 5:
            return np.nan
        val = float(digits[0] + '.' + digits[1:7])
        if 3 <= val <= 7:
            return val
        return np.nan
    except:
        return np.nan

# =========================================================
# 2. ELECTION PIPELINE FUNCTION
#
# For each election year:
# - Load vote results and polling station locations
# - Construct unique polling station identifier
# - Clean coordinates
# - Spatial join to CBS neighbourhood polygons
# - Assign BU_CODE to each polling station
# =========================================================

def run_pipeline(election_year, votes_file, loc_file, buurten_file):

    print(f"\n STARTING PIPELINE {election_year}")

    # Load election results
    df_votes = pd.read_csv(votes_file, sep=";", encoding="latin1")

    # Load polling station locations
    df_loc = pd.read_csv(
        loc_file, sep=None, engine="python",
        encoding="latin1", on_bad_lines="skip"
    )
    df_loc.columns = df_loc.columns.str.strip()

    print(f"  Votes shape:    {df_votes.shape}")
    print(f"  Location shape: {df_loc.shape}")

    # Extract polling station numbers
    df_votes['sb_nummer'] = (
        df_votes['StembureauCode'].astype(str).str.extract(r'(\d+)')[0]
    )
    df_loc['Nummer stembureau'] = (
        df_loc['Nummer stembureau'].astype(str).str.extract(r'(\d+)')[0]
    )

    # Construct unique polling station identifier: municipality_number
    df_votes['sb_unique'] = (
        df_votes['GemeenteNaam'].astype(str).str.strip().str.lower()
        + "_" + df_votes['sb_nummer']
    )
    df_loc['sb_unique'] = (
        df_loc['Gemeente'].astype(str).str.strip().str.lower()
        + "_" + df_loc['Nummer stembureau']
    )

    # Clean coordinates
    df_loc['Latitude']  = df_loc['Latitude'].apply(fix_lat)
    df_loc['Longitude'] = df_loc['Longitude'].apply(fix_lon)

    # Merge coordinates onto vote results
    df_merged = df_votes.merge(
        df_loc[['sb_unique', 'Latitude', 'Longitude']],
        on='sb_unique', how='left'
    )

    # Fill missing coordinates using first observed coordinate per station
    coord_fill = (
        df_merged.groupby('sb_unique')[['Latitude', 'Longitude']]
        .first().reset_index()
    )
    df_merged = df_merged.drop(columns=['Latitude', 'Longitude'])
    df_merged = df_merged.merge(coord_fill, on='sb_unique', how='left')

    # Create GeoDataFrame of unique polling station points
    df_points_unique = (
        df_merged[['sb_unique', 'Latitude', 'Longitude']]
        .dropna().drop_duplicates()
    )

    gdf_points = gpd.GeoDataFrame(
        df_points_unique,
        geometry=gpd.points_from_xy(
            df_points_unique['Longitude'],
            df_points_unique['Latitude']
        ),
        crs="EPSG:4326"
    )
    gdf_points = gdf_points.to_crs(28992)  # Convert to Dutch RD New projection

    # Load CBS neighbourhood polygons
    gdf_buurten = gpd.read_file(buurten_file, layer="buurten")
    gdf_buurten = (
        gdf_buurten
        .rename(columns={'buurtcode': 'BU_CODE'})
        [['BU_CODE', 'geometry']]
    )
    gdf_buurten = gdf_buurten.to_crs(28992)

    # Spatial join: point-in-polygon
    gdf_joined = gpd.sjoin(
        gdf_points, gdf_buurten, how="left", predicate="within"
    )
    gdf_joined = gdf_joined.drop_duplicates(subset='sb_unique')

    # Merge BU_CODE back to election results
    sb_to_bu = gdf_joined[['sb_unique', 'BU_CODE']]
    df_final = df_merged.merge(sb_to_bu, on='sb_unique', how='left')

    # Drop observations without matched neighbourhood
    n_before = len(df_final)
    df_final = df_final.dropna(subset=['BU_CODE'])
    n_after  = len(df_final)
    print(f"  Dropped {n_before - n_after} rows without BU_CODE match")
    print(f"  Match rate: {n_after / n_before * 100:.1f}%")

    df_final['year'] = election_year

    # Save
    output_name = f"dataset_{election_year}_clean"
    df_final.to_parquet(output_name + ".parquet")
    df_final.to_csv(output_name + ".csv", index=False)

    print(f"  {election_year} COMPLETE")
    return df_final

# =========================================================
# 3. RUN PIPELINE FOR ALL ELECTION YEARS
# =========================================================

df_2010 = run_pipeline(
    2010,
    r"Data Verkiezingsuitslag Tweede Kamer\2010\TK2010_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2010\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2010\wijkenbuurten_2023_v3.gpkg"
)

df_2012 = run_pipeline(
    2012,
    r"Data Verkiezingsuitslag Tweede Kamer\2012\TK2012_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2012\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2012\wijkenbuurten_2023_v3.gpkg"
)

df_2017 = run_pipeline(
    2017,
    r"Data Verkiezingsuitslag Tweede Kamer\2017\TK2017_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2017\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2017\wijkenbuurten_2023_v3.gpkg"
)

df_2021 = run_pipeline(
    2021,
    r"Data Verkiezingsuitslag Tweede Kamer\2021\TK2021_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2021\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2021\wijkenbuurten_2023_v3.gpkg"
)

df_2023 = run_pipeline(
    2023,
    r"Data Verkiezingsuitslag Tweede Kamer\2023\TK2023_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2023\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2023\wijkenbuurten_2023_v3.gpkg"
)

df_2025 = run_pipeline(
    2025,
    r"Data Verkiezingsuitslag Tweede Kamer\2025\TK2025_Stemmen_Per_Lijst_Per_Stembureau.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2025\Stembureau info.csv",
    r"Data Verkiezingsuitslag Tweede Kamer\2025\wijkenbuurten_2023_v3.gpkg"
)

# =========================================================
# 4. COMBINE ALL ELECTIONS
# =========================================================

df_panel = pd.concat([df_2010, df_2012, df_2017, df_2021, df_2023, df_2025])

df_panel.to_parquet("master_election_panel.parquet")
df_panel.to_csv("master_election_panel.csv", index=False)

print("\n MASTER ELECTION PANEL SAVED")

# =========================================================
# 5. MERGE WITH WOZ + CONTROLS (from Stata)
# =========================================================

df_controls = pd.read_stata("woz_controls_final_v1.dta")

df_panel['BU_CODE']       = df_panel['BU_CODE'].astype(str)
df_controls['bu_code']    = df_controls['bu_code'].astype(str)

df_merged = df_panel.merge(
    df_controls,
    left_on=['BU_CODE', 'year'],
    right_on=['bu_code', 'year'],
    how='left',
    indicator=True
)

print(f"\nMerge result:")
print(df_merged['_merge'].value_counts())

# =========================================================
# 6. CONSTRUCT HOUSING WEALTH VARIABLES
#
# log_woz:
#   Logarithm of average WOZ value per neighbourhood.
#   Captures housing wealth growth (first derivative).
#   A 1% increase in WOZ level = 1 unit increase in log_woz.
#
# woz_growth:
#   Raw percentage change in WOZ values between elections.
#   Used as robustness check (Table 14).
#
# woz_growth_annual (CAGR):
#   Compound Annual Growth Rate of WOZ values.
#   Corrects for unequal periods between elections
#   (e.g. 2 years between 2010-2012, 5 years between 2012-2017).
#   Captures the rate of housing wealth appreciation
#   (second derivative). Used in main specification.
# =========================================================

df_merged = df_merged.sort_values(['BU_CODE', 'year'])

# Log WOZ
df_merged['log_woz'] = np.log(df_merged['woz'])

# Raw growth (pct change)
df_merged['woz_growth'] = (
    df_merged.groupby('BU_CODE')['woz']
    .pct_change(fill_method=None)
)

# Years between elections (for CAGR denominator)
df_merged['years_since_prev'] = (
    df_merged.groupby('BU_CODE')['year'].diff()
)

# CAGR: compound annual growth rate
df_merged['woz_growth_annual'] = (
    (df_merged['woz'] / df_merged.groupby('BU_CODE')['woz'].shift(1))
    ** (1 / df_merged['years_since_prev'])
    - 1
)

print("\nHousing wealth variables:")
print(df_merged[['log_woz', 'woz_growth', 'woz_growth_annual']].describe())

# =========================================================
# 7. SAVE MASTER PANEL DATASET
# =========================================================

df_merged.to_parquet("master_panel_buurt_v4.parquet")
df_merged.to_csv("master_panel_buurt_v4.csv", index=False)

print("\n FINAL MASTER DATASET SAVED: master_panel_buurt_v4.parquet")

# =========================================================
# 8. SANITY CHECKS
# =========================================================

print("\n===================================")
print("SANITY CHECKS")
print("===================================\n")

print(f"Dataset shape:       {df_merged.shape}")
print(f"\nObservations per year:")
print(df_merged['year'].value_counts().sort_index())
print(f"\nUnique neighbourhoods: {df_merged['BU_CODE'].nunique()}")
print(f"Unique polling stations: {df_merged['sb_unique'].nunique()}")

print(f"\nMissing WOZ (%):         {df_merged['woz'].isna().mean() * 100:.2f}%")
print(f"Missing BU_CODE (%):     {df_merged['BU_CODE'].isna().mean() * 100:.2f}%")
print(f"Missing CAGR (%):        {df_merged['woz_growth_annual'].isna().mean() * 100:.2f}%")

print("\nWOZ missings per year:")
print(df_merged.groupby('year')['woz'].apply(lambda x: x.isna().mean()).round(3))

print("\nRandom sample:")
print(df_merged[['BU_CODE', 'year', 'woz', 'log_woz', 'woz_growth_annual']].sample(5))

print("\n===================================")
print("PIPELINE COMPLETE")
print("===================================")
