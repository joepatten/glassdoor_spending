#===========================================================================================#
# Description: analysis done on the following dfs in 'higher_ed\output data'
#  -institution level df (institution_df.dta)
#  -state aggregated IPEDS df (delta_agg.dta)
#  -state aggregated IPEDS with acs state aggregated enrollment and bs attainment (final.dta)
# functions determined too long have been saved in analysis_functions.py
# 
# Stata (analysis.do) was used for most of the analysis due to Stata having greate panel tools
#
# Author: Joe Patten
#
# Updated: April 17, 2019
#===========================================================================================#

import os
import numpy as np
import pandas as pd
import sys
import seaborn as sns
import matplotlib.pyplot as plt
%matplotlib inline


path = 'your_path_here'

#===========================================================================================#
# Data Summary (Table 1)
#===========================================================================================#
os.chdir(os.path.join(path,'higher_ed\\output data'))
df = pd.read_stata(r'institution_df.dta')

grouped = df.groupby(['year'])
def f(x):
    d = {}
    d['count_Two year'] = x[x['iclevel']==2]['iclevel'].count()
    d['count_Four year'] = x[x['iclevel']==1]['iclevel'].count()
    for col in ['statetuit', 'enroll']:
        d[(col+'_Two year')] = x[x['iclevel']==2][col].mean()
        d[(col+'_Four year')] = x[x['iclevel']==1][col].mean()
    for col in ['st_approp', 'tot_spend']:
        d[(col+'_Two year')] = x[x['iclevel']==2][col].sum()/x[x['iclevel']==2]['enroll'].sum()
        d[(col+'_Four year')] = x[x['iclevel']==1][col].sum()/x[x['iclevel']==2]['enroll'].sum()
    return pd.Series({k:v for k,v in d.items()})

temp = grouped.apply(f).loc[[1990,2013]].stack().unstack(level=0).reset_index()
temp[['Variable','Institution Type']] = temp['index'].str.rsplit('_',1,expand=True)
table1 = temp.pivot(index='Variable', columns='Institution Type')[[1990,2013]].astype(int)
print(table1.to_latex())
print(table1)
