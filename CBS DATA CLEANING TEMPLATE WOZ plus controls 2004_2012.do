* ==============================
* CBS DATA CLEANING TEMPLATE WOZ plus controls 2004-2012
* ==============================

* 1. Set directory
cd "C:/Users/2214946/OneDrive - Universiteit Utrecht/Master Thesis/Data/WOZ Waarde/2009-2012"

* 2. Import CSV
import delimited "cbs_woz_controls_2009_2012_raw.csv.csv", delimiter(";") clear

* 3. Rename variables
rename regios gm_code
rename perioden year
rename gemeentenaam_1 municipality
rename aantalinwoner~4 population
rename gemiddeldewoningwaarde_36 woz
rename koopwoningen_37 share_owner
rename huurwoningen_ share_rent
rename gemiddeldinkomenperinwoner_65 income_pc

* 4. Convert to numeric
destring woz, replace force
destring share_owner, replace force
destring share_rent, replace force
destring income_receiver, replace force
destring income_pc, replace force

drop income_receiver
 
* 5. Fix year variable
gen year_num = real(substr(year,1,4))
drop year
rename year_num year

* 6. Drop Netherlands total
drop if gm_code == 0

* 7 create BU code
gen code_length = length(string(regios))

gen level = ""
replace level = "GM" if code_length <= 2
replace level = "WK" if code_length == 3
replace level = "BU" if code_length >= 5

tab level

keep if level == "BU"
gen bu_code = "BU" + string(gm_code, "%08.0f")


* 8 Check duplicates
duplicates report bu_code year

* If duplicates exist → collapse
collapse (mean) population woz share_owner share_rent income_pc ///
         (first) municipality, by(bu_code year)

* Convert percentages to shares
replace share_owner = share_owner / 100
replace share_rent  = share_rent / 100

* Set panel structure
encode bu_code, gen(bu_id)
xtset bu_id year

* 9. Save clean dataset
save "woz_2009_2012_clean.dta", replace