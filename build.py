#===========================================================================================#
# Description: builds the following dfs in 'higher_ed\output data'
#  -institution level df (institution_df.dta)
#  -state aggregated IPEDS df (delta_agg.dta)
#  -state aggregated IPEDS with acs state aggregated enrollment and bs attainment (final.dta)
# functions determined too long have been saved in build_functions.py
# 
# Author: Joe Patten
#
# Updated: April 17, 2019
#===========================================================================================#

import os
import numpy as np
import pandas as pd
import sys

path = 'your_path_here'
sys.path.append(path)
import higher_ed.build_functions as b

def build():
    #check for final.dta in 'higher_ed\output data'
    if 'final.dta' in os.listdir(os.path.join(path,'higher_ed\\output data')):
        os.chdir(os.path.join(path,'higher_ed\\output data'))
        return pd.read_stata(r'final.dta')
    else:
        #===========================================================================================#
        # Load in and clean delta cost (IPEDS) data from 'raw\delta_public_release_87_99.dta'
        # and 'raw\delta_public_release_00_15.dta'
        #===========================================================================================#
        os.chdir(os.path.join(path,'higher_ed\\raw'))
        
        #load delta dataset by concatenating two files, and applying heca scalar. See the build_functions.py file.
        delta = b.load_delta()
        delta.head()
        
        #load in state population df, state unemployment, and freezes
        pop = pd.read_csv(r'pop.csv')
        unemp = pd.read_csv(r'unemployment.csv')\
                  .rename(columns = {'fips':'statefip'})
        freezes = b.reshape_long(pd.read_csv(r'freezes.csv'))
        freezes.columns = ['year','state','freeze']
        
        
        
        #merge these dfs into delta
        delta = delta.merge(unemp[['statefip','year','unemployment']], on = ['statefip','year'], how='left')\
                     .merge(freezes, on=['year','state'], how='left')\
                     .merge(pd.read_csv(r'acs_state.csv'), on=['statefip','year'], how='left', suffixes={'','_acs'})\
                     .merge(pop[['year','statefip','state_population']], on=['statefip','year'], how="right", suffixes={"","_acs"})
                     
                     
        #Edit some freeze values corresponding to freeze.pdf
        for fip,level in zip([1,9,23,24,29,33,34,37,41,55],[2,1,2,1,1,2,1,1,1,1]):
            delta.loc[(delta['statefip'] == fip) & (delta['iclevel'] != level), 'freeze'] = np.nan
            
        delta.loc[(delta['statefip'] == 36) & ((delta['unitid'] != 190415) & (delta['unitid'] != 190567)), 'freeze'] = np.nan
        
        #rename delta df
        d = {'total03_revenue':'tot_rev', 'tuitionfee02_tf':'statetuit', 'state03':'st_approp', 'fips':'st_fips', 'state_population_acs':'st_pop',
             'total_state_appropriations':'state_approp_total', 'state_med_income':'inctot', 'state_black_race':'black', 'state_male_ratio':'male',
             'state_below_poverty':'pov','state_some_college':'some_coll', 'state_bs_college':'BAplus', 'state_hispanic':'hisp',
             'eandg01':'tot_spend', 'level_of_institution':'iclevel', 'unemployment':'st_unemp', 'total_enrollment':'enroll',
             'totalcompletions':'cert_total','totaldegrees':'award_total', 'associatedegrees':'aa_total', 'bachelordegrees':'ba_total'}
        delta = delta.rename(columns=d)
        
        #create budget shock
        delta = b.create_instruments(delta, tuitcaps=True)
        
        #create per enrollment vars
        delta = b.per_enroll(delta)
            
        delta.rename(columns={'tot_tuition_enroll':'tuit_enroll', 'tot_spend_enroll':'spend_enroll'}, inplace=True)
        
        delta['year_trend']=delta.year-1989
        
        #add variables - also think about making a pipeline to make the code a bit more readable
        delta = b.log_vars(delta)
        delta = b.create_lags(delta, 'unitid')
        delta = b.diff_lags(delta, 'unitid')
        delta_agg = b.diff_covs(delta, 'unitid')
        delta = delta.replace([np.inf, -np.inf], np.nan)

        #only keep public institutions
        delta = delta[delta.control == 1]
        
        os.chdir(os.path.join(path,'higher_ed\\output data'))
        delta.to_stata(r'institution_df.dta')
        
        #===========================================================================================#
        # Aggregate delta cost (IPEDS) data to the state level
        #===========================================================================================#
        delta_agg = b.aggregate_delta(delta)
        
        #add variables
        delta_agg = b.create_instruments(delta_agg)
        delta_agg = b.per_enroll(delta_agg)\
                     .rename(columns={'tot_spend_enroll':'spend_enroll'})
        delta_agg = b.log_vars(delta_agg)\
                     .rename(columns={'log_st_approp':'log_approp'})
        delta_agg = b.create_lags(delta_agg, 'statefip')
        delta_agg = b.diff_lags(delta_agg, 'statefip')
        delta_agg = b.diff_covs(delta_agg, 'statefip')
        
        #output state-aggregated delta cost data 
        os.chdir(os.path.join(path,'higher_ed\\output data'))
        delta_agg.to_stata(r'delta_agg.dta')
        
        #===========================================================================================#
        # Aggregate ACS data to the state level and merge it with aggregated delta cost data
        #===========================================================================================#
        #load in state acs data for enrollment and degree completion variables
        if 'state_df.csv' in os.listdir(os.path.join(path,'higher_ed\\output data')):
            state_df = pd.read_csv(r'state_df.csv')
        else:
            os.chdir(os.path.join(path,'higher_ed\\raw'))
            state_df = b.aggregate_acs()
            state_df.to_csv(r'state_df.csv')
            
        state_df = b.log_vars(state_df, cols=['current_college', 'bs_college', 'assoc_college'])
        state_df = b.diff_lags(state_df, group='bpl', cols = ['current_college_mean', 'bs_college_mean', 
                    'assoc_college_mean', 'pov_current_college_mean', 'pov_bs_college_mean',
                    'log_current_college', 'log_bs_college', 'log_assoc_college', 'some_college_mean'])
            
        final = delta_agg.merge(state_df, left_on=['statefip','year'], right_on=['bpl','college_year'], how='left')\
                        .rename(columns={'year_y':'year_acs', 'year_x':'year'})
                        
        final = final[(final.bpl != 11) & (final.year != 2014)]
        final = final.replace([np.inf, -np.inf], np.nan)
        
        os.chdir(os.path.join(path,'higher_ed\\output data'))
        final.to_stata(r'final.dta')
        return final

if __name__ == '__main__':
    print(build())
    