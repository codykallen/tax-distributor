# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:19:52 2018

@author: cody_
This is the main execution file. It runs all the other files in the 
appropriate orders to ensure that the model works.
"""

# Import necessary packages
import os
import taxcalc
from taxcalc import *
import numpy as np
import pandas as pd
import copy
from scipy.stats import norm
    
puf_path = 'data_files/puf09112018.csv'
os.chdir('C:/Users/cody_/Documents/GitHub/tax-distributor/')
path_to_growfactors = 'taxcalc/'
scfresults_path = 'data_files/scf_results.csv'

# Code for creating calculators
def make_calculator(refdict = {}, year=2018):
    """
    Creates a calculator advanced to the given year and calculates tax results
    Note: Passing an empty dictionary to refdict produces a 
          current law calculator (TCJA law)
    """
    assert year in range(2014, 2028)
    assert type(refdict) is dict
    pol = Policy()
    beh = Behavior()
    rec = Records(puf_path)
    if refdict != {}:
        pol.implement_reform(refdict)
    calc1 = Calculator(pol, rec, beh)
    calc1.advance_to_year(year)
    calc1.calc_all()
    return calc1

# Make the pre-TCJA and TCJA calculators
year_to_use = 2018
param = Calculator.read_json_param_objects(taxcalculator_path + 'taxcalc/reforms/2017_law.json', None)
calc_pre = make_calculator(param['policy'], year_to_use)
calc_tcja = make_calculator({}, year_to_use)

# Change in corporate tax liabilities for each year 2018-2027
ctaxrev = {"2018": -94.38 * 10**9,
           "2019": -95.83 * 10**9,
           "2020": -79.939 * 10**9,
           "2021": -56.961 * 10**9,
           "2022": -31.9 * 10**9,
           "2023": -7.383 * 10**9,
           "2024": 9.777 * 10**9,
           "2025": 14.129 * 10**9,
           "2026": -9.033 * 10**9,
           "2027": -57.566 * 10**9}

# Define all the assumptions we will use
exec(open('assumptions.py').read())

# Execute the necessary code for distributional analysis (in general)
exec(open('distributional_code.py').read())

# Run the individual income tax distributional analysis
exec(open('indiv_tables_code.py').read())

# Run the equity imputations
exec(open('equity_imputation_code.py').read())
(equity1, dshare1, wtshare1) = imputeAllEquityInfo(calc_pre)
equity = np.array(equity1)
dshare = np.array(dshare1)
wtshare = np.array(wtshare1)


# Execute the necessary code for the business tax distribution
exec(open('business_distribution_code.py').read())

# Run the static corporate income tax distributional analysis
exec(open('business_tables_code.py').read())

"""
If desired, run using a simple growth model, based on a first-order
log-linearized effect using marginal incentives only.
Alternatively, run using robustness analysis for growth effects.
"""
ownGrowthModel = True

if ownGrowthModel:
    # Run the NOL distortion model
    exec(open('nolmodel.py').read())
    allTheta(1000)
    # Execute code for and estimate individual tax incentives
    exec(open('labor_model.py').read())
    calc_pre2 = make_calculator(param['policy'], 2014)
    calc_tcja2 = make_calculator({}, 2014)
    allLaborChanges(calc_pre2, calc_tcja2, eti)
    allOwnerTaxes(calc_pre2, calc_tcja2)
    # Execute the investment model and estimate changes in investment
    exec(open('investmentmodel.py').read())
    allInvChanges(ELAST_INV_CORP, ELAST_INV_NONCORP, SELAST_INV_MNE)
    # Execute the growth model
    exec(open('growthmodel.py').read())
else:
    # Growth effect to consider (pct change in GDP level)
    geffect = 0.0
    # Construct alternative file for growth effect (permanent increase in 2018)
    growdiffs1 = np.zeros(13)
    growdiffs1[4] = geffect
    # Save these alternative growth rate effects to file for dynamic work
    growdiff_tab = pd.DataFrame({"Year": range(2015, 2028),
                                 "gfactors": growdiffs1})
    growdiff_tab.to_csv("intermediate_results/growdiffs.csv")

# Execute the dynamic distributional anaylsis
exec(open('dynamic_distribution_code.py').read())
