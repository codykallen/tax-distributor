# -*- coding: utf-8 -*-
"""
Created on Sat Sep 29 09:31:00 2018

@author: cody_

This file imputes equity ownership to tax units. These functions assume
the existence of a Calculator object calc. 

They also assume that the relevant analysis of the SCF has already been 
completed, and that the probabilities of equity ownership and average values 
have been saved for each group in a file "scf_results.csv". This csv has the
following columns:
    'prob_stock': probability of stock ownership
    'stock_average': average amount of stock, conditional on ownership
    'group_income': identifier for income group
    'group_mars': identifier for marital status
    'group_age': identifier for age group
"""
import numpy as np
import pandas as pd
import copy

scf_results = pd.read_csv('C:/Users/cody_/Desktop/scf/scf_results.csv')

def assignGroup(calc1):
    """
    This function takes in a Calculator object and assigns tax units to 
    groups. It returns a 3 arrays, where each filing unit is assigned a list
    of groups, with the groups corresponding to those used in the
    SCF analysis. 
    Current version:
        Assigns age groups using age of head
        Assigns income groups using comparable income measure, nested in age
    """
    # Assign age groups
    age = calc1.array('age_head')
    group_age0 = np.zeros(len(age))
    group_age1 = np.where(age >= 35, 1, group_age0)
    group_age2 = np.where(age >= 45, 2, group_age1)
    group_age3 = np.where(age >= 55, 3, group_age2)
    group_age4 = np.where(age >= 65, 4, group_age3)
    group_age5 = np.where(age >= 75, 5, group_age4)
    # Create comparable income measure
    compinc = (calc1.array('e00200') + calc1.array('e02100') +
               calc1.array('e00900') + calc1.array('e02000') +
               calc1.array('e00400') + calc1.array('e00300') +
               calc1.array('e00600') + calc1.array('e02300') +
               calc1.array('e01500') + calc1.array('e02400'))
    wgt = calc1.array('s006')
    indx = np.array(range(len(wgt)))
    # Create empty lists for storing results
    indxresults = []
    incgrpresults = []
    for a in range(6):
        # Restrict to just those in the given age category
        compinc1 = compinc[group_age5 == a]
        wgt1 = wgt[group_age5 == a]
        indx1 = indx[group_age5 == a]
        # Sort by income
        (compinc2, wgt2, indx2) = zip(*sorted(zip(compinc1, wgt1, indx1)))
        # Save as arrays
        compinc3 = np.array(compinc2)
        wgt3 = np.array(wgt2)
        indx3 = np.array(indx2)
        # Cumulative weight
        cumwgt3 = np.cumsum(wgt3) / sum(wgt3)
        # Assign income groups
        group_inc3 = np.zeros(len(compinc3))
        group_inc3 = np.where(cumwgt3 > 0.2, 1, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.4, 2, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.6, 3, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.8, 4, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.9, 5, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.95, 6, group_inc3)
        group_inc3 = np.where(cumwgt3 > 0.99, 7, group_inc3)
        # Save income group and index to lists
        indxresults.append(indx3)
        incgrpresults.append(group_inc3)
    # Combine the indexes and income group arrays
    index1 = np.concatenate((indxresults[0], indxresults[1], indxresults[2],
                             indxresults[3], indxresults[4], indxresults[5]))
    incgroup1 = np.concatenate((incgrpresults[0], incgrpresults[1],
                                incgrpresults[2], incgrpresults[3],
                                incgrpresults[4], incgrpresults[5]))
    # Restore the original order
    (index2, incgroup2) = zip(*sorted(zip(index1, incgroup1)))
    incgroup3 = np.array(incgroup2)
    # Combine the top 2 income groups for the young age group
    youngandrich = (group_age5 == 0) * (incgroup3 == 7)
    incgroup4 = np.where(youngandrich, 6, incgroup3)
    # Make group identifier
    groupid = []
    for i in range(len(age)):
        groupid.append(str(int(group_age5[i])) + "_" + str(int(incgroup4[i])))
    return (groupid)

def identifyStockholders(calc1):
    """
    This function identifies owners of stock, using income from equity:
            e00600: dividends (includes qualified and nonqualified)
            p22250: short-term capital gain/loss
            p23250: long-term capital gain/loss
    It returns an array of booleans for equity ownership.
    """
    has_div = (calc1.array('e00600') != 0)
    has_stcg = (calc1.array('p22250') != 0)
    has_ltcg = (calc1.array('p23250') != 0)
    has_equity = has_div | has_stcg | has_ltcg
    return has_equity

def identifyOAssetholders(calc1):
    """
    This function identifies owners of non-equity financial assets, using
    capital income not from equity:
        e00300: taxable interest income
        e00400: tax-exempt interest income
    It returns an array of booleans for non-equity asset ownership.
    """
    has_int1 = (calc1.array('e00300') != 0)
    has_int2 = (calc1.array('e00400') != 0)
    hasoassets = has_int1 | has_int2
    return hasoassets

def fracAssetholders(calc1, scfdata):
    """
    This function uses identified stockholders to estimate the fraction of
    people in each group who certainly own stock. It then estimates the 
    probability of stock ownership for those not identified as owning stock.
    These reults are saved into a dataset and returned.
    """
    # Information on PUF units
    scf_data2 = copy.deepcopy(scfdata)
    wgt = calc1.array('s006')
    groupid = assignGroup(calc1)
    holders = identifyStockholders(calc1)
    owners = identifyOAssetholders(calc1)
    # Empty vectors for SCF group data
    frac_holders = np.zeros(len(scf_data2))
    frac_owners = np.zeros(len(scf_data2))
    grpid = []
    for g in range(len(frac_owners)):
        # Extract SCf information to match individuals to groups
        incnum = scf_data2['group_income'][g]
        agenum = scf_data2['group_age'][g]
        grpid.append(str(agenum) + "_" + str(incnum))
        match_groups = [x == grpid[g] for x in groupid]
        # Calculate the share with equity income
        frac_holders[g] = (sum(holders[match_groups * holders] * 
                               wgt[match_groups * holders]) / 
                           sum(wgt[match_groups]))
        # Calculate the share with income from other financial assets
        frac_owners[g] = (sum(owners[match_groups * owners] *
                              wgt[match_groups * owners]) /
                          sum(wgt[match_groups]))
    # Save the share with equity income
    scf_data2['frac_eqinc'] = np.minimum(frac_holders,
                                         np.array(scf_data2['prob_stock']))
    # Save the share with other financial income
    scf_data2['frac_oainc'] = np.minimum(frac_owners,
                                         np.array(scf_data2['prob_oassets']))
    # Probability of equity ownership given no equity income
    scf_data2['prob_stock2'] = ((scf_data2['prob_stock'] - 
                                 scf_data2['frac_eqinc']) / 
                                (1 - scf_data2['frac_eqinc']))
    # Probability of other asset ownership given no income from nonequity assets
    scf_data2['prob_oassets2'] = ((scf_data2['prob_oassets'] -
                                   scf_data2['frac_oainc']) /
                                  (1 - scf_data2['frac_oainc']))
    # Save the group identifier
    scf_data2['groupid'] = grpid
    return scf_data2

scf_results2 = fracAssetholders(calc_pre, scf_results)

def imputeEquity(calc1):
    """
    This function imputes the expected amount of equity per person.
    """
    groupid = assignGroup(calc1)
    holders = identifyStockholders(calc1)
    equity = np.zeros(len(holders))
    for i in range(len(holders)):
        prob2 = scf_results2['prob_stock2'][scf_results2['groupid'] == groupid[i]].item()
        eqavg = scf_results2['lequity'][scf_results2['groupid'] == groupid[i]].item()
        if holders[i]:
            equity[i] = np.exp(eqavg)
        else:
            equity[i] = prob2 * np.exp(eqavg)
    return equity

def imputeDirectEquity(calc1):
    """
    This function imputes the expected share of equity held in
    direct form (stocks and corporate equity in directly held mutual funds). 
    All other equity is held in tax-preferred savings accounts.
    """
    groupid = assignGroup(calc1)
    dshare = np.zeros(len(groupid))
    for i in range(len(groupid)):
        dshare[i] = scf_results2['deqshare'][scf_results2['groupid'] == groupid[i]].item()
    return dshare

def imputeTaxableIndirectEquity(calc1, dshare):
    """
    This function imputes the expected share of equity held in indirect form
    that is subject to tax at withdrawal. 
    """
    groupid = assignGroup(calc1)
    wtshare = np.zeros(len(groupid))
    for i in range(len(groupid)):
        wtshare[i] = scf_results2['disttaxshare'][scf_results2['groupid'] == groupid[i]].item()
    return wtshare

def imputeOtherFA(calc1):
    """
    This function imputes the expected non-equity financial assets.
    """
    groupid = assignGroup(calc1)
    owners = identifyOAssetholders(calc1)
    oassets = np.zeros(len(owners))
    for i in range(len(owners)):
        prob2 = scf_results2['prob_oasssets'][scf_results2['groupid'] == groupid[i]].item()
        oaavg = scf_results2['loassets'][scf_results2['groupid'] == groupid[i]].item()
        if owners[i]:
            oassets[i] = np.exp(oaavg)
        else:
            oassets[i] = prob2 * np.exp(oaavg)
    return oassets

def advanceEquity(equity2016, year):
    """
    This function takes the imputed equity amount for 2016 and advances it to
    the requested year, using the CBO estimates of nominal corporate profits
    as the growth factor. The CBO numbers go from 2015 thtrough 2027, and are
    from the June 2017 report.
    """
    assert year in range(2015, 2028)
    EQtotal = [2088.1, 2085.8, 2093.9, 2097.9, 2117.7, 2148.1, 2192.6, 2252.8,
               2334.8, 2424.0, 2517.1, 2619.5, 2724.6]
    equity = equity2016 * EQtotal[year - 2015] / EQtotal[1]
    return equity





