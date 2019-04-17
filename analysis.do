*===========================================================================================#
* Description: includes regression used in analysis
*
* Author: Joe Patten
*
* Updated: April 18, 2019
*===========================================================================================#


*===========================================================================================#
* Institution Analysis
*===========================================================================================#
cd "\output data"
use institution_df, clear

global controls "i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_log_inctot delta_some_coll delta_BAplus delta_st_unemp"
global instruments "delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap"

xtset unitid year

eststo clear
eststo: xi: xtreg delta_log_tot_spend $instruments $controls $options, cluster(unitid) fe
eststo: xi: xtreg delta_log_statetuit $instruments $controls $options, cluster(unitid) fe
eststo: xi: xtivreg2 delta_log_enroll $controls (delta_log_tot_spend delta_log_statetuit = $instruments), cluster(unitid) fe 
estout, cells(b(star fmt(3) label("Model")) se(par fmt(2)label(""))) keep (delta_stapprop_SIV delta*_tuit_cap* delta_log_tot_spend delta_log_statetuit*) style(tex) varlabels(_cons \_cons) label legend starlevels( * 0.10 ** 0.05 *** 0.010)

eststo clear
eststo: xi: xtivreg2 delta_log_enroll $controls (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap), cluster(unitid) fe
forvalues i = 1/3{
	eststo: xi: xtivreg2 delta`i'_log_enroll $controls (delta_log_tot_spend delta_log_statetuit = $instruments), cluster(unitid) fe
}
estout, cells(b(star fmt(3) label("Model")) se(par fmt(2)label(""))) keep (delta_log_tot_spend delta_log_statetuit*) style(tex) varlabels(_cons \_cons) label legend starlevels( * 0.10 ** 0.05 *** 0.010)


*===========================================================================================#
* IPEDS Analysis
*===========================================================================================#
use delta_agg, clear

global controls "i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_log_inctot delta_some_coll delta_BAplus delta_st_unemp"
global instruments "delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap"
global weight ""

eststo clear
eststo: xi: reg delta_log_tot_spend $instruments $controls $options, cluster(statefip) 
eststo: xi: reg delta_log_statetuit $instruments $controls $options, cluster(statefip)
eststo: xi: ivreg2 delta_log_enroll $controls (delta_log_tot_spend delta_log_statetuit = $instruments), cluster(statefip) 
estout, cells(b(star fmt(3) label("Model")) se(par fmt(2)label(""))) keep (delta_stapprop_SIV delta*_tuit_cap* delta_log_tot_spend delta_log_statetuit*) style(tex) varlabels(_cons \_cons) label legend starlevels( * 0.10 ** 0.05 *** 0.010)

//Second
eststo clear
eststo: xi: ivreg2 delta_log_enroll i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weight, cluster(statefip)
eststo: xi: ivreg2 delta1_log_enroll i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weight, cluster(statefip)
eststo: xi: ivreg2 delta2_log_enroll i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weight, cluster(statefip)
eststo: xi: ivreg2 delta3_log_enroll i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weight, cluster(statefip)
estout, cells(b(star fmt(3) label("Model")) se(par fmt(2)label(""))) keep (delta_log_tot_spend delta_log_statetuit*) style(tex) varlabels(_cons \_cons) label legend starlevels( * 0.10 ** 0.05 *** 0.010)

*===========================================================================================#
* ACS + IPEDS Analysis
*===========================================================================================#
use final, clear

global controls "i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_log_inctot delta_some_coll delta_BAplus delta_st_unemp"
global instruments "delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap"
global options "[aweight=hhwt]"

keep if age >= 18 & age <= 24
//Second
eststo clear
eststo: xi: ivreg2 delta_current_college_mean  i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weights, cluster(statefip)
eststo: xi: ivreg2 delta1_current_college_mean i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weights, cluster(statefip)
eststo: xi: ivreg2 delta2_current_college_mean i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weights, cluster(statefip)
eststo: xi: ivreg2 delta3_current_college_mean i.year delta_st_pop delta_black delta_hisp delta_male delta_pov delta_some_coll delta_BAplus delta_st_unemp (delta_log_tot_spend delta_log_statetuit = delta_stapprop_SIV delta_any_tuit_cap delta_tuit_cap) $weights, cluster(statefip)
estout, cells(b(star fmt(3) label("Model")) se(par fmt(2)label(""))) keep (delta_log_tot_spend delta_log_statetuit) style(tex) varlabels(_cons \_cons) label legend starlevels( * 0.10 ** 0.05 *** 0.010)
