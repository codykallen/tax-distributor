# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:57:09 2018

@author: cody_
Distribution of corporate tax changes (static)
"""

"""
# Section 1: Code for comparing against SCF data
# Note: This code is not necessary for the paper. It's here for purposes of 
        comparability.
# Distribution of comparable income measure to compare against SCF distribution
calc1 = make_calculator({}, 2015)

expinc = calc1.array('expanded_income')
agi = calc1.array('c00100')
wgt = calc1.array('s006')
compinc = (calc1.array('e00200') + calc1.array('e02100') +
           calc1.array('e00900') + calc1.array('e02000') + 
           calc1.array('e00400') + calc1.array('e00300') +
           calc1.array('e00600') + calc1.array('e02300') + 
           calc1.array('e01500') + calc1.array('e02400'))
(expinc_a, wgt_a) = zip(*sorted(zip(expinc, wgt)))
(agi_b, wgt_b) = zip(*sorted(zip(agi, wgt)))
(compinc_c, wgt_c) = zip(*sorted(zip(compinc, wgt)))
expinc_a = np.array(expinc_a)
agi_b = np.array(agi_b)
compinc_c = np.array(compinc_c)
wgt_a = np.array(wgt_a)
wgt_b = np.array(wgt_b)
wgt_c = np.array(wgt_c)
wgt_acum = np.cumsum(wgt_a) / sum(wgt_a)
wgt_bcum = np.cumsum(wgt_b) / sum(wgt_b)
wgt_ccum = np.cumsum(wgt_c) / sum(wgt_c)

qlist_exp = np.ones(9)
qlist_agi = np.ones(9)
qlist_comp = np.ones(9)
qlist_exp[0] = max(expinc_a[wgt_acum <= 0.01])
qlist_agi[0] = max(agi_b[wgt_bcum <= 0.01])
qlist_comp[0] = max(compinc_c[wgt_ccum <= 0.01])
qlist_exp[1] = max(expinc_a[wgt_acum <= 0.05])
qlist_agi[1] = max(agi_b[wgt_bcum <= 0.05])
qlist_comp[1] = max(compinc_c[wgt_ccum <= 0.05])
qlist_exp[2] = max(expinc_a[wgt_acum <= 0.1])
qlist_agi[2] = max(agi_b[wgt_bcum <= 0.1])
qlist_comp[2] = max(compinc_c[wgt_ccum <= 0.1])
qlist_exp[3] = max(expinc_a[wgt_acum <= 0.25])
qlist_agi[3] = max(agi_b[wgt_bcum <= 0.25])
qlist_comp[3] = max(compinc_c[wgt_ccum <= 0.25])
qlist_exp[4] = max(expinc_a[wgt_acum <= 0.5])
qlist_agi[4] = max(agi_b[wgt_bcum <= 0.5])
qlist_comp[4] = max(compinc_c[wgt_ccum <= 0.5])
qlist_exp[5] = max(expinc_a[wgt_acum <= 0.75])
qlist_agi[5] = max(agi_b[wgt_bcum <= 0.75])
qlist_comp[5] = max(compinc_c[wgt_ccum <= 0.75])
qlist_exp[6] = max(expinc_a[wgt_acum <= 0.9])
qlist_agi[6] = max(agi_b[wgt_bcum <= 0.9])
qlist_comp[6] = max(compinc_c[wgt_ccum <= 0.9])
qlist_exp[7] = max(expinc_a[wgt_acum <= 0.95])
qlist_agi[7] = max(agi_b[wgt_bcum <= 0.95])
qlist_comp[7] = max(compinc_c[wgt_ccum <= 0.95])
qlist_exp[8] = max(expinc_a[wgt_acum <= 0.99])
qlist_agi[8] = max(agi_b[wgt_bcum <= 0.99])
qlist_comp[8] = max(compinc_c[wgt_ccum <= 0.99])
for i in range(9):
    print(qlist_exp[i])
for i in range(9):
    print(qlist_agi[i])
for i in range(9):
    print(qlist_comp[i])
"""

"""
Section 2: Underlying distribution info
This presents the underlying relative distributional information
for the windfall to nonprofits and to state/local governments.
"""
# Distributions for nonprofit stakeholders
services_tot = distTable_km(calc_pre, calc_tcja, 'expanded',
                            'benefits', 'total1',
                            RANKING, SCALING, EXCLUDING, SCREENING)
char_tot = distTable_km(calc_pre, calc_tcja, 'expanded',
                        'charity', 'total1',
                        RANKING, SCALING, EXCLUDING, SCREENING)
char_totafter = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'charity_after', 'total1',
                             RANKING, SCALING, EXCLUDING, SCREENING)
wage_tot = distTable_km(calc_pre, calc_tcja, 'expanded',
                        'wages', 'total1',
                        RANKING, SCALING, EXCLUDING, SCREENING)
wage_totafter = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'wages_after', 'total1',
                             RANKING, SCALING, EXCLUDING, SCREENING)
rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile',
            'Fifth decile', 'Sixth decile', 'Seventh decile', 'Eighth decile',
            'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%', 'All units']
services_dist = services_tot / services_tot[-1]
wage_dist = wage_tot / wage_tot[-1]
wageafter_dist = wage_totafter / wage_totafter[-1]
char_dist = char_tot / char_tot[-1]
charafter_dist = char_totafter / char_totafter[-1]
ourmix_tot = 0.208 * services_tot + 0.78 * wage_tot
ourmix_dist = ourmix_tot / ourmix_tot[-1]
ourmixafter_tot = 0.208 * services_tot + 0.78 * wage_totafter
ourmixafter_dist = ourmixafter_tot / ourmixafter_tot[-1]
nonprof_tableA = pd.DataFrame({"Income groups": rowlabel,
                               "Reduced services": services_dist,
                               "Reduced compensation": wage_dist,
                               "More giving": char_dist,
                               "Preferred mix": ourmix_dist})
nonprof_tableB = pd.DataFrame({"Income groups": rowlabel,
                               "Reduced services": services_dist,
                               "Reduced compensation": wageafter_dist,
                               "More giving": charafter_dist,
                               "Preferred mix": ourmixafter_dist})
nonprof_tableA.to_csv('business_dist_tables/nonprof_tableA.csv', index=False)
nonprof_tableB.to_csv('business_dist_tables/nonprof_tableB.csv', index=False)

# Distributions for state/local governments
benefits = distTable_km(calc_pre, calc_tcja, 'expanded',
                        'benefits', 'total1',
                        RANKING, SCALING, EXCLUDING, SCREENING)
wage = distTable_km(calc_pre, calc_tcja, 'expanded',
                    'wages', 'total1',
                    RANKING, SCALING, EXCLUDING, SCREENING)
taxes = distTable_km(calc_pre, calc_tcja, 'expanded',
                     'state_taxes', 'total1',
                     RANKING, SCALING, EXCLUDING, SCREENING)
rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile',
            'Fifth decile', 'Sixth decile', 'Seventh decile', 'Eighth decile',
            'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%', 'All units']
slgtable = pd.DataFrame({"Income groups": rowlabel,
                         "Increase Medicaid spending": benefits / benefits[-1],
                         "Increase compensation": wage / wage[-1],
                         "Reduce taxes": taxes / taxes[-1]})
slgtable.to_csv('business_dist_tables/slg_table.csv', index=False)

# Generate the distributional tables for every year
for year in range(2018, 2028):
    dtab = fullDistComparison(calc_pre, calc_tcja, year,
                              equity, dshare, wtshare,
                              nonprofit_split, slgov_split,
                              RANKING, SCALING, EXCLUDING, SCREENING)
    dtab.to_csv('business_dist_tables/mainfullstatic' + str(year) + '.csv',
                index=False)
