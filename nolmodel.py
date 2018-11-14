# -*- coding: utf-8 -*-
"""
Created on Thu Nov  8 10:23:20 2018

@author: cody_
"""

import numpy as np
import pandas as pd
import copy
import scipy
from scipy.stats import norm, describe

cpolicy_base = pd.read_csv('policy_corp_base.csv')
cpolicy_ref = pd.read_csv('policy_corp_ref.csv')
random_numbers = pd.read_csv('pseudo_runif.csv')

#Specify underlying parameters
r = 0.058
pi = 0.024
p = 0.1
sd_p = 0.1
ar1 = 0.75
g = 0.02
numyears = 210

assert numyears <= 210

def getNOLparams(year, baseline):
    """
    Extracts the parameters for the NOL analysis in the given year."
    """
    if baseline:
        policies = copy.deepcopy(cpolicy_base)
    else:
        policies = copy.deepcopy(cpolicy_ref)
    assert year in range(2014, 2028)
    cbyears = int(policies['nol_cbyears'][year-2014].item())
    cfyears = int(policies['nol_cfyears'][year-2014].item())
    refund = policies['nol_refundrate'][year-2014].item()
    inclim = policies['nol_inclimit'][year-2014].item()
    assert cbyears < 10
    assert cfyears >= 0
    assert (refund >= 0) & (refund <= 1)
    assert (inclim >= 0) & (inclim <= 1)
    return (cbyears, cfyears, refund, inclim)

def calc_theta_once(year, baseline, randarray):
    """
    Calculates theta using parameters in place at the given time.
    Runs only once, on the given array of uniform random numbers.
    """
    # Extract parameters
    (cb_years, cf_years, refundrate, inc_limit) = getNOLparams(year, baseline)
    # Growth path of capital stock
    K = np.ones(numyears)
    for i in range(numyears):
        K[i] = ((1 + pi) * (1 + g)) ** (i - 10)
    return1 = np.zeros(numyears)
    netinc1 = np.zeros(numyears)
    taxinc1 = np.zeros(numyears)
    nol_ded1 = np.zeros(numyears)
    nol_cf1 = np.zeros(numyears)
    pv_trueinc1 = np.zeros(numyears)
    pv_taxinc1 = np.zeros(numyears)
    # set values for before beginning (for carrybacks)
    for i in range(10):
        return1[i] = norm.ppf(randarray[i]) * sd_p + p
        netinc1[i] = return1[i] * K[i]
        taxinc1[i] = max(netinc1[i], 0.)
    # calculations for future
    for i in range(10, numyears):
        return1[i] = (norm.ppf(randarray[i]) + ar1 * norm.ppf(randarray[i-1])) * sd_p + p
        netinc1[i] = return1[i] * K[i]
        if i - cf_years >= 10:
            cf_expiring = max(-min(netinc1[i-cf_years], 0) - sum(nol_ded1[i-cf_years:i]), 0)
        else:
            cf_expiring = 0
        nol_cf1[i] = max((nol_cf1[i-1] - min(netinc1[i-1], 0.) - nol_ded1[i-1]) * (i > 10) - cf_expiring, 0.)
        if netinc1[i] < 0.:
            prevtaxinc = 0.
            if cb_years > 0:
                prevtaxinc = np.max(sum(taxinc1[max(i-cb_years, 0):i]), 0)
            nol_ded1[i] = min(-netinc1[i], prevtaxinc) * (1 - refundrate) - netinc1[i] * refundrate
        else:
            nol_ded1[i] = min(netinc1[i] * inc_limit, nol_cf1[i])
        taxinc1[i] = max(netinc1[i], 0.) - nol_ded1[i]
        pv_trueinc1[i] = netinc1[i] / (1 + r) ** (i - 9)
        pv_taxinc1[i] = taxinc1[i] / (1 + r) ** (i - 9)
    return (sum(pv_trueinc1), sum(pv_taxinc1))

def calcTheta(year, baseline, nsim):
    """
    Runs the simulation to calculate theta nsim times, and returns the average.
    """
    assert nsim <= 10000
    assert type(nsim) == int
    trueinc = np.zeros(nsim)
    taxinc = np.zeros(nsim)
    for s in range(nsim):
        (trueinc[s], taxinc[s]) = calc_theta_once(year, baseline, np.array(random_numbers.iloc[[s]])[0])
    TRUEINC = sum(trueinc) / nsim
    TAXINC = sum(taxinc) / nsim
    return TAXINC / TRUEINC

def allTheta(nsim):
    """
    Runs the simulation and saves the results for all years under the baseline
    and under the reform. 
    """
    theta_base = []
    theta_ref = []
    for year in range(2014, 2028):
        theta_base.append(calcTheta(year, True, nsim))
        theta_ref.append(calcTheta(year, False, nsim))
    thetares = pd.DataFrame({"Year": range(2014, 2028),
                             "theta_base": theta_base,
                             "theta_ref": theta_ref})
    thetares.to_csv('intermediate_results/theta_results.csv', index=False)
    return None

