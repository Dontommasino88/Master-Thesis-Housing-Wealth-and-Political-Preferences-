* ==============================
* CBS DATA CLEANING TEMPLATE
* WOZ + CONTROLS 2004-2012
* Tom Huijgens | Utrecht University | 2026
* ==============================

* 1. Set directory
cd "C:/Users/2214946/OneDrive - Universiteit Utrecht/Master Thesis/Data/WOZ Waarde/2009-2012"

* 2. Import CSV
import delimited "cbs_woz_controls_2009_2012_raw.csv", delimiter(";") clear

* 3. Rename variables
* NOTE: CBS column names differ per year and download.
* Adjust names (e.g. aantalinwoner~4) to match
* the exact column names in your downloaded CSV file.

* Core identifiers
rename regios    gm_code
rename perioden  year

* Municipality name
rename gemeentenaam_1 municipality

* Housing wealth
rename gemiddeldewoningwaarde_36 woz

* Tenure
rename koopwoningen_37 share_owner
rename huurwoningen_   share_rent

* Income
rename gemiddeldinkomenperinwoner_65 income_pc

* Population
rename aantalinwoner~4 population

* Demographic controls
* NOTE: These variables were retrieved separately from CBS
* Kerncijfers Wijken en Buurten. Adjust variable names
* to match your downloaded CSV file.
rename percentage65jaarofouder        share_65plus
rename nietwestersetotaal             share_non_west
rename omgevingsadressendichtheid     urban_density
rename gemiddeldehuishoudensgrootte   household_size

* 4. Convert to numeric
destring woz,           replace force
destring share_owner,   replace force
destring share_rent,    replace force
destring income_pc,     replace force
destring population,    replace force
destring share_65plus,  replace force
destring share_non_west, replace force
destring urban_density,  replace force
destring household_size, replace force

* Drop income_receiver if present
capture drop income_receiver

* 5. Fix year variable (CBS format -> numeric year)
gen year_num = real(substr(year,1,4))
drop year
rename year_num year

* 6. Drop Netherlands total
drop if gm_code == 0

* 7. Create BU code
gen code_length = length(string(gm_code))

gen level = ""
replace level = "GM" if code_length <= 2
replace level = "WK" if code_length == 3
replace level = "BU" if code_length >= 5

tab level

keep if level == "BU"
gen bu_code = "BU" + string(gm_code, "%08.0f")

* 8. Convert percentages to shares (0-1 scale)
replace share_owner    = share_owner    / 100 if share_owner    > 1
replace share_rent     = share_rent     / 100 if share_rent     > 1
replace share_65plus   = share_65plus   / 100 if share_65plus   > 1
replace share_non_west = share_non_west / 100 if share_non_west > 1

* 9. Handle missing values
replace woz = . if woz == 0

* 10. Check duplicates
duplicates report bu_code year

* Collapse if duplicates exist
collapse (mean) population woz share_owner share_rent income_pc ///
                share_65plus share_non_west urban_density household_size ///
         (first) municipality, by(bu_code year)

* 11. Panel setup
encode bu_code, gen(bu_id)
xtset bu_id year

* 12. Variable labels
label var population    "Population"
label var woz           "Average house value (WOZ)"
label var share_owner   "Share owner-occupied housing"
label var share_rent    "Share rental housing"
label var income_pc     "Income per capita"
label var share_65plus  "Share aged 65+"
label var share_non_west "Share non-western migrants"
label var urban_density  "Urban density (addresses per km2)"
label var household_size "Average household size"

* 13. Save
save "woz_2004_2012_clean.dta", replace

