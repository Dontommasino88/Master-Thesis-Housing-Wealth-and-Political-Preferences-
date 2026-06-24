# =========================================================
# MASTER THESIS
# HOUSING WEALTH & VOTING BEHAVIOUR IN THE NETHERLANDS
# Tom Huijgens | Utrecht University | 2026
#
# This script contains all regression analyses:
# - Baseline OLS
# - Fixed Effects models
# - Homeownership interaction
# - Homeownership sample split
# - Robustness checks (income, municipality FE,
#   municipality clustering, post-2015, urban split)
# - Granger causality tests
# =========================================================

import pandas as pd
import numpy as np
import pyfixest as pf
import os

# =========================================================
# 0. SETUP
# =========================================================

os.makedirs("Results/Tables", exist_ok=True)

# =========================================================
# 1. LOAD DATA
# =========================================================

path = r"master_panel_buurt_v4.parquet"

df = pd.read_parquet(path)

print(f"Dataset shape: {df.shape}")
print(df[["woz_growth_annual", "woz_growth", "log_woz"]].describe())

# =========================================================
# 2. TABLE EXPORT FUNCTION
# =========================================================

def save_table(models, filename, heads):
    html = pf.etable(
        models,
        type="html",
        model_heads=heads,
        signif_code=[0.01, 0.05, 0.10],
        coef_fmt="b:.3f* \n (se:.3f)"
    )
    with open(
        f"Results/Tables/{filename}.html",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)
    print(f"Saved: {filename}.html")

# =========================================================
# 3. DESCRIPTIVE STATISTICS (Table 1)
# =========================================================

vars_desc = [
    "right_share", "populist_share", "left_share",
    "log_woz", "woz_growth_annual",
    "share_owner", "share_65plus", "share_non_west",
    "urban_density", "population", "household_size"
]

desc = df[vars_desc].describe().T
desc.to_html("Results/Tables/Table_1_Descriptive_Statistics.html")
print(desc)

# =========================================================
# 4. CORRELATION MATRIX (Table 2)
# =========================================================

corr = df[vars_desc].corr()
corr.to_html("Results/Tables/Table_2_Correlation_Matrix.html")

# =========================================================
# 5. BASELINE OLS — NO CONTROLS (Table 6)
# =========================================================

m1 = pf.feols("right_share ~ log_woz", data=df)
m2 = pf.feols("populist_share ~ log_woz", data=df)
m3 = pf.feols("left_share ~ log_woz", data=df)

save_table([m1, m2, m3], "Table_6_Baseline_OLS", ["Right", "Populist", "Left"])

# =========================================================
# 6. OLS WITH CONTROLS (Table 7)
# =========================================================

formula_controls = """
log_woz +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(f"right_share ~ {formula_controls}", data=df)
m2 = pf.feols(f"populist_share ~ {formula_controls}", data=df)
m3 = pf.feols(f"left_share ~ {formula_controls}", data=df)

save_table([m1, m2, m3], "Table_7_OLS_Controls", ["Right", "Populist", "Left"])

# =========================================================
# 7. FE: HOUSING WEALTH LEVELS ONLY (Table 8)
# =========================================================

m1 = pf.feols(
    f"right_share ~ {formula_controls} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m2 = pf.feols(
    f"populist_share ~ {formula_controls} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m3 = pf.feols(
    f"left_share ~ {formula_controls} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)

save_table([m1, m2, m3], "Table_8_FE_Levels", ["Right", "Populist", "Left"])

# =========================================================
# 8. FE: RATE OF APPRECIATION ONLY (Table 9)
# =========================================================

formula_growth = """
woz_growth_annual +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(
    f"right_share ~ {formula_growth} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m2 = pf.feols(
    f"populist_share ~ {formula_growth} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m3 = pf.feols(
    f"left_share ~ {formula_growth} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)

save_table([m1, m2, m3], "Table_9_FE_Growth", ["Right", "Populist", "Left"])

# =========================================================
# 9. MAIN SPECIFICATION — STANDARDISED (Table 3)
# FE: LEVELS + GROWTH (STANDARDISED)
# =========================================================

# Standardise variables
for var in ["log_woz", "woz_growth_annual",
            "right_share", "populist_share", "left_share"]:
    df[f"{var}_std"] = (df[var] - df[var].mean()) / df[var].std()

formula_main = """
log_woz_std +
woz_growth_annual_std +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(
    f"right_share_std ~ {formula_main} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m2 = pf.feols(
    f"populist_share_std ~ {formula_main} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m3 = pf.feols(
    f"left_share_std ~ {formula_main} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)

save_table([m1, m2, m3], "Table_3_Main_FE_Standardised", ["Right", "Populist", "Left"])

# =========================================================
# 10. HOMEOWNERSHIP INTERACTION MODEL (Table 4)
# =========================================================

formula_interaction = """
log_woz_std +
woz_growth_annual_std +
share_owner +
log_woz_std:share_owner +
woz_growth_annual_std:share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(
    f"right_share_std ~ {formula_interaction} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m2 = pf.feols(
    f"populist_share_std ~ {formula_interaction} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)
m3 = pf.feols(
    f"left_share_std ~ {formula_interaction} | BU_CODE + year",
    data=df, vcov={"CRV1": "BU_CODE"}
)

save_table([m1, m2, m3], "Table_4_Homeownership_Interaction", ["Right", "Populist", "Left"])

# =========================================================
# 11. HOMEOWNERSHIP SAMPLE SPLIT (Table 5)
# =========================================================

median_ho = df["share_owner"].median()
print(f"Median homeownership: {median_ho:.3f}")

df_high = df[df["share_owner"] >= median_ho].copy()
df_low  = df[df["share_owner"] <  median_ho].copy()

formula_split = """
log_woz_std +
woz_growth_annual_std +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

# Right
mh1 = pf.feols(f"right_share_std ~ {formula_split} | BU_CODE + year", data=df_high, vcov={"CRV1": "BU_CODE"})
ml1 = pf.feols(f"right_share_std ~ {formula_split} | BU_CODE + year", data=df_low,  vcov={"CRV1": "BU_CODE"})

# Populist
mh2 = pf.feols(f"populist_share_std ~ {formula_split} | BU_CODE + year", data=df_high, vcov={"CRV1": "BU_CODE"})
ml2 = pf.feols(f"populist_share_std ~ {formula_split} | BU_CODE + year", data=df_low,  vcov={"CRV1": "BU_CODE"})

# Left
mh3 = pf.feols(f"left_share_std ~ {formula_split} | BU_CODE + year", data=df_high, vcov={"CRV1": "BU_CODE"})
ml3 = pf.feols(f"left_share_std ~ {formula_split} | BU_CODE + year", data=df_low,  vcov={"CRV1": "BU_CODE"})

save_table(
    [mh1, ml1, mh2, ml2, mh3, ml3],
    "Table_5_Homeownership_Sample_Split",
    ["Right High", "Right Low", "Populist High", "Populist Low", "Left High", "Left Low"]
)

# =========================================================
# 12. ROBUSTNESS: INCOME CONTROL (Table 10)
# =========================================================

formula_income = """
log_woz_std +
woz_growth_annual_std +
income_pc +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(f"right_share_std ~ {formula_income} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m2 = pf.feols(f"populist_share_std ~ {formula_income} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m3 = pf.feols(f"left_share_std ~ {formula_income} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})

save_table([m1, m2, m3], "Table_10_Income_Control", ["Right", "Populist", "Left"])

# =========================================================
# 13. ROBUSTNESS: MUNICIPALITY FIXED EFFECTS (Table 11)
# =========================================================

m1 = pf.feols(f"right_share_std ~ {formula_main} | municipality + year", data=df, vcov={"CRV1": "BU_CODE"})
m2 = pf.feols(f"populist_share_std ~ {formula_main} | municipality + year", data=df, vcov={"CRV1": "BU_CODE"})
m3 = pf.feols(f"left_share_std ~ {formula_main} | municipality + year", data=df, vcov={"CRV1": "BU_CODE"})

save_table([m1, m2, m3], "Table_11_Municipality_FE", ["Right", "Populist", "Left"])

# =========================================================
# 14. ROBUSTNESS: MUNICIPALITY CLUSTERING (Table 12)
# =========================================================

m1 = pf.feols(f"right_share_std ~ {formula_main} | BU_CODE + year", data=df, vcov={"CRV1": "municipality"})
m2 = pf.feols(f"populist_share_std ~ {formula_main} | BU_CODE + year", data=df, vcov={"CRV1": "municipality"})
m3 = pf.feols(f"left_share_std ~ {formula_main} | BU_CODE + year", data=df, vcov={"CRV1": "municipality"})

save_table([m1, m2, m3], "Table_12_Municipality_Clustering", ["Right", "Populist", "Left"])

# =========================================================
# 15. ROBUSTNESS: POST-2015 SAMPLE (Table 13)
# =========================================================

df_post = df[df["year"] >= 2017].copy()

m1 = pf.feols(f"right_share_std ~ {formula_main} | BU_CODE + year", data=df_post, vcov={"CRV1": "BU_CODE"})
m2 = pf.feols(f"populist_share_std ~ {formula_main} | BU_CODE + year", data=df_post, vcov={"CRV1": "BU_CODE"})
m3 = pf.feols(f"left_share_std ~ {formula_main} | BU_CODE + year", data=df_post, vcov={"CRV1": "BU_CODE"})

save_table([m1, m2, m3], "Table_13_Post2015", ["Right", "Populist", "Left"])

# =========================================================
# 16. ROBUSTNESS: RAW GROWTH MEASURE (Table 14)
# =========================================================

formula_raw = """
log_woz_std +
woz_growth +
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

m1 = pf.feols(f"right_share_std ~ {formula_raw} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m2 = pf.feols(f"populist_share_std ~ {formula_raw} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m3 = pf.feols(f"left_share_std ~ {formula_raw} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})

save_table([m1, m2, m3], "Table_14_Raw_Growth", ["Right", "Populist", "Left"])

# =========================================================
# 17. ROBUSTNESS: URBAN-RURAL SPLIT (Table 15)
# =========================================================

q75 = df["urban_density"].quantile(0.75)
df_urban = df[df["urban_density"] >= q75].copy()
df_rural = df[df["urban_density"] <  q75].copy()

formula_split_urban = """
log_woz_std +
woz_growth_annual_std +
share_owner +
share_65plus +
share_non_west +
population +
household_size
"""

urban_right   = pf.feols(f"right_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_urban, vcov={"CRV1": "BU_CODE"})
rural_right   = pf.feols(f"right_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_rural, vcov={"CRV1": "BU_CODE"})
urban_pop     = pf.feols(f"populist_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_urban, vcov={"CRV1": "BU_CODE"})
rural_pop     = pf.feols(f"populist_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_rural, vcov={"CRV1": "BU_CODE"})
urban_left    = pf.feols(f"left_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_urban, vcov={"CRV1": "BU_CODE"})
rural_left    = pf.feols(f"left_share_std ~ {formula_split_urban} | BU_CODE + year", data=df_rural, vcov={"CRV1": "BU_CODE"})

save_table(
    [urban_right, rural_right, urban_pop, rural_pop, urban_left, rural_left],
    "Table_15_Urban_Rural_Split",
    ["Right Urban", "Right Rural", "Populist Urban", "Populist Rural", "Left Urban", "Left Rural"]
)

# =========================================================
# 18. GRANGER CAUSALITY TESTS (Tables 16 & 17)
# =========================================================

df = df.sort_values(["BU_CODE", "year"])

df["right_share_lag"]    = df.groupby("BU_CODE")["right_share"].shift(1)
df["populist_share_lag"] = df.groupby("BU_CODE")["populist_share"].shift(1)
df["left_share_lag"]     = df.groupby("BU_CODE")["left_share"].shift(1)

controls = """
share_owner +
share_65plus +
share_non_west +
urban_density +
population +
household_size
"""

# Direction 1: WOZ growth → voting behaviour (Table 16)
m_right_gr  = pf.feols(f"right_share ~ right_share_lag + woz_growth_annual + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m_pop_gr    = pf.feols(f"populist_share ~ populist_share_lag + woz_growth_annual + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m_left_gr   = pf.feols(f"left_share ~ left_share_lag + woz_growth_annual + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})

save_table(
    [m_right_gr, m_pop_gr, m_left_gr],
    "Table_16_Granger_WOZ_to_Vote",
    ["Right", "Populist", "Left"]
)

# Direction 2: voting behaviour → WOZ growth (Table 17)
m_woz_right = pf.feols(f"woz_growth_annual ~ right_share_lag + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m_woz_pop   = pf.feols(f"woz_growth_annual ~ populist_share_lag + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})
m_woz_left  = pf.feols(f"woz_growth_annual ~ left_share_lag + {controls} | BU_CODE + year", data=df, vcov={"CRV1": "BU_CODE"})

save_table(
    [m_woz_right, m_woz_pop, m_woz_left],
    "Table_17_Granger_Vote_to_WOZ",
    ["Right → WOZ", "Populist → WOZ", "Left → WOZ"]
)

print("\n✅ ALL TABLES SAVED TO Results/Tables/")
