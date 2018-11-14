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
compinc = (calc1.array('e00200') + calc1.array('e02100') + calc1.array('e00900') + calc1.array('e02000') + 
           calc1.array('e00400') + calc1.array('e00300') + calc1.array('e00600') + calc1.array('e02300') + 
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
ranking = {'w_adult': 1, 'w_child': 1, 'elast_size': 0.5}
scaling = {'w_adult': 1, 'w_child': 1, 'elast_size': 0}

# Distributions for nonprofit stakeholders
services_tot = distTable_km(calc_pre, calc_tcja, 'expanded', 'benefits', 'total1', ranking, scaling, ["neginc"], ["",""])
char_tot = distTable_km(calc_pre, calc_tcja, 'expanded', 'charity', 'total1', ranking, scaling, ["neginc"], ["",""])
char_totafter = distTable_km(calc_pre, calc_tcja, 'expanded', 'charity_after', 'total1', ranking, scaling, ["neginc"], ["",""])
wage_tot = distTable_km(calc_pre, calc_tcja, 'expanded', 'wages', 'total1', ranking, scaling, ["neginc"], ["",""])
wage_totafter = distTable_km(calc_pre, calc_tcja, 'expanded', 'wages_after', 'total1', ranking, scaling, ["neginc"], ["",""])
rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile', 'Fifth decile', 'Sixth decile',
            'Seventh decile', 'Eighth decile', 'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%', 'All units']
nonprof_tableA = pd.DataFrame({"Income groups": rowlabel,
                               "Reduced services": services_tot / services_tot[-1],
                               "Reduced compensation": wage_tot / wage_tot[-1],
                               "More giving": char_tot / char_tot[-1],
                               "Preferred mix": (0.208 * services_tot + 0.78 * wage_tot) / (0.208 * services_tot[-1] + 0.78 * wage_tot[-1])})
nonprof_tableB = pd.DataFrame({"Income groups": rowlabel,
                               "Reduced services": services_tot / services_tot[-1],
                               "Reduced compensation": wage_totafter / wage_tot[-1],
                               "More giving": char_totafter / char_tot[-1],
                               "Preferred mix": (0.208 * services_tot + 0.78 * wage_totafter) / (0.208 * services_tot[-1] + 0.78 * wage_tot[-1])})
nonprof_tableA.to_csv('business_dist_tables/nonprof_tableA.csv', index=False)
nonprof_tableB.to_csv('business_dist_tables/nonprof_tableB.csv', index=False)

# Distributions for state/local governments
ranking = {'w_adult': 1, 'w_child': 1, 'elast_size': 0.5}
scaling = {'w_adult': 1, 'w_child': 1, 'elast_size': 0}
benefits = distTable_km(calc_pre, calc_tcja, 'expanded', 'benefits', 'total1', ranking, scaling, ["neginc"], ["",""])
wage = distTable_km(calc_pre, calc_tcja, 'expanded', 'wages', 'total1', ranking, scaling, ["neginc"], ["",""])
taxes = distTable_km(calc_pre, calc_tcja, 'expanded', 'state_taxes', 'total1', ranking, scaling, ["neginc"], ["",""])
rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile', 'Fifth decile', 'Sixth decile',
            'Seventh decile', 'Eighth decile', 'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%', 'All units']
slgtable = pd.DataFrame({"Income groups": rowlabel,
                         "Increase Medicaid spending": benefits / benefits[-1],
                         "Increase compensation": wage / wage[-1],
                         "Reduce taxes": taxes / taxes[-1]})
slgtable.to_csv('business_dist_tables/slg_table.csv', index=False)

# Choose distribution inputs and assumptions of burden split
ranking = {'w_adult': 1, 'w_child': 1, 'elast_size': 0.5}
scaling = {'w_adult': 1, 'w_child': 1, 'elast_size': 0}
excluding = ["neginc"]
screening = ["", ""]
nonprofit_split = {"services": 0.208, "compensation": 0.78, "donors": 0, "foreign": 0.012}
slgov_split = {"benefits": 0.0, "compensation": 1.0, "taxes": 0.0}

# Generate the distributional tables for every year
for year in range(2018, 2028):
    dtab = fullDistComparison(calc_pre, calc_tcja, year, equity, dshare, wtshare,
                              nonprofit_split, slgov_split, ranking, scaling, excluding, screening)
    dtab.to_csv('business_dist_tables/mainfullstatic' + str(year) + '.csv', index=False)
