* ==============================

* CBS DATA CLEANING TEMPLATE WOZ + controls (2013+)

* ==============================

* 1. Set directory
     cd "C:/Users/2214946/OneDrive - Universiteit Utrecht/Master Thesis/Data/WOZ Waarde/20xx"

* 2. Import CSV
     import delimited "cbs_woz_controls_20xx_raw.csv.csv", delimiter(";") clear

* 3. Rename variables
     rename wijkenenbuurten code
     rename gemeentenaam_1 municipality
     rename aantalinwoners_5 population
     rename gemiddeldewozwaardevanwoningen_3 woz
     rename koopwoningen_47 share_owner
     rename huurwoningentotaal_48 share_rent
     rename gemiddeldinkomenperinwoner_78 income_pc

* 4. Keep only BU-level (buurten)
     keep if substr(code,1,2) == "BU"

* 5. Create bu_code
     gen bu_code = code

* 6. Convert to numeric (if needed)
     destring population, replace force
     destring woz, replace force
     destring share_owner, replace force
     destring share_rent, replace force
     destring income_pc, replace force

* 7. Handle missing values
     replace woz = . if woz == 0


* 8. Convert percentages to shares
replace share_owner = share_owner / 100
replace share_rent  = share_rent / 100

* 9. Generate year (IMPORTANT: adjust if needed)
     gen year = 20xx  // <-- aanpassen per file of loop later

* 10. Check duplicates
      duplicates report bu_code year

* If duplicates exist → inspect first
  duplicates tag bu_code year, gen(dup)
  browse if dup > 0

* Collapse if necessary
  collapse (mean) population woz share_owner share_rent income_pc ///
  (first) municipality, by(bu_code year)

* 11. Panel setup
      encode bu_code, gen(bu_id)
      xtset bu_id year

* 12. Labels (nice for thesis)
      label var population "Population"
      label var woz "Average house value (WOZ)"
      label var share_owner "Share owner-occupied housing"
      label var share_rent "Share rental housing"
      label var income_pc "Income per capita"

* 13. Save clean dataset
      save "woz_20xx_clean.dta", replace
