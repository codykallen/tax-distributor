# -*- coding: utf-8 -*-
"""
The following file provides the code for the distributional analysis of 
the corporate income tax. This assumes several things have already been 
specified:
    distTable_km: (func) function for distributional analysis
    calc_pre: (calc) Calculator object, pre-TCJA law
    calc_tcja: (calc): Calculator object, TCJA law
It then splits the burden between several different groups, and distributes
accordingly:
    Federal government: not distributed
    Rest of the world: not distributed
    State and local governments: slgDistribution()
    Nonprofit organizations: npDistribution()
    Households: hhEquityDistribution()
Note: This requires that you have already compiled the following files:
    distributional_code.py
    equity_imputation_code.py
"""
import numpy as np
import pandas as pd
import copy
# Decrease in corporate tax liabilities for each year 2018-2027
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
hhshare = 0.668920896
npshare = 0.047345087
fedshare = 0.001261413
slgshare = 0.085778364
rowshare = 0.196694239

def npDistribution(calc1, ctaxch, split):
    """
    This function produces an estimate of how much incomes change based on the
    change in corporate equity income to nonprofits.
    Note that the year should be the same for calc1 and ctaxch.
    Inputs:
        ctaxch: the change in corporate tax liability ($)
            Note: ctaxch should be positive for a tax hike, and negative for a tax cut
        split: dict of how to allocate the burden:
            "services": reduce services using distribution of benefit_value_total
            "compensation": reduce compensation using distribution of e00200
            "donors": reduce compensation using distribution of e19800 + e20100
            "foreign": reduce provision of foreign aid
    Returns a tuple of the changes  to be added to:
        mcare_ben: for nontaxable services
        e00200p: for compensation
        e19800: for charitable giving
    """
    assert (split['services'] + split['compensation'] + split['donors'] +
            split['foreign'] == 1.0)
    assert (min(split['services'], split['compensation'], split['donors'],
                split['foreign']) >= 0)
    # Calculate total change in each category, excluding foreign aid
    totch_services = -ctaxch * npshare * split['services']
    totch_comp = -ctaxch * npshare * split['compensation']
    totch_giving = -ctaxch * npshare * split['donors']
    # Actual amounts in Tax-Calculator
    services = calc1.array('benefit_value_total')
    comp = calc1.array('e00200')
    giving = calc1.array('e19800') + calc1.array('e20100')
    wgt = calc1.array('s006')
    # Distribute to each type
    services_ch = totch_services * services / sum(services * wgt)
    comp_ch = totch_comp * comp / sum(comp * wgt)
    giving_ch = totch_giving * giving / sum(giving * wgt)
    return (services_ch, comp_ch, giving_ch)

def slgDistribution(calc1, ctaxch, split):
    """
    This function produces an estimate of how much incomes change based on the
    change in corporate equity income to state and local governments.
    Note that the year should be the same for calc1 and ctaxch.
    Inputs:
        ctaxch: the change in corporate tax liability ($)
            Note: ctaxch should be positive for a tax hike, and negative for a tax cut
        split: dict of how to allocate the burden:
            "benefits": reduce spending proportional to government benefits
            "compensation": reduce compensation using distribution of e00200
            "taxes": raise taxes, using e18400 + e18500 - e00700
    Returns a tuple of the changes  to be added to:
        mcaid_ben: for nontaxable services
        e00200p: for compensation
        e18400: for taxes
    """
    assert split["benefits"] + split["compensation"] + split["taxes"] == 1.
    assert min(split["benefits"], split["compensation"], split["taxes"]) >= 0
    totch_benefits = -ctaxch * slgshare * split["benefits"]
    totch_comp = -ctaxch * slgshare * split["compensation"]
    totch_tax = -ctaxch * slgshare * split["taxes"]
    benefits = calc1.array('benefit_value_total')
    comp = calc1.array('e00200')
    taxes = calc1.array('e18400') + calc1.array('e18500') - calc1.array('e00700')
    wgt = calc1.array('s006')
    benefits_ch = totch_benefits * benefits / sum(benefits * wgt)
    comp_ch = totch_comp * comp / sum(comp * wgt)
    taxes_ch = totch_tax * taxes / sum(taxes * wgt)
    return (benefits_ch, comp_ch, taxes_ch)

divshare = 0.44
cgsplit = [0.034, 0.496]
def hhEquityDistribution(calc1, equity, dshare, wtshare, ctaxch):
    """
    This function produces an estimate of how much incomes change base on the
    change in corporate equity income to households. This includes separate
    splits for different types of income. 
    Inputs:
        equity: imputed total equity amount for each person
        dshare: direct equity share for each person
        wtshare: share of indirect equity taxable at withdrawal per person
        ctaxch: change in corporate tax liability ($)
            Note: ctaxch should be positive for a tax hike, and negative for a tax cut
    Note that the year should be the same for calc1, equity and ctaxch.
    Process:
        The corporate tax change is allocated proportional to equity.
        The burden is then split between the direct and indirect shares.
        Direct share: split between dividends and capital gains.
            Dividends: split between qualified and nonqualified
            Capital gains: split between short-term, long-term and unrealized
        Indirect share: split between taxed and withdrawal and not
    Returns a type of the changes to be added to:
        e00650: qualified dividends
        e00600: total dividends
        p22250: short-term gains
        p23250: long-term gains
        e01400: taxable IRA distributions
            Note that this will be for the taxed windfall for indirect equity
        e00400: nontaxable interest income
            Note that this is for all equity not subject to tax:
                Unrealized capital gains
                Equity in accounts not taxed at withdrawal
    """
    wgt = calc1.array('s006')
    assert len(equity) == len(wgt)
    assert len(dshare) == len(wgt)
    assert len(wtshare) == len(wgt)
    assert divshare >= 0
    assert divshare <= 1
    assert len(cgsplit) == 2
    assert min(cgsplit) >= 0
    assert sum(cgsplit) <= 1
    ctax_tot = -ctaxch * hhshare * equity / sum(equity * wgt)
    # Direct tax burden
    ctax_direct = ctax_tot * dshare
    # Tax burden on dividend income
    qdiv = calc1.array('e00650')
    tdiv = calc1.array('e00600')
    qdivshare = sum(qdiv * calc1.array('s006')) / sum(tdiv * calc1.array('s006'))
    divsplit = np.where(tdiv > 0, qdiv / (tdiv + 0.00001), qdivshare)
    ctax_qdiv = (ctax_direct * divshare * divsplit)
    ctax_nqdiv = (ctax_direct * divshare * (1 - divsplit))
    # Tax burden on capital gains
    ctax_stcg = ctax_direct * (1 - divshare) * cgsplit[0]
    ctax_ltcg = ctax_direct * (1 - divshare) * cgsplit[1]
    ctax_urcg = ctax_direct * (1 - divshare) * (1 - cgsplit[0] - cgsplit[1])
    # Indirect tax burden
    ctax_wt = ctax_tot * (1 - dshare) * wtshare
    ctax_wnt = ctax_tot * (1 - dshare) * (1 - wtshare)
    return (ctax_qdiv, ctax_qdiv + ctax_nqdiv,
            ctax_stcg, ctax_ltcg, ctax_wt, ctax_urcg + ctax_wnt)

def applyBtaxDistribution(calcA, calcB, year, equity, dshare, wtshare,
                          npsplit, slgsplit,
                          rerankby, rescaleby, exclude, screen):
    """
    This function applies the distributional analysis using information in
    calcA and making changes to calcB. It only operates for the given year.
    The equity imputation must be for 2016. 
    Returns a DataFrame object with income groups, the percent change in
    after-tax income, and the dollar change in after-tax income.
    """
    # Advance inputs to the year requested
    assert year in range(2018, 2028)
    calc1 = copy.deepcopy(calcA)
    calc1.advance_to_year(year)
    calc1.calc_all()
    calc2 = copy.deepcopy(calcB)
    calc2.advance_to_year(year)
    calc2.calc_all()
    equity2 = advanceEquity(equity, year)
    ctaxchange = ctaxrev[str(year)]
    # Obtain changes for nonprofit response
    (ben_ch1, comp_ch1, giving_ch1) = npDistribution(calc1, ctaxchange, npsplit)
    (ben_ch2, comp_ch2, taxes_ch2) = slgDistribution(calc1, ctaxchange, slgsplit)
    (qdiv_ch3, tdiv_ch3,
     stcg_ch3, ltcg_ch3,
     tira_ch3, free_ch3) = hhEquityDistribution(calc1, equity2, dshare,
                                                wtshare, ctaxchange)
    # Update incomes in calc2
    calc2.incarray('mcaid_ben', np.array(ben_ch1 + ben_ch2))
    calc2.incarray('e00200p', np.array(comp_ch1 + comp_ch2))
    calc2.incarray('e00200', np.array(comp_ch1 + comp_ch2))
    calc2.incarray('e19800', np.array(giving_ch1))
    calc2.incarray('e18400', np.array(taxes_ch2))
    calc2.incarray('e00650', np.array(qdiv_ch3))
    calc2.incarray('e00600', np.array(tdiv_ch3))
    calc2.incarray('p22250', np.array(stcg_ch3))
    calc2.incarray('p23250', np.array(ltcg_ch3))
    calc2.incarray('e01400', np.array(tira_ch3))
    calc2.incarray('e00400', np.array(free_ch3))
    calc2.calc_all()
    # Produce the distributional comparison
    pchange = distTable_km(calc1, calc2, 'expanded', 'aftertax_income', "pch",
                           rerankby, rescaleby, exclude, screen)
    dchange = distTable_km(calc1, calc2, 'expanded', 'aftertax_income', "dch",
                           rerankby, rescaleby, exclude, screen)
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile',
                'Fourth decile', 'Fifth decile', 'Sixth decile',
                'Seventh decile', 'Eighth decile', 'Ninth decile',
                'Next 5%', 'Next 4%', 'Top 1%', 'All units']
    table1 = pd.DataFrame({"Income group": rowlabel,
                           "Percent": pchange,
                           "Average ($)": dchange})
    totalchange = sum((ben_ch1 + comp_ch1 + giving_ch1 +
                       ben_ch2 + comp_ch2 + taxes_ch2 +
                       tdiv_ch3 + stcg_ch3 + ltcg_ch3 +
                       tira_ch3 + free_ch3) * calc1.array('s006'))
    #print("Change in corporate tax liability: " + str(ctaxchange / 10**9))
    #print("Change in pre-tax income: " + str(totalchange / 10**9))
    aft1 = calc1.array('aftertax_income')
    aft2 = calc2.array('aftertax_income')
    wgt = calc1.array('s006')
    #print("Change in after-tax income: " + str(sum((aft2 - aft1) * wgt) / 10**9))
    return table1

def fullDistComparison(calcA, calcB, year, equity, dshare, wtshare,
                       npsplit, slgsplit,
                       rerankby, rescaleby, exclude, screen):
    """
    This function produces a table combining 3 version of the one produced b
    applyBtaxDistribution. The three components are:
        Individual income tax cuts without corporate tax cuts
        Corporate tax cuts without individual income tax cuts
        Individual and corporate tax cuts
    """
    calc1 = copy.deepcopy(calcA)
    calc2 = copy.deepcopy(calcB)
    calc1.advance_to_year(year)
    calc1.calc_all()
    calc2.advance_to_year(year)
    calc2.calc_all()
    pchange_iit = distTable_km(calc1, calc2, 'expanded', 'aftertax_income',
                               'pch', rerankby, rescaleby, exclude, screen)
    dchange_iit = distTable_km(calc1, calc2, 'expanded', 'aftertax_income',
                               'dch', rerankby, rescaleby, exclude, screen)
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile',
                'Fourth decile', 'Fifth decile', 'Sixth decile',
                'Seventh decile', 'Eighth decile', 'Ninth decile',
                'Next 5%', 'Next 4%', 'Top 1%', 'All units']
    iit_table = pd.DataFrame({"Income groups": rowlabel,
                              "IIT, percent": pchange_iit,
                              "IIT, average": dchange_iit})
    cit_table = applyBtaxDistribution(calcA, calcA, year, equity, dshare,
                                      wtshare, npsplit, slgsplit, rerankby,
                                      rescaleby, exclude, screen)
    all_table = applyBtaxDistribution(calcA, calcB, year, equity, dshare,
                                      wtshare, npsplit, slgsplit, rerankby,
                                      rescaleby, exclude, screen)
    iit_table["CIT, percent"] = cit_table["Percent"]
    iit_table["CIT, average"] = cit_table["Average ($)"]
    iit_table["Both, percent"] = all_table["Percent"]
    iit_table["Both, average"] = all_table["Average ($)"]
    return iit_table


    
        


