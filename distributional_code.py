# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 13:07:02 2018

@author: Cody Kallen

This file provides the code for the distributional analysis comparing 
any two sets of policies.
Note that this is not intended to be run on its own. It merely provides code
for use in any Tax-Calculator object. 

The distributional analysis functions here allow for various measures,
means of comparison, rankings, scalings, etc. 
        calc1: baseline calculator object for comparison
        calc2: reform calculator object
        nbin: number of groups
        income: measure of income to use for ranking and average rates
                Acceptable values:
                    "expanded": total income
                    "agi": income after exclusions
                    "aftertax": after-tax income under baseline
                    "nobenefits": total income less UI & SS benefits
        measure: variable whose change we want to measure,
                Acceptable values:
                    "filers": number of filers
                    "expanded_income": total income
                    "iitax": individual income tax liability
                    "payrolltax": payroll tax liability
                    "totaltax": iitax + payrolltax
                    "aftertax_income": expanded_income - totaltax
                    "avgtaxrate": totaltax / expanded_income
                    "margtaxrate" effective marginal tax rate
                    "avgnettaxrate": 1 - avgtaxrate
                    "margnettaxrate": 1 - margtaxrate
                    "fraczero": paying zero or negative income tax
                    "fraccut": receiving net tax cut
                    "frachike": receiving net tax hike
                    "fraccut100": receiving tax cut of at least $100
                    "frachike100": receiving tax hike of at least $100
                    "charity": total charitable contributions
                    "charity_after": charitable contributions after marginal
                                     subsidy
                    "state_taxes": State and local income/sales and property
                                   taxes less refunds
                    "benefits": consumption value of government benefits
                    "medicaid": Medicaid benefits (actuarial value)
                    "wages": wage and salary income
                    "wages_after": wage and salary income after marginal tax
        chtype: calculation of change
                Acceptable values:
                    "pch": % change from calc1 to calc2 (decimal)
                    "dch": average difference between calc1 and calc2 ($)
                    "tch": total difference between calc1 and calc2 ($billion)
                    "level1": average value in calc1 ($)
                    "level2": average value in calc2 ($)
                    "total1": total value in calc1 ($)
                    "total2": total value in calc2 ($)
        rerankby: measure by which to rerank filers by income
                Acceptable values:
                    None
                    "hhsize": household size (XTOT)
                    "hhsize_sqrt": square root of household size
                    "marital": 2 if married joint, 1 otherwise
        rescaleby: measure by which to rescale filers
                Acceptable values:
                    None
                    "hhsize"
                    "hhsize_sqrt"
                    "marital"
        exclude: those to exclude from the distributional analysis
                Note: this argument must be a list of strings
                Acceptable elements in list (if not empty):
                    "neginc": expanded_income < 0
                    "zeroinc": expanded_income == 0
                    "supertax": totaltax > expanded_income
        screen: those to include in the table
                Note: This measure allows for identifying changes within bins
                      without changing units' distributional positions. 
                      This argument must be a list of 2 strings
                Acceptable elements for screen[0] (filing status):
                    "": no restrictions by filing status
                    "single": single filing status
                    "head": head of household filing status
                    "married": married filing jointly
                    "married_sep": married filing separately
                    "not_joint": not married filing jointly
                    "not_sep": not married filing separately
                    "not_married"
                Acceptable elements for screen[1] (child status):
                    "": no restrictions by number of children
                    "0": no children under 18
                    "1": 1 child under 18
                    "2": 2 children under 18
                    "3+": 3 or more children under 18
                    "nonzero": at least one child under 18
"""

def getIncome(calc, income):
    """
    Returns the requested income measure.
    Acceptable values:
        "expanded": total income
        "aftertax": total income - total tax
        "agi": adjusted gross income
        "nobenefits": expanded income less government benefits
    """
    assert income in ["expanded", "agi", "aftertax", "market"]
    if income == "expanded":
        inc = calc.array('expanded_income')
    elif income == "agi":
        inc = calc.array('c00100')
    elif income == "aftertax":
        inc = calc.array('aftertax_income')
    elif income == "market":
        inc = (calc.array('expanded_income') - 
               calc.array('benefit_value_total') -
               calc.array('e00700'))
    return inc

def getMeasures(calc1, calc2, measure):
    """
    Returns the requested measures to be evaluated
    Acceptable values for measure:
        "filers": number of filers
        "expanded_income": total income
        "iitax": individual income tax liability
        "payrolltax": payroll tax liability
        "totaltax": iitax + payrolltax
        "aftertax_income": expanded_income - totaltax
        "avgtaxrate": totaltax / expanded_income
        "margtaxrate" effective marginal tax rate
        "avgnettaxrate": 1 - avgtaxrate
        "margnettaxrate": 1 - margtaxrate
        "fraczero": paying zero or negative income tax
        "fraccut": receiving net tax cut
        "frachike": receiving net tax hike
        "fraccut100": receiving tax cut of at least $100
        "frachike100": receiving tax hike of at least $100
        "charity": total charitable contributions
        "charity_after": charitable contributions after marginal subsidy
        "state_taxes": state and local income/sales and property taxes less
                       refunds
        "benefits": consumption value of government benefits
        "medicaid": Medical benefits (actuarial value)
        "wages": wage and salary income
        "wages_after": wage and salary income after marginal tax
    """
    assert measure in ["expanded_income", "iitax", "payrolltax",
                       "totaltax", "aftertax_income", "avgtaxrate",
                       "margtaxrate", "avgnettaxrate", "margnettaxrate",
                       "fraczero", "filers", "fraccut", "frachike",
                       "fraccut100", "frachike100", "charity", "charity_after",
                       "state_taxes", "benefits", "medicaid", 
                       "wages", "wages_after"]
    if measure == "expanded_income":
        var1 = calc1.array('expanded_income')
        var2 = calc2.array('expanded_income')
    elif measure == "iitax":
        var1 = calc1.array("iitax")
        var2 = calc2.array("iitax")
    elif measure == "payrolltax":
        var1 = calc1.array("payrolltax")
        var2 = calc2.array("payrolltax")
    elif measure == "totaltax":
        var1 = calc1.array("combined")
        var2 = calc2.array("combined")
    elif measure == "aftertax_income":
        var1 = calc1.array("aftertax_income")
        var2 = calc2.array("aftertax_income")
    elif measure == "avgtaxrate":
        var1 = np.divide(calc1.array("combined"),
                         calc1.array("expanded_income"),
                         where=(calc1.array("expanded_income")>0))
        var1 = np.where(np.abs(var1) > 1, np.sign(var1), var1)
        var2 = np.divide(calc2.array("combined"),
                         calc2.array("expanded_income"),
                         where=(calc2.array("expanded_income")>0))
    elif measure == "margtaxrate":
        var1 = calc1.mtr('e00200p')[2]
        var2 = calc2.mtr('e00200p')[2]
    elif measure == "avgnettaxrate":
        var1 = np.divide(calc1.array("aftertax_income"),
                         calc1.array("expanded_income"),
                         where=(calc1.array("expanded_income") != 0))
        var2 = np.divide(calc2.array("aftertax_income"),
                         calc2.array("expanded_income"),
                         where=(calc2.array("expanded_income") != 0))
    elif measure == "margnettaxrate":
        var1 = 1 - calc1.mtr("e00200p")[2]
        var2 = 1 - calc2.mtr("e00200p")[2]
    elif measure == "fraczero":
        var1 = np.where(calc1.array('iitax') <= 0, 1, 0)
        var2 = np.where(calc2.array('iitax') <= 0, 1, 0)
    elif measure == "filers":
        var1 = np.ones(len(calc1.array('s006')))
        var2 = np.ones(len(calc2.array('s006')))
    elif measure == "fraccut":
        var1 = np.ones(len(calc1.array('s006')))
        var2 = np.where(calc2.array('combined') - calc1.array('combined') < 0,
                        1, 0)
    elif measure == "frachike":
        var1 = np.ones(len(calc1.array('s006')))
        var2 = np.where(calc2.array('combined') - calc1.array('combined') > 0,
                        1, 0)
    elif measure == "fraccut":
        var1 = np.ones(len(calc1.array('s006')))
        var2 = np.where(calc2.array('combined') - calc1.array('combined') <
                        -100, 1, 0)
    elif measure == "fraccut":
        var1 = np.ones(len(calc1.array('s006')))
        var2 = np.where(calc2.array('combined') - calc1.array('combined') >
                        100, 1, 0)
    elif measure == "charity":
        cashgiving1 = calc1.array('e19800')
        cashgiving2 = calc2.array('e19800')
        noncashgiving1 = calc1.array('e20100')
        noncashgiving2 = calc2.array('e20100')
        var1 = cashgiving1 + noncashgiving1
        var2 = cashgiving2 + noncashgiving2
    elif measure == "charity_after":
        cashgiving1 = calc1.array('e19800')
        cashgiving2 = calc2.array('e19800')
        noncashgiving1 = calc1.array('e20100')
        noncashgiving2 = calc2.array('e20100')
        mtr_cash1 = calc1.mtr('e19800')[2]
        mtr_cash2 = calc2.mtr('e19800')[2]
        mtr_noncash1 = calc1.mtr('e20100')[2]
        mtr_noncash2 = calc2.mtr('e20100')[2]
        var1 = (cashgiving1 * (1 + mtr_cash1) +
                noncashgiving1 * (1 - mtr_noncash1))
        var2 = (cashgiving2 * (1 + mtr_cash2) +
                noncashgiving2 * (1 - mtr_noncash2))
    elif measure == "state_taxes":
        var1 = (calc1.array('e18400') + calc1.array('e18500') -
                calc1.array('e00700'))
        var2 = (calc2.array('e18400') + calc2.array('e18500') -
                calc2.array('e00700'))
    elif measure == "benefits":
        var1 = calc1.array('benefit_value_total')
        var2 = calc2.array('benefit_value_total')
    elif measure == "medicaid":
        var1 = calc1.array('mcaid_ben')
        var2 = calc2.array('mcaid_ben')
    elif measure == "wages":
        var1 = calc1.array('e00200')
        var2 = calc2.array('e00200')
    elif measure == "wages_after":
        wage1 = calc1.array('e00200')
        wage2 = calc2.array('e00200')
        mtr1 = calc1.mtr('e00200p')[2]
        mtr2 = calc2.mtr('e00200p')[2]
        var1 = wage1 * (1 - mtr1)
        var2 = wage2 * (1 - mtr2)
    return (var1, var2)

def getRankScale(calc1, rerankby, rescaleby):
    """
    Returns the requested reranking array and rescaling array
    rerankby and rescaleby are both dictionaries with entries for
        w_adult
        w_child
        elast_size
    """
    assert (rerankby['w_adult'] >= 0) and (rerankby['w_adult'] <= 1)
    assert (rerankby['w_child'] >= 0) and (rerankby['w_child'] <= 1)
    assert (rerankby['elast_size'] >= 0) and (rerankby['elast_size'] <= 1)
    assert (rescaleby['w_adult'] >= 0) and (rescaleby['w_adult'] <= 1)
    assert (rescaleby['w_child'] >= 0) and (rescaleby['w_child'] <= 1)
    assert (rescaleby['elast_size'] >= 0) and (rescaleby['elast_size'] <= 1)
    # Get relevant measures for each filer
    n_child = calc1.array('nu18')
    n_adult = calc1.array('XTOT') - n_child
    hhsize_rank = (1 + rerankby['w_adult'] * (n_adult - 1) +
                   rerankby['w_child'] * n_child)
    hhsize_scale = (1 + rescaleby['w_adult'] * (n_adult - 1) +
                    rescaleby['w_child'] * n_child)
    # Correct for filers with no adults (dependent children)
    hhsize_rank = np.where(hhsize_rank >= 1, hhsize_rank, 1)
    hhsize_scale = np.where(hhsize_scale >= 1, hhsize_scale, 1)
    # Apply elasticities
    rank = np.power(hhsize_rank, rerankby['elast_size'])
    scale = np.power(hhsize_scale, rescaleby['elast_size'])
    return (rank, scale)

def getExclude(calc, exclude, income='expanded'):
    """
    Returns an array of units to drop from the analysis
    Note: this argument must be a list of strings
    Acceptable elements in list (if not empty):
        "neginc": expanded_income < 0
        "zeroinc": expanded_income == 0
        "supertax": totaltax > expanded_income
        "bottom5": bottom 5% of income distribution
        "under5k": income under $5,000
        "under10k": income under $10,000
        "dependents": if filer is a dependent of others
        "separate": if filing married separate
    """
    assert type(exclude) == list
    inc = getIncome(calc, income)
    tax = calc.array('combined')
    # Figure out income distribution position
    wgt = calc.array('s006')
    inx = range(len(wgt))
    (inc1, wgt1, inx1) = zip(*sorted(zip(inc, wgt, inx)))
    cwgt1 = np.cumsum(wgt1) / sum(wgt1)
    (inx2, cwgt) = zip(*sorted(zip(inx1, cwgt1)))
    todrop = np.zeros(len(calc.array('s006')))
    if exclude != []:
        for ex in exclude:
            assert ex in ["neginc", "zeroinc", "supertax", "bottom5",
                          "under5k", "under10k", "dependents", "separate"]
            if ex == "neginc":
                todrop = np.where(inc < 0, 1, todrop)
            if ex == "zeroinc":
                todrop = np.where(inc == 0, 1, todrop)
            if ex == "supertax":
                todrop = np.where(tax > inc, 1, todrop)
            if ex == "bottom5":
                todrop = np.where(cwgt < 0.05, 1, todrop)
            if ex == "under5k":
                todrop = np.where(inc < 5000, 1, todrop)
            if ex == "under10k":
                todrop = np.where(inc < 10000, 1, todrop)
            if ex == "dependents":
                todrop = np.where(calc.array('XTOT') == 0, 1, todrop)
            if ex == "separate":
                todrop = np.where(calc.array('MARS') == 3, 1, todrop)
    return todrop

def getScreen(calc, screen):
    """
    Returns an array to units to include in the final analysis
    Note: this argument must be a list of 2 strings
    Acceptable elements for screen[0] (filing status):
        "": no restrictions by filing status
        "single": single filing status
        "head": head of household filing status
        "married": married filing jointly
        "married_sep": married filing separately
        "not_joint": not married filing jointly
        "not_sep": not married filing separately
        "not_married": not married
    Acceptable elements for screen[1] (child status):
        "": no restrictions by number of children
        "0": no children under 18
        "1": 1 child under 18
        "2": 2 children under 18
        "3+": 3 or more children under 18
        "nonzero": at least one child under 18
    """
    assert (type(screen) == list) and (len(screen) == 2)
    assert screen[0] in ["", "single", "head", "married", "married_sep",
                         "not_joint", "not_sep", "not_married"]
    assert screen[1] in ["", "0", "1", "2", "3+", "nonzero"]
    if screen[0] == "single":
        screen_status = np.where(calc.array('MARS') == 1, 1, 0)
    elif screen[0] == "head":
        screen_status = np.where(calc.array('MARS') == 4, 1, 0)
    elif screen[0] == "married":
        screen_status = np.where(calc.array('MARS') == 2, 1, 0)
    elif screen[0] == "married_sep":
        screen_status = np.where(calc.array('MARS') == 3, 1, 0)
    elif screen[0] == "not_joint":
        screen_status = np.where(calc.array('MARS') != 2, 1, 0)
    elif screen[0] == "not_sep":
        screen_status = np.where(calc.array('MARS') != 3, 1, 0)
    elif screen[0] == "not_married":
        notjoint = np.where(calc.array('MARS') != 2, 1, 0)
        notseparated = np.where(calc.array('MARS') != 3, 1, 0)
        screen_status = np.where(notjoint * notseparated, 1, 0)
    else:
        screen_status = np.ones(len(calc.array('MARS')))
    if screen[1] == "0":
        screen_child = np.where(calc.array('nu18') == 0, 1, 0)
    elif screen[1] == "1":
        screen_child = np.where(calc.array('nu18') == 1, 1, 0)
    elif screen[1] == "2":
        screen_child = np.where(calc.array('nu18') == 2, 1, 0)
    elif screen[1] == "3+":
        screen_child = np.where(calc.array('nu18') >= 3, 1, 0)
    elif screen[1] == "nonzero":
        screen_child = np.where(calc.array('nu18') > 0, 1, 0)
    else:
        screen_child = np.ones(len(calc.array('nu18')))
    screen2 = screen_status * screen_child
    return screen2
        
def distOrderPrep(calc1, calc2, income, measure, rerankby, rescaleby,
                  exclude, screen):
    """
    This function prepares all of the relevant measures. It performs the
    following tasks:
        - Removes observations per the "exclude" requirement
        - Orders the units by income measure, including reranking
        - Adjust the unit weights for scaling measure
        - Calculates the cumulative weight sum
        - Removes observations not include in the screen measure
    Returns a tuple of (inc, var1, var2, wgt, cumwgt)
    """
    ## Extract measures to use from calculators
    wgtA = calc1.array('s006')
    incA = getIncome(calc1, income)
    (var1A, var2A) = getMeasures(calc1, calc2, measure)
    (rankA, scaleA) = getRankScale(calc1, rerankby, rescaleby)
    todropA = getExclude(calc1, exclude, income)
    screenA = getScreen(calc1, screen)
    ## Rescale incomes and order units by income
    inc_rescaled= incA / rankA
    ziplist = sorted(zip(inc_rescaled, var1A, var2A, wgtA, rankA, scaleA,
                         screenA, todropA))
    (incB, var1B, var2B, wgtB, rankB, scaleB, screenB, todropB) = zip(*ziplist)
    ## Store as arrays and apply weights
    incC = np.array(incB) * np.array(rankB)
    wgtC = np.array(wgtB) * np.array(scaleB)
    var1C = np.array(var1B)
    var2C = np.array(var2B)
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
    var1E = var1C[screenC == 1]
    var2E = var2C[screenC == 1]
    return (incE, var1E, var2E, wgtE, cumwgtE)

def distTable_even(calc1, calc2, nbin, income, measure, chtype, rerankby,
                  rescaleby, exclude, screen):
    """
    Returns a list of the distributional analysis requested, using 
    evenly divided income groups (e.g. deciles). Last entry is for all 
    units (in screen)
    """
    ## Check input values not being passed to distOrderPrep function
    assert (type(nbin) == int) and (nbin > 0)
    assert chtype in ["dch", "pch", "tch", "level1", "level2", 
                      "total1", "total2"]
    # Pass inputs to be prepared for analysis
    (inc, var1, var2, wgt, cumwgt) = distOrderPrep(calc1, calc2, 
                                                   income, measure, rerankby,
                                                   rescaleby, exclude, screen)
    # Calculations within each group
    outcome = np.zeros(nbin + 1)
    for i in range(nbin):
        groupid = (cumwgt >= i / nbin) & (cumwgt < (i+1) / nbin)
        if chtype == "pch":
            outcome[i] = (sum(var2[groupid] * wgt[groupid]) /
                          sum(var1[groupid] * wgt[groupid]) - 1)
        elif chtype == "dch":
            outcome[i] = (sum((var2[groupid] - var1[groupid]) * wgt[groupid]) /
                          sum(wgt[groupid]))
        elif chtype == "tch":
            outcome[i] = sum((var2[groupid] - var1[groupid]) * wgt[groupid])
        elif chtype == "level1":
            outcome[i] = sum(var1[groupid] * wgt[groupid]) / sum(wgt[groupid])
        elif chtype == "level2":
            outcome[i] = sum(var2[groupid] * wgt[groupid]) / sum(wgt[groupid])
        elif chtype == "total1":
            outcome[i] = sum(var1[groupid] * wgt[groupid])
        elif chtype == "total2":
            outcome[i] = sum(var2[groupid] * wgt[groupid])
    # Calculations for total population
    if chtype == "pch":
        outcome[nbin] = sum(var2 * wgt) / sum(var1 * wgt) - 1
    elif chtype == "dch":
        outcome[nbin] = sum((var2 - var1) * wgt) / sum(wgt)
    elif chtype == "tch":
        outcome[nbin] = sum((var2 - var1) * wgt)
    elif chtype == "level1":
        outcome[nbin] = sum(var1 * wgt) / sum(wgt)
    elif chtype == "level2":
        outcome[nbin] = sum(var2 * wgt) / sum(wgt)
    elif chtype == "total1":
        outcome[nbin] = sum(var1 * wgt)
    elif chtype == "total2":
        outcome[nbin] = sum(var2 * wgt)
    return outcome

def distTable_uneven(calc1, calc2, income, measure, chtype, rerankby,
                     rescaleby, exclude, screen):
    """
    Returns a list of the uneven distributional analysis focusing on
    higher incomes. The entries in the list are, in order:
        - bottom quintile (x < q20)
        - second quintile (q20 <= x < q40)
        - third quintile (q40 <= x < q60)
        - fourth quintile (q60 <= x < q80)
        - next 10% (q80 <= x < q90)
        - next 5% (q90 <= x < q95)
        - next 4% (q95 <= x < q99)
        - top 1% (q99 <= x)
    """
    assert chtype in ["dch", "pch", "tch", "level1", "level2",
                      "total1", "total2"]
    # Pass inputs to be prepared for analysis
    (inc, var1, var2, wgt, cumwgt) = distOrderPrep(calc1, calc2, 
                                                   income, measure, rerankby,
                                                   rescaleby, exclude, screen)
    # Identify the bin for each observation
    groupid = np.zeros(len(inc))
    groupid = np.where(cumwgt >= 0.2, 1, groupid)
    groupid = np.where(cumwgt >= 0.4, 2, groupid)
    groupid = np.where(cumwgt >= 0.6, 3, groupid)
    groupid = np.where(cumwgt >= 0.8, 4, groupid)
    groupid = np.where(cumwgt >= 0.9, 5, groupid)
    groupid = np.where(cumwgt >= 0.95, 6, groupid)
    groupid = np.where(cumwgt >= 0.99, 7, groupid)
    groupid = np.where(cumwgt == 99, 99, groupid)
    outcome = np.zeros(9)
    for i in range(8):
        if chtype == "pch":
            outcome[i] = (sum(var2[groupid==i] * wgt[groupid==i]) /
                          sum(var1[groupid==i] * wgt[groupid==i]) - 1)
        elif chtype == "dch":
            outcome[i] = (sum((var2[groupid==i] - var1[groupid==i]) *
                              wgt[groupid==i]) / sum(wgt[groupid==i]))
        elif chtype == "tch":
            outcome[i] = (sum((var2[groupid==i] - var1[groupid==i]) *
                          wgt[groupid==i]))
        elif chtype == "level1":
            outcome[i] = (sum(var1[groupid==i] * wgt[groupid==i]) /
                          sum(wgt[groupid==i]))
        elif chtype == "level2":
            outcome[i] = (sum(var2[groupid==i] * wgt[groupid==i]) /
                          sum(wgt[groupid==i]))
        elif chtype == "total1":
            outcome[i] = sum(var1[groupid==i] * wgt[groupid==i])
        elif chtype == "total2":
            outcome[i] = sum(var2[groupid==i] * wgt[groupid==i])
    if chtype == "pch":
        outcome[8] = sum(var2 * wgt) / sum(var1 * wgt) - 1
    elif chtype == "dch":
        outcome[8] = sum((var2 - var1) * wgt) / sum(wgt)
    elif chtype == "tch":
        outcome[8] = sum((var2 - var1) * wgt)
    elif chtype == "level1":
        outcome[8] = sum(var1 * wgt) / sum(wgt)
    elif chtype == "level2":
        outcome[8] = sum(var2 * wgt) / sum(wgt)
    elif chtype == "total1":
        outcome[8] = sum(var1 * wgt)
    elif chtype== "total2":
        outcome[8] = sum(var2 * wgt)
    return outcome

def distTable_km(calc1, calc2, income, measure, chtype, rerankby,
                 rescaleby, exclude, screen):
    """
    Returns a list of the uneven distributional analysis focusing on
    higher incomes. The entries in the list are, in order:
        - bottom decile (x < q10)
        - second decile (q10 <= x < q10)
        - third decile (q20 <= x < q30)
        - fourth decile (q30 <= x < q40)
        - fifth decile (q40 <= x < q50)
        - sixth decile (q50 <= x < q60)
        - seventh decile (q60 <= x < q70)
        - eighth decile (q70 <= x < q80)
        - ninth decile (q80 <= x < q90)
        - next 5% (q90 <= x < q95)
        - next 4% (q95 <= x < q99)
        - top 1% (q99 <= x)
    """
    assert chtype in ["dch", "pch", "tch", "level1", "level2",
                      "total1", "total2"]
    # Pass inputs to be prepared for analysis
    (inc, var1, var2, wgt, cumwgt) = distOrderPrep(calc1, calc2, 
                                                   income, measure, rerankby,
                                                   rescaleby, exclude, screen)
    # Identify the bin for each observation
    groupid = np.zeros(len(inc)) # bottom decile
    groupid = np.where(cumwgt >= 0.1, 1, groupid) # second decile
    groupid = np.where(cumwgt >= 0.2, 2, groupid) # third decile
    groupid = np.where(cumwgt >= 0.3, 3, groupid) # fourth decile
    groupid = np.where(cumwgt >= 0.4, 4, groupid) # fifth decile
    groupid = np.where(cumwgt >= 0.5, 5, groupid) # sixth decile
    groupid = np.where(cumwgt >= 0.6, 6, groupid) # seventh decile
    groupid = np.where(cumwgt >= 0.7, 7, groupid) # eighth decile
    groupid = np.where(cumwgt >= 0.8, 8, groupid) # ninth decile
    groupid = np.where(cumwgt >= 0.9, 9, groupid) # 90-95
    groupid = np.where(cumwgt >= 0.95, 10, groupid) # 95-99
    groupid = np.where(cumwgt >= 0.99, 11, groupid) # top 1%
    groupid = np.where(cumwgt == 99, 99, groupid) # excluded individuals
    outcome = np.zeros(13)
    for i in range(12):
        if chtype == "pch":
            outcome[i] = (sum(var2[groupid==i] * wgt[groupid==i]) /
                          sum(var1[groupid==i] * wgt[groupid==i]) - 1)
        elif chtype == "dch":
            outcome[i] = (sum((var2[groupid==i] - var1[groupid==i]) *
                              wgt[groupid==i]) / sum(wgt[groupid==i]))
        elif chtype == "tch":
            outcome[i] = (sum((var2[groupid==i] - var1[groupid==i]) *
                          wgt[groupid==i]))
        elif chtype == "level1":
            outcome[i] = (sum(var1[groupid==i] * wgt[groupid==i]) /
                          sum(wgt[groupid==i]))
        elif chtype == "level2":
            outcome[i] = (sum(var2[groupid==i] * wgt[groupid==i]) /
                          sum(wgt[groupid==i]))
        elif chtype == "total1":
            outcome[i] = sum(var1[groupid==i] * wgt[groupid==i])
        elif chtype == "total2":
            outcome[i] = sum(var2[groupid==i] * wgt[groupid==i])
    if chtype == "pch":
        outcome[12] = sum(var2 * wgt) / sum(var1 * wgt) - 1
    elif chtype == "dch":
        outcome[12] = sum((var2 - var1) * wgt) / sum(wgt)
    elif chtype == "tch":
        outcome[12] = sum((var2 - var1) * wgt)
    elif chtype == "level1":
        outcome[12] = sum(var1 * wgt) / sum(wgt)
    elif chtype == "level2":
        outcome[12] = sum(var2 * wgt) / sum(wgt)
    elif chtype == "total1":
        outcome[12] = sum(var1 * wgt)
    elif chtype== "total2":
        outcome[12] = sum(var2 * wgt)
    return outcome

def kakwani(calc1, calc2, income, measure, rerankby, rescaleby, exclude):
    """
    Calculates the Kakwani index for the change from calc1 to calc2.
    measure is restricted to "iitax", "payrolltax", "totaltax"
    Restricts screening to none
    """
    assert measure in ["iitax", "payrolltax", "totaltax"]
    (inc, var1, var2, wgt, cumwgt) = distOrderPrep(calc1, calc2, income,
                                                   measure, rerankby,
                                                   rescaleby, exclude,
                                                   ["", ""])
    # Drop those to be excluded
    inc1 = inc[cumwgt < 99]
    wgt1 = wgt[cumwgt < 99]
    varch1 = var2[cumwgt < 99] - var1[cumwgt < 99]
    # Cumulative measures by person and totals
    Cumwgt = np.cumsum(wgt1)
    Cumvar = np.cumsum(varch1 * wgt1)
    Cuminc = np.cumsum(inc1 * wgt1)
    Totwgt = sum(wgt1)
    Totvar = sum(varch1 * wgt1)
    Totinc = sum(inc1 * wgt1)
    income_ineq = sum((Cumwgt / Totwgt - Cuminc / Totinc) * wgt1 / Totwgt) * 2
    tax_ineq = sum((Cumwgt / Totwgt - Cumvar / Totvar) * wgt1 / Totwgt) * 2
    kak = (tax_ineq - income_ineq) * np.sign(Totvar)
    return kak

def levelTable_km(calc1, calc2, rerankby, rescaleby, exclude, screen):
    """
    Builds the Kallen-Mathur distributional table for levels, pre and post.
    Measures:
        Average tax rates
        Share of income and payroll tax liability
        Share with no II tax liability
    Returns a pandas DataFrame table
    """
    totaltax_pre = distTable_km(calc1, calc2, 'expanded',
                                'totaltax', 'total1', 
                                rerankby, rescaleby, exclude, screen)
    totaltax_post = distTable_km(calc1, calc2, 'expanded',
                                 'totaltax', 'total2', 
                                 rerankby, rescaleby, exclude, screen)
    totalinc_pre = distTable_km(calc1, calc2, 'expanded',
                                'expanded_income', 'total1',
                                rerankby, rescaleby, exclude, screen)
    totalinc_post = distTable_km(calc1, calc2, 'expanded',
                                 'expanded_income', 'total2',
                                 rerankby, rescaleby, exclude, screen)
    fraczero_pre = distTable_km(calc1, calc2, 'expanded',
                                'fraczero', 'level1',
                                rerankby, rescaleby, exclude, screen) * 100
    fraczero_post = distTable_km(calc1, calc2, 'expanded',
                                 'fraczero', 'level2',
                                 rerankby, rescaleby, exclude, screen) * 100
    # Produce desired measures
    avgrate_pre = totaltax_pre / totalinc_pre * 100
    avgrate_post = totaltax_post / totalinc_post * 100
    taxshare_pre = totaltax_pre / totaltax_pre[-1] * 100
    taxshare_post = totaltax_post / totaltax_post[-1] * 100
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile',
                'Fourth decile', 'Fifth decile', 'Sixth decile',
                'Seventh decile', 'Eighth decile', 'Ninth decile',
                'Next 5%', 'Next 4%', 'Top 1%', 'All units']
    table1 = pd.DataFrame({"Income group": rowlabel,
                           "Avg tax rate, pre (%)": avgrate_pre,
                           "Avg tax rate, post (%)": avgrate_post,
                           "Share of tax liability, pre (%)": taxshare_pre, 
                           "Share of tax liability, post (%)": taxshare_post,
                           "No II tax liability, pre (%)": fraczero_pre,
                           "No II tax liability, post (%)":fraczero_post})
    return table1

def changeTable_km(calc1, calc2, rerankby, rescaleby, exclude, screen):
    """
    Builds the Kallen-Mathur distributional table for changes.
    Measures:
        Change in after-tax income
        Dollar change in tax liability
        Share of the tax change
        Share receiving tax cut
        Share receiving tax hike
    """
    totaltax_pre = distTable_km(calc1, calc2, 'expanded',
                                'totaltax', 'total1',
                                rerankby, rescaleby, exclude, screen)
    totaltax_post = distTable_km(calc1, calc2, 'expanded',
                                 'totaltax', 'total2',
                                 rerankby, rescaleby, exclude, screen)
    totalinc_pre = distTable_km(calc1, calc2, 'expanded',
                                'expanded_income', 'total1',
                                rerankby, rescaleby, exclude, screen)
    totalinc_post = distTable_km(calc1, calc2, 'expanded',
                                 'expanded_income', 'total2',
                                 rerankby, rescaleby, exclude, screen)
    tax_ch = distTable_km(calc1, calc2, 'expanded',
                          'totaltax', 'dch',
                          rerankby, rescaleby, exclude, screen)
    totalchange = distTable_km(calc1, calc2, 'expanded',
                               'totaltax', 'tch',
                               rerankby, rescaleby, exclude, screen)
    taxhike = distTable_km(calc1, calc2, 'expanded',
                           'frachike', 'level2',
                           rerankby, rescaleby, exclude, screen) * 100
    taxcut = distTable_km(calc1, calc2, 'expanded',
                          'fraccut', 'level2',
                          rerankby, rescaleby, exclude, screen) * 100
    aftertax_pch = ((totalinc_post - totaltax_post) /
                    (totalinc_pre - totaltax_pre) - 1) * 100
    change_share = totalchange / totalchange[-1] * 100
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile',
                'Fourth decile', 'Fifth decile', 'Sixth decile',
                'Seventh decile', 'Eighth decile', 'Ninth decile',
                'Next 5%', 'Next 4%', 'Top 1%', 'All units']
    table1 = pd.DataFrame({"Income group": rowlabel,
                           "Change in after-tax income (%)": aftertax_pch,
                           "Average tax change ($)": tax_ch,
                           "Share of the tax change (%)": change_share,
                           "Share receiving tax cut (%)": taxcut,
                           "Share receiving tax hike (%)": taxhike})
    return table1

def demogTable_km(calc1, calc2, exclude, screen):
    """
    Builds the Kallen-Mathur distributional table for specific demographic 
    groups.
    Measures:
        Average tax rate, pre
        Average tax rate, post
        Dollar change in tax liability
        Percent change in after-tax income
    """
    rankscale = {"w_adult": 1, "w_child": 1, "elast_size": 0}
    totaltax_pre = distTable_km(calc1, calc2, 'expanded',
                                'totaltax', 'total1',
                                rankscale, rankscale, exclude, screen)
    totaltax_post = distTable_km(calc1, calc2, 'expanded',
                                 'totaltax', 'total2',
                                 rankscale, rankscale, exclude, screen)
    totalinc_pre = distTable_km(calc1, calc2, 'expanded', 
                                'expanded_income', 'total1',
                                rankscale, rankscale, exclude, screen)
    totalinc_post = distTable_km(calc1, calc2, 'expanded',
                                 'expanded_income', 'total2',
                                 rankscale, rankscale, exclude, screen)
    tax_ch = distTable_km(calc1, calc2, 'expanded',
                          'totaltax', 'dch',
                          rankscale, rankscale, exclude, screen)
    nfilers = distTable_km(calc1, calc2, 'expanded',
                           'filers', 'total1',
                           rankscale, rankscale, exclude, screen)
    rowlabel = ['Bottom decile', 'Second decile', 'Third decile',
                'Fourth decile', 'Fifth decile', 'Sixth decile',
                'Seventh decile', 'Eighth decile', 'Ninth decile',
                'Next 5%', 'Next 4%', 'Top 1%', 'All units']
    avgrate_pre = totaltax_pre / totalinc_pre * 100
    avgrate_post = totaltax_post / totalinc_post * 100
    table1 = pd.DataFrame({"Income group": rowlabel,
                           "Percent of filers": nfilers / nfilers[-1] * 100,
                           "Avg tax rate, pre (%)": avgrate_pre,
                           "Avg tax rate, post (%)": avgrate_post,
                           "Average tax change ($)": tax_ch})
    return table1

