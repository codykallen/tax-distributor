# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:19:52 2018

@author: cody_
This is the main execution file. It runs all the other files in the 
appropriate orders to ensure that the model works.

Instructions for using the model:
"""

# Import necessary packages
import taxcalc
from taxcalc import *
import numpy as np
import pandas as pd
import copy
from scipy.stats import norm

puf_path = 'C:/Users/cody_/Documents/GitHub/tax-calculator/puf.csv'

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
param = Calculator.read_json_param_objects('../../taxcalc/reforms/2017_law.json', None)
calc_pre = make_calculator(param['policy'], year_to_use)
calc_tcja = make_calculator({}, year_to_use)

# Execute the necessary code for distributional analysis (in general)
exec(open('distributional_code.py').read())

# Run the individual income tax distributional analysis
exec(open('indiv_tables_code.py').read())

# Run the equity imputations
exec(open('equity_imputation_code.py').read())
equity = imputeEquity(calc_pre)
dshare = imputeDirectEquity(calc_pre)
wtshare = imputeTaxableIndirectEquity(calc_pre, dshare)

# Execute the necessary code for the business tax distribution
exec(open('business_distribution_code.py').read())

# Run the static corporate income tax distributional analysis
exec(open('business_tables_code.py').read())

# Run the NOL distortion model
exec(open('nol_model.py').read())
allTheta(1000)

# Execute code for and estimate individual tax incentives
exec(open('labormodel.py').read())
allOwnerTaxes(calc_pre, calc_tcja)

# Execute the investment model and estimate changes in investment
exec(open('investmentmodel.py').read())
allInvChanges(-1.0, -1.0, -3.0)

# Execute the growth model
exec(open('growthmodel.py').read())

# Execute the dynamic distributional anaylsis
exec(open('dynamic_distribution_code.py').read())



