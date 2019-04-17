#===========================================================================================#
# Description: includes functions that are used in build.py 
# (imported as b in build.py)
#
# Author: Joe Patten
#
# Updated: April 17, 2019
#===========================================================================================#

import numpy as np
import pandas as pd
import re

def reshape_long(df):
    #use pd.wide_to_long to have columns (which are years) become row values
    rename_dict = {col[:-4]:col[:-5] for col in df if re.match(r'\D*\d{4}$',col)}
    stub_list = list({col[:-4] for col in df if re.match(r'\D*\d{4}$',col)})

    #reindex
    df.reset_index(inplace=True,drop=True)
    df['id'] = df.index

    df = pd.wide_to_long(df, stubnames=stub_list, i='id', j='year').reset_index().rename(columns=rename_dict)
    df = df.drop(['id'], axis=1)
    return df


def load_delta():
	delta = pd.concat([pd.read_stata(r'delta_public_release_87_99.dta'),pd.read_stata(r'delta_public_release_00_15.dta')])
	delta = delta[(delta['academicyear']>=1990) & (delta['academicyear']<=2015)]

	delta = delta.rename(columns={'academicyear':'year','ansi_code':'statefip'})

	inst = ['control', 'state','unitid', 'hepi_scalar_2015', 'heca_scalar_2015']
	revenue = ['state03','total03_revenue']
	spending = ['eandg01']
	tuition_fees = ['tuitionfee02_tf']
	control_vars = ['hospital','medical']
	misc = ['iclevel','statefip','year']
	enrollment = ['total_enrollment','bachelordegrees','totaldegrees','totalawards','associatedegrees','totalcompletions']
    
    #subset the data
	delta = delta[inst + revenue + spending + tuition_fees + control_vars + misc + enrollment] 
    
    #apply heca scalar (to normalize to 2015)
	delta[revenue + spending + tuition_fees] = delta[revenue + spending + tuition_fees].div(delta['heca_scalar_2015'], axis=0) #change to hepi? heca_scalar_2015

	delta.sort_values([ 'unitid', 'year'], inplace=True)
	
	delta.loc[delta.total03_revenue.isna(),'state03'] = np.nan
	delta.loc[delta.state03.isna(),'total03_revenue'] = np.nan
    
    #get revenue and state appropriations in 1990 (to be used as a baseline in analysis). get state appropriations aggregated to the state
	revenue90 = delta.groupby(['unitid'])['total03_revenue','state03'].nth(0).reset_index().rename(index=str, columns={'total03_revenue':'revenue90','state03':'approps90'})
	state_approps = delta.groupby(['state','year'])['state03'].sum().reset_index().rename(index=str, columns={'state03':'total_state_appropriations'})
	delta = delta.merge(revenue90, on='unitid').merge(state_approps, on=['state','year'])
	
	return delta
	
def create_instruments(df, tuitcaps=False):
    df['st_approp_share90'] = df['approps90']/df['revenue90']
    df['stapprop_actual']=df['st_approp']/10000000
    df['state_approp_percap']=df.state_approp_total/df.st_pop
    df['stapprop_SIV']=(df.state_approp_percap*df.st_approp_share90)/1000
    
    if tuitcaps:
        df['tuit_cap'] = df['freeze']
        df['no_tuit_cap'] = (df['tuit_cap'].isna()).astype(int)
        df['any_tuit_cap'] = (df['no_tuit_cap'] == 0).astype(int)
        df.loc[df['tuit_cap'].isna(), 'tuit_cap'] = 0
    return df

def per_enroll(df):
    for col in ['st_approp', 'tot_spend']:
        df[col+'_enroll'] = df[col]/df.enroll
    return df

def log_vars(df, cols=None):
    if cols == None:
        cols = ['statetuit', 'tot_spend', 'st_pop', 'enroll', 'aa_total', 'ba_total', 'cert_total', 'inctot', 'spend_enroll', 'st_approp']
    for col in cols:    
        df['log_'+col] = np.log(df[col]) 
    return df

def create_lags(df, group):
    df.sort_values([group,'year'], inplace=True)
    grouped = df.groupby([group])
    
    for col in ['log_tot_spend', 'log_statetuit','log_spend_enroll']:
        for y in range(1,6):
            df[f'{col}_lag{y}'] = grouped[f'{col}'].shift(-y)
            df[f'{col}_lead{y}'] = grouped[f'{col}'].shift(y)
    return df

def diff_lags(df, group, cols=None):
    df.sort_values([group,'year'], inplace=True)
    grouped = df.groupby([group])
    if cols == None:
        cols = ['log_enroll', 'log_cert_total', 'log_tot_spend', 'log_statetuit', 'stapprop_SIV','tuit_cap', 'any_tuit_cap']
    for col in cols:
        df['delta_'+col] = df[col] - grouped[col].shift()
        for i in range(1,5):
            df[f'delta{i}_'+col] = grouped[col].shift(-i) - grouped[col].shift()
            df[f'delta_{i}_'+col] = grouped[col].shift(i+1) - grouped[col].shift()
        for y in range(1,8):
            df[f'delta_{col}_lead{y}'] = grouped[col].shift(-y) - grouped[col].shift()
            df[f'delta_{col}_lag{y}'] = grouped[col].shift(y) - grouped[col].shift(y+1)
            
    return df

def diff_covs(df, group):
    df.sort_values([group,'year'], inplace=True)
    grouped = df.groupby([group])
    for col in ['st_pop', 'black', 'hisp', 'male', 'pov', 'log_inctot', 'some_coll', 'BAplus', 'st_unemp']:
        df['delta_'+col] = df[col] - grouped[col].shift()
    return df

def aggregate_delta(df):
    grouped = df.groupby(['statefip','year'])

    def f(x):
        #create dictionary of how I want to agg variables
        d = {}
        
        d['statetuit_wgt'] = (x['statetuit']*x['enroll']).sum()/x['enroll'].sum()
        
        for col in ['statetuit', 'any_tuit_cap', 'tuit_cap']:
            d[col] = x[col].mean()
               
        for col in ['any_tuit_cap', 'tuit_cap']:
            for i in range(1,3):
                d[col+f'_{i}'] = x[x['iclevel'] == i][col].mean()
            
        for col in ['cert_total', 'ba_total', 'aa_total', 'enroll', 'tot_spend', 'approps90', 'revenue90', 'st_approp']:
            d[col] = x[col].sum()
            
        for col in ['st_pop', 'black', 'pov', 'st_unemp', 'hisp', 
                    'male', 'inctot', 'some_coll', 'BAplus', 'state_approp_total']:
            d[col] = x[col].max()
            
        d['count'] = x[col].count()
        
        return pd.Series(d, index=[k for k in d])
    
    df_agg = grouped.apply(f)\
                    .reset_index()
    return df_agg

def aggregate_acs():
    df = pd.read_csv(r'acs_individual.csv')
    
    #subset data
    df = df[df['year'] > 2000]
    df = df[df.age >= 18]
    
    #replace missing variables (coded as 9999999) to np.nan
    df = df.replace(9999999, np.nan)
    df.sort_values(['statefip','county','year'],inplace=True)
    cols = ['year', 'hhwt', 'statefip', 'county', 'gq',
           'pernum', 'perwt', 'sex', 'age', 'race', 'raced', 'hispan',
           'hispand', 'school', 'educd', 'inctot',
           'poverty','datanum','serial', 'bpl']
    df = df[cols]
    
    #create dummies for variables of interest
    df['below_poverty'] = (df['poverty']<=100).astype(int)
    df['below_poverty_50'] = (df['poverty']<=50).astype(int)
    df['below_poverty_25'] = (df['poverty']<=25).astype(int)
    df['bs_college'] = (df['educd']>=101).astype(int)
    df['assoc_college'] = (df['educd']>=81).astype(int)
    df['_1_yr_college'] = (df['educd']>=71).astype(int)
    df['less_1_yr_college'] = (df['educd']==65).astype(int)
    df['current_school'] = (df['school']>=2).astype(int)
    df['some_college'] = (df['educd']>=65).astype(int)
    df['current_college'] = (df['some_college'] & df['current_school']).astype(int)
    df['coll_age_population'] = ((df['age']>=18) & (df['age']<=24)).astype(int)
    
    #create dummies based on interactions
    df['pov_current_college'] = df['below_poverty']*df['current_college']
    df['pov_bs_college'] = df['below_poverty']*df['bs_college']
    
    #create variable list of created dummies
    idx = list(df.columns).index('below_poverty')
    cols = df.columns[idx:]
    
    #create year individual was 18
    df['college_year'] = df['year'] - (df['age']-18)
    
    #groupby cohort (college_year), year of survey (year), and birthplace (bpl)
    grouped = df.groupby(['bpl','year','age','college_year'])
    
    #need the sum AND the weighted mean
    def f(x):
        d = {}
        d['hhwt'] = x['hhwt'].sum()
        
        for col in cols:
            d[col+'_mean'] = (x[col]*x['hhwt']).sum()/x['hhwt'].sum()
            d[col] = (x[col]*x['hhwt']).sum()
            
        return pd.Series(d, index=[k for k in d])
    
    state_df = grouped.apply(f)
    state_df.reset_index(inplace=True)
    return state_df