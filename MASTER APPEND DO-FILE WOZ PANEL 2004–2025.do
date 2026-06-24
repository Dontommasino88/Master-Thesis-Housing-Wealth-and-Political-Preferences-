* ============================================

* MASTER APPEND DO-FILE: WOZ PANEL 2004–2023

* ============================================

* 1. Set working directory
     cd "C:/Users/2214946/OneDrive - Universiteit Utrecht/Master Thesis/Data/WOZ Waarde"

* ============================================

* 2. LOAD BASE DATA (2004–2012)

* ============================================

use "woz_2004_20xx_master.dta", clear

* Check base
  describe
  tab year

* ============================================

* 3. APPEND 2013+

* ============================================

append using "C:\Users\2214946\OneDrive - Universiteit Utrecht\Master Thesis\Data\WOZ Waarde\20xx\woz_20xx_clean.dta"

  
* Check of alles goed ging
duplicates report bu_code year

* Panel opnieuw zetten (correct na append)

drop bu_id
encode bu_code, gen(bu_id)

xtset bu_id year

xtdescribe


* Save nieuwe master
save "woz_2004_2025_master_final.dta", replace