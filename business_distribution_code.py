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

def npDistribution(calc1, ctaxch, split):
    """
    This function produces an estimate of how much incomes change based on the
    change in corporate equity income to nonprofits.
    Note that the year should be the same for calc1 and ctaxch.
    Inputs:
        ctaxch: the change in corporate tax liability ($)
            Note: ctaxch should be positive for a tax hike, 
                  and negative for a tax cut
        split: dict of how to allocate the burden:
            "services": reduce services using distribution of 
                        benefit_value_total
            "compensation": reduce compensation using distribution of e00200
            "donors": reduce compensation using distribution of 
                      e19800 + e20100
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
            Note: ctaxch should be positive for a tax hike, 
                  and negative for a tax cut
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
    taxes = (calc1.array('e18400') + calc1.array('e18500') -
             calc1.array('e00700'))
    wgt = calc1.array('s006')
    benefits_ch = totch_benefits * benefits / sum(benefits * wgt)
    comp_ch = totch_comp * comp / sum(comp * wgt)
    taxes_ch = totch_tax * taxes / sum(taxes * wgt)
    return (benefits_ch, comp_ch, taxes_ch)

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
            Note: ctaxch should be positive for a tax hike, 
                  and negative for a tax cut
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
        e00400: nontaxable interest income
            Note that this is for all equity not subject to tax:
                Unrealized capital gains
                Equity in accounts not taxed at withdrawal
                Equity in accounts taxed at withdrawal, after withdrawal tax
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
    qdivshare = (sum(qdiv * calc1.array('s006')) /
                 sum(tdiv * calc1.array('s006')))
    divsplit = np.where(tdiv > 0, qdiv / (tdiv + 0.00001), qdivshare)
    ctax_qdiv = (ctax_direct * divshare * divsplit)
    ctax_nqdiv = (ctax_direct * divshare * (1 - divsplit))
    # Tax burden on capital gains
    ctax_stcg = ctax_direct * (1 - divshare) * cgsplit[0]
    ctax_ltcg = ctax_direct * (1 - divshare) * cgsplit[1]
    ctax_urcg = ctax_direct * (1 - divshare) * (1 - cgsplit[0] - cgsplit[1])
    # Indirect tax burden
    mtr_ira = sum(calc1.mtr('e01400',calc_all_already_called=True)[2] *
                  calc1.array('e01400') * wgt) / sum(calc1.array('e01400') * wgt)
    ctax_wt = ctax_tot * (1 - dshare) * wtshare * (1 - mtr_ira)
    ctax_wnt = ctax_tot * (1 - dshare) * (1 - wtshare)
    return (ctax_qdiv, ctax_qdiv + ctax_nqdiv,
            ctax_stcg, ctax_ltcg, ctax_wt + ctax_urcg + ctax_wnt)

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
    (ben_ch1, comp_ch1, giving_ch1) = npDistribution(calc1, ctaxchange,
                                                     npsplit)
    (ben_ch2, comp_ch2, taxes_ch2) = slgDistribution(calc1, ctaxchange,
                                                     slgsplit)
    (qdiv_ch3, tdiv_ch3,
     stcg_ch3, ltcg_ch3,
     free_ch3) = hhEquityDistribution(calc1, equity2, dshare,
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
    #calc2.incarray('e01400', np.array(tira_ch3))
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


def equityDistribution(eq, deqsh, calc1, rerankby, rescaleby,
                       exclude, screen):
    """
    Function to build distribution table for
    equity, directly held equity, dividends,
    and dividends + capital gains.
    Returns distribution table.
    """
    # Arrays of measures to use
    equityA = np.array(eq)
    dequityA = np.array(deqsh) * equityA
    divA = calc1.array('e00600')
    divcgA = divA + calc1.array('p22250') + calc1.array('p23250')
    # Arrays of measures for sorting
    incA = getIncome(calc1, 'expanded')
    wgtA = calc1.array('s006')
    (rankA, scaleA) = getRankScale(calc1, rerankby, rescaleby)
    todropA = getExclude(calc1, exclude, 'expanded')
    screenA = getScreen(calc1, screen)
    ## Rescale incomes and order units by income
    inc_rescaled= incA / rankA
    ziplist = sorted(zip(inc_rescaled, equityA, dequityA, divA, divcgA,
                         wgtA, rankA, scaleA, screenA, todropA))
    (incB, equityB, dequityB, divB, divcgB, wgtB, rankB, scaleB, screenB, todropB) = zip(*ziplist)
    ## Store as arrays and apply weights
    incC = np.array(incB) * np.array(rankB)
    wgtC = np.array(wgtB) * np.array(scaleB)
    equityC = np.array(equityB)
    dequityC = np.array(dequityB)
    divC = np.array(divB)
    divcgC = np.array(divcgB)
    screenC = np.array(screenB)
    todropC = np.array(todropB)
    # Remove excluded units and calculate cumulative weight of others
    wgtD = np.where(todropC == 1, 0, wgtC)
    cumwgtD = np.cumsum(wgtD) / sum(wgtD)
    cumwgtD = np.where(todropC == 1, 99, cumwgtD)
    # Retain cumulative weights but drop observations not included in screen
    incE = incC[screenC == 1]
    wgtE = wgtC[screenC == 1]
    cumwgtE = cumwgtD[screenC == 1]
    equityE = equityC[screenC == 1]
    dequityE = dequityC[screenC == 1]
    divE = divC[screenC == 1]
    divcgE = divcgC[screenC == 1]
    # Identify the bin for each observation
    groupid = np.zeros(len(incE)) # bottom decile
    groupid = np.where(cumwgtE >= 0.1, 1, groupid) # second decile
    groupid = np.where(cumwgtE >= 0.2, 2, groupid) # third decile
    groupid = np.where(cumwgtE >= 0.3, 3, groupid) # fourth decile
    groupid = np.where(cumwgtE >= 0.4, 4, groupid) # fifth decile
    groupid = np.where(cumwgtE >= 0.5, 5, groupid) # sixth decile
    groupid = np.where(cumwgtE >= 0.6, 6, groupid) # seventh decile
    groupid = np.where(cumwgtE >= 0.7, 7, groupid) # eighth decile
    groupid = np.where(cumwgtE >= 0.8, 8, groupid) # ninth decile
    groupid = np.where(cumwgtE >= 0.9, 9, groupid) # 90-95
    groupid = np.where(cumwgtE >= 0.95, 10, groupid) # 95-99
    groupid = np.where(cumwgtE >= 0.99, 11, groupid) # top 1%
    groupid = np.where(cumwgtE == 99, 99, groupid) # excluded individuals
    # Arrays to store shares
    equityF = np.zeros(12)
    dequityF = np.zeros(12)
    divF = np.zeros(12)
    divcgF = np.zeros(12)
    # Compute shares for each income group
    for i in range(12):
        equityF[i] = sum(equityE[groupid==i] * wgtE[groupid==i]) / sum(equityE * wgtE)
        dequityF[i] = sum(dequityE[groupid==i] * wgtE[groupid==i]) / sum(dequityE * wgtE)
        divF[i] = sum(divE[groupid==i] * wgtE[groupid==i]) / sum(divE * wgtE)
        divcgF[i] = sum(divcgE[groupid==i] * wgtE[groupid==i]) / sum(divcgE * wgtE)
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile',
                'Fifth decile', 'Sixth decile', 'Seventh decile', 'Eighth decile',
                'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%']
    table1 = pd.DataFrame({"Income group": rowlabel,
                           "Equity": equityF, "Direct equity": dequityF,
                           "Dividends": divF, "Dividends + CapGains": divcgF})
    return table1