# glassdoor_spending

A little description of the files

# Scripts
- build.py: builds the 3 dfs needed for the analysis
- build_functions.py: includes the functions used in build.py (that were too big to be included in build.py)
- analysis.py: includes code for summary stats
- analysis.do: includes regressions used in analysis of the paper

# Data
You will notice that some of the data files are missing (frow the raw and output data directories). This is because they were too big for github. Here is a list of those not included in the repo

From \raw

| filename                       | description                   | size    |
|--------------------------------|-------------------------------|---------|
| delta_public_release_00_15.dta | IPEDS data from 2000-2015     | 223 MB  |
| delta_public_release_87_00.dta | IPEDS data from 1987-2000     | 210 MB  |
| acs_individual.csv             | ACS data from 1990, 2000-2013 | 1.47 GB |

From \output data

| filename                       | description                   | size    |
|--------------------------------|-------------------------------|---------|
| final.dta | acs data state aggregated by cohort, year, and college_year (see paper)     | 43 MB  |
| institution_df.dta | cleaned up IPEDS data at insitution level     | 77 MB  |
