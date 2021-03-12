# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 09:36:03 2018

@author: cody_
This file takes the growth results and produces tables for the dynamic 
distributional effects of the TCJA
"""
# Update the growth factors for tax-calculator
growthresults = pd.read_csv('intermediate_results/growdiffs.csv')
growfact_base = pd.read_csv(path_to_growfactors + 'growfactors.csv')
growfact_ref = copy.deepcopy(growfact_base)
growdiffs = np.concatenate(([0,0,0,0], np.array(growthresults['gfactors'])))
growfact_ref['ATXPY'] = growfact_base['ATXPY'] + growdiffs
growfact_ref['ASCHF'] = growfact_base['ASCHF'] + growdiffs
growfact_ref['ABOOK'] = growfact_base['ABOOK'] + growdiffs
growfact_ref['AWAGE'] = growfact_base['AWAGE'] + growdiffs
growfact_ref['ASCHCI'] = growfact_base['ASCHCI'] + growdiffs
growfact_ref['ASCHEI'] = growfact_base['ASCHEI'] + growdiffs
growfact_ref['AINTS'] = growfact_base['AINTS'] + growdiffs
growfact_ref['ADIVS'] = growfact_base['ADIVS'] + growdiffs
growfact_ref['ACGNS'] = growfact_base['ACGNS'] + growdiffs
growfact_ref['AUCOMP'] = growfact_base['AUCOMP'] + growdiffs
growfact_ref['AIPD'] = growfact_base['AIPD'] + growdiffs
growfact_ref['ATXPY'] = growfact_base['ATXPY'] + growdiffs
growfact_ref['ASCHCL'] = growfact_base['ASCHCL'] - growdiffs
growfact_ref['ASCHEL'] = growfact_base['ASCHEL'] + growdiffs
growfact_ref.to_csv(path_to_growfactors + 'growfactors2.csv', index=False)

def make_calculator2(refdict, year, gfactorname):
    """
    Thus is a special version of the make_calculator function that allows for
    alternative growth factors. It creates a calculator advanced to the given
    year and calculates tax results.
    Note: Passing an empty dictionary to refdict produces a current law 
    calculator.
    """
    assert year in range(2014, 2028)
    assert type(refdict) is dict
    growfactor = GrowFactors(path_to_growfactors + gfactorname)
    pol = Policy()
    beh = Behavior()
    rec = Records(puf_path, gfactors=growfactor)
    if refdict != {}:
        pol.implement_reform(refdict)
    calc1 = Calculator(pol, rec, beh)
    calc1.advance_to_year(year)
    calc1.calc_all()
    return calc1

calc_tcjaD = make_calculator2({}, 2018, 'growfactors2.csv')

# Static and dynamic comparison for each given year
for year in YEARLIST:
    static_table1 = applyBtaxDistribution(calc_pre, calc_tcja, year,
                                          equity, dshare, wtshare,
                                          nonprofit_split, slgov_split,
                                          RANKING, SCALING, EXCLUDING, SCREENING)
    dynamic_table1 = applyBtaxDistribution(calc_pre, calc_tcjaD, year,
                                           equity, dshare, wtshare,
                                           nonprofit_split, slgov_split,
                                           RANKING, SCALING, EXCLUDING, SCREENING)
    combined_table1 = static_table1.merge(dynamic_table1, on="Income group")
    combined_table1.to_csv('dynamic_tables/dynamicdist' + str(year) + '.csv')


