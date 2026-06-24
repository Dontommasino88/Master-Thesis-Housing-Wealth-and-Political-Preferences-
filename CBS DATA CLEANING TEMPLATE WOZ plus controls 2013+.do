* ==============================
* CBS DATA CLEANING TEMPLATE
* WOZ + CONTROLS 2013+
* Tom Huijgens | Utrecht University | 2026
*
* NOTE: This template is applied separately for each
* year from 2013 onwards. Adjust the directory, filename
* and year placeholder (20xx) for each year.
* ==============================

* 1. Set directory
cd "C:/Users/2214946/OneDrive - Universiteit Utrecht/Master Thesis/Data/WOZ Waarde/20xx"

* 2. Import CSV
import delimited "cbs_woz_controls_20xx_raw.csv", delimiter(";") clear

* 3. Rename variables
* NOTE: CBS column names differ per year and download.
* Adjust truncated or numbered names to match
* the exact column names in your downloaded CSV file.

* Core identifiers
rename wijkenenbuurten code
rename gemeentenaam_1  municipality

* Population
rename aantalinwoners_5 population

* Housing wealth
rename gemiddeldewozwaardevanwoningen_3 woz

* Tenure
rename koopwoningen_47      share_owner
rename huurwoningentotaal_48 share_rent

* Income
rename gemiddeldinkomenperinwoner_78 income_pc

* Demographic controls
* NOTE: These variables were retrieved from CBS
* Kerncijfers Wijken en Buurten. Adjust variable names
* to match your downloaded CSV file.
rename percentage65jaarofouder        share_65plus
rename nietwestersetotaal             share_non_west
rename omgevingsadressendichtheid     urban_density
rename gemiddeldehuishoudensgrootte   household_size

* 4. Keep only BU-level (buurten)
keep if substr(code,1,2) == "BU"

* 5. Create bu_code
gen bu_code = code

* 6. Convert to numeric
destring population,    replace force
destring woz,           replace force
destring share_owner,   replace force
destring share_rent,    replace force
destring income_pc,     replace force
destring share_65plus,  replace force
destring share_non_west, replace force
destring urban_density,  replace force
destring household_size, replace force

* 7. Handle missing values
replace woz = . if woz == 0

* 8. Convert percentages to shares (0-1 scale)
replace share_owner    = share_owner    / 100 if share_owner    > 1
replace share_rent     = share_rent     / 100 if share_rent     > 1
replace share_65plus   = share_65plus   / 100 if share_65plus   > 1
replace share_non_west = share_non_west / 100 if share_non_west > 1

* 9. Generate year
* IMPORTANT: adjust year for each file
gen year = 20xx  // <-- aanpassen per file

* 10. Check duplicates
duplicates report bu_code year

* If duplicates exist → inspect first
duplicates tag bu_code year, gen(dup)
browse if dup > 0

* Collapse if necessary
collapse (mean) population woz share_owner share_rent income_pc ///
               share_65plus share_non_west urban_density household_size ///
         (first) municipality, by(bu_code year)

* 11. Panel setup
encode bu_code, gen(bu_id)
xtset bu_id year

* 12. Variable labels
label var population     "Population"
label var woz            "Average house value (WOZ)"
label var share_owner    "Share owner-occupied housing"
label var share_rent     "Share rental housing"
label var income_pc      "Income per capita"
label var share_65plus   "Share aged 65+"
label var share_non_west "Share non-western migrants"
label var urban_density  "Urban density (addresses per km2)"
label var household_size "Average household size"

* 13. Save clean dataset
save "woz_20xx_clean.dta", replace

