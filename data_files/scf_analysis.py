import os
import pandas as pd
import numpy as np

# Read in Stata datasets
scf1 = pd.read_stata('p16i6.dta')
scf2 = pd.read_stata('rscfp2016.dta')

"""
Analyze raw SCF data to get the following measures:
    compincome: Income measure comparably defined across SCF & IRS
    disttaxshare: Of savings in tax-preferred accounts, 
                  the share in accounts subject to tax at withdrawal
"""
# Build measure of comparable income
compincome = np.array(scf1['X5702'] + scf1['X5704'] + scf1['X5714'] +
                      scf1['X5706'] + scf1['X5708'] + scf1['X5710'] +
                      scf1['X5716'] + scf1['X5722'], dtype=float)
# Amount in Roth IRA
rothira = scf1['X6551'] + scf1['X6559'] + scf1['X6567']
# Amount in regular IRA
ira = (scf1['X6553'] + scf1['X6561'] + scf1['X6569'] +
       scf1['X6552'] + scf1['X6560'] + scf1['X6568'])
# Amount in Keogh account
keogh = scf1['X6554'] + scf1['X6562'] + scf1['X6570']
# Separate spending accounts by tax-preferred status (HSA, 529, Coverdell)
sav1 = np.where(scf1['X3732'] == 2, scf1['X3730'], 0.)
sav2 = np.where(scf1['X3738'] == 2, scf1['X3736'], 0.)
sav3 = np.where(scf1['X3744'] == 2, scf1['X3742'], 0.)
sav4 = np.where(scf1['X3750'] == 2, scf1['X3748'], 0.)
sav5 = np.where(scf1['X3756'] == 2, scf1['X3754'], 0.)
sav6 = np.where(scf1['X3762'] == 2, scf1['X3760'], 0.)
spendaccts_notax = sav1 + sav2 + sav3 + sav4 + sav5 + sav6
spendaccts_tax = np.maximum(scf1['X3730'] + scf1['X3736'] +
                            scf1['X3742'] + scf1['X3748'] +
                            scf1['X3754'] + scf1['X3760'] -
                            spendaccts_notax, 0.)
# Other retirement savings accounts (401(k), 403(b), TSP, 457)
ret1 = np.where(scf1['X11001'] == 2, scf1['X11032'], 0.)
ret2 = np.where(scf1['X11101'] == 2, scf1['X11132'], 0.)
ret3 = np.where(scf1['X11301'] == 2, scf1['X11332'], 0.)
ret4 = np.where(scf1['X11401'] == 2, scf1['X11432'], 0.)
otherretaccts = np.maximum(ret1 + ret2 + ret3 + ret4, 0.)
# Total in savings accounts
totalinaccts = (rothira + ira + keogh + spendaccts_notax +
                spendaccts_tax + otherretaccts)
# Total in accounts taxed at withdrawal
totaltaxdistribution = ira + keogh + otherretaccts + spendaccts_tax
# Share of tax-preferred savings taxed at withdrawal/distribution
hpreferred0 = np.where(totalinaccts > 0, 1, 0)
disttaxshare0 = np.where(hpreferred0 == 1,
                        totaltaxdistribution / totalinaccts, 0.)

"""
Analyze cleaned SCF dataset
"""
# Get relevant measures from cleaned SCF data
age0 = np.array(scf2['age'])
wgt0 = np.array(scf2['wgt'])
equity0 = np.array(scf2['equity'])
hequity0 = np.array(scf2['hequity'])
lequity0 = np.where(hequity0 == 1, np.log(equity0), 0.)
deqshare0 = np.where(equity0 > 0, scf2['deq'] / equity0, 0.)
oassets0 = scf2['fin'] - equity0
hoassets0 = np.where(oassets0 > 0, 1, 0)
loassets0 = np.where(hoassets0 == 1, np.log(oassets0), 0.)

# Function to assign groups to individuals
def assignGroup(age, compinc, wgt):
    """
    This function takes in arrays for age, income and weight, and assigns units
    to groups. It returns an array with the group ID, which is the age category
    and the income category with an underscore between them.
    Current version:
        Assigns age groups using age of head
            0: age < 35
            1: 35 <= age < 45
            2: 45 <= age < 55
            3: 55 <= age < 65
            4: 65 <= age < 75
            5: age >= 75
        Assigns income groups using comparable income measure, nested in age
            0: compincome <= q20
            1: q20 < compincome <= q40
            2: q40 < compincome <= q60
            3: q60 < compincome <= q80
            4: q80 < compincome <= q90
            5: q90 < compincome <= q95
            6: q95 < compincome <= q99
            7: compincome > q99
    """
    # Assign age groups
    group_age0 = np.zeros(len(age))
    group_age1 = np.where(age >= 35, 1, group_age0)
    group_age2 = np.where(age >= 45, 2, group_age1)
    group_age3 = np.where(age >= 55, 3, group_age2)
    group_age4 = np.where(age >= 65, 4, group_age3)
    group_age5 = np.where(age >= 75, 5, group_age4)
    # Create comparable income measure
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
    return (np.array(groupid))

grpid0 = assignGroup(age0, compincome, wgt0)

# Tabulate results by group
grplist = np.unique(grpid0)
prob_stock = np.zeros(len(grplist))
m_equity = np.zeros(len(grplist))
deqshare = np.zeros(len(grplist))
prob_oassets = np.zeros(len(grplist))
m_oassets = np.zeros(len(grplist))
disttaxshare = np.zeros(len(grplist))
s_equity = np.zeros(len(grplist))
s_oassets = np.zeros(len(grplist))
for i in range(len(grplist)):
    g = grplist[i]
    wgtg = np.where(grpid0 == g, wgt0, 0.)
    prob_stock[i] = sum(hequity0 * wgtg) / sum(wgtg)
    m_equity[i] = sum(lequity0 * hequity0 * wgtg) / sum(hequity0 * wgtg)
    s_equity[i] = (sum((lequity0 - m_equity[i])**2 * hequity0 * wgtg) / sum(hequity0 * wgtg))**0.5
    deqshare[i] = sum(deqshare0 * hequity0 * wgtg) / sum(hequity0 * wgtg)
    prob_oassets[i] = sum(hoassets0 * wgtg) / sum(wgtg)
    m_oassets[i] = sum(loassets0 * hoassets0 * wgtg) / sum(hoassets0 * wgtg)
    s_oassets[i] = (sum((loassets0 - m_oassets[i])**2 * hoassets0 * wgtg) / sum(hoassets0 * wgtg))**0.5
    disttaxshare[i] = sum(disttaxshare0 * hpreferred0 * wgtg) / sum(hpreferred0 * wgtg)

# Combine into dataset
scf_results = pd.DataFrame({'groupid': grplist, 'prob_stock': prob_stock, 'm_equity': m_equity, 'deqshare': deqshare, 'prob_oassets': prob_oassets, 'm_oassets': m_oassets, 'disttaxshare': disttaxshare, 's_equity': s_equity, 's_oassets': s_oassets})
scf_results.to_csv('scf_results2.csv')


