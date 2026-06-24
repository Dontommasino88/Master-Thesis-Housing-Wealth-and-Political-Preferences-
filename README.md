Housing Wealth and Political Preferences in the Netherlands (2010–2025)

Overview

This repository contains the replication code for the master thesis "Housing Wealth and Political Preferences in the Netherlands" (Utrecht University, School of Economics, 2026). The study examines the relationship between local housing wealth dynamics and voting behaviour across Dutch neighbourhoods using neighbourhood-level panel data covering six general elections between 2010 and 2025.

Research Question

To what extent do housing wealth gains shape political preferences across neighbourhoods with different levels of homeownership in the Netherlands?

Repository Structure

housing-wealth-voting-netherlands/
├── README.md
├── data_pipeline/
│   ├── CBS_DATA_CLEANING_TEMPLATE_WOZ_plus_controls_2004_2012.do
│   ├── CBS_DATA_CLEANING_TEMPLATE_WOZ_plus_controls_2013_.do
│   ├── MASTER_APPEND_DO-FILE_WOZ_PANEL_2004_2025.do
│   └── pipeline.py
└── regressions/
    └── regressions.py

Data Sources


Election results: Dutch general elections 2010–2025, retrieved from the official Dutch government databases (data.overheid.nl)
Socioeconomic neighbourhood data: CBS Kerncijfers Wijken en Buurten 2004–2025
Neighbourhood shapefiles: CBS wijken en buurten shapefile (wijkenbuurten_2023_v3.gpkg)


Note: Raw data files are not included in this repository due to file size constraints. Election results and CBS neighbourhood data are publicly available via data.overheid.nl and opendata.cbs.nl.

Execution Order


Run CBS_DATA_CLEANING_TEMPLATE_WOZ_plus_controls_2004_2012.do to clean CBS neighbourhood data for 2004–2012
Run CBS_DATA_CLEANING_TEMPLATE_WOZ_plus_controls_2013_.do for each year from 2013 onwards (adjust year placeholder)
Run MASTER_APPEND_DO-FILE_WOZ_PANEL_2004_2025.do to combine all years into one panel dataset
Run pipeline.py to process election results and perform geospatial matching to CBS neighbourhoods
Run regressions.py to reproduce all regression tables (Tables 3–17)


Dependencies

Python:

pandas
geopandas
numpy
pyfixest
statsmodels

Stata: Version 16 or higher

Author

Tom Huijgens | Utrecht University, School of Economics | 2026
