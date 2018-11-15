# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:27:56 2018

@author: cody_
This file generates the main distributional tables from 
Kallen and Mathur (2018).
It assumes the existence (already) of Calculator objects calc_pre and calc_tcja
and that the code in `distributional_code.py` has already been executed.

We first specify preferred measures for equivalence scales (ranking), 
weighting (scaling), excluding groups (excluding), and demographics to focus
on (screening). For instructions on which to choose, see the explanation in
`distributional_code.py`.
"""

"""
Section 1: Main distributional analysis for each year
"""
calc1 = copy.deepcopy(calc_pre)
calc2 = copy.deepcopy(calc_tcja)

for year in range(2018, 2028):
    calc1.advance_to_year(year)
    calc2.calc_all()
    calc1.advance_to_year(year)
    calc2.calc_all()
    tableL = levelTable_km(calc1, calc2, RANKING, SCALING, EXCLUDING,
                           SCREENING)
    tableC = changeTable_km(calc1, calc2, RANKING, SCALING, EXCLUDING,
                            SCREENING)
    tableL.to_csv('indiv_dist_tables/tableL' + str(year) + '.csv', index=False)
    tableC.to_csv('indiv_dist_tables/tableC' + str(year) + '.csv', index=False)


# Labels for income groups
rowlabel = ['Bottom decile', 'Second decile', 'Third decile', 'Fourth decile',
            'Fifth decile', 'Sixth decile', 'Seventh decile', 'Eighth decile',
            'Ninth decile', 'Next 5%', 'Next 4%', 'Top 1%', 'All units']

"""
Section 2: Sensitivity to equivalence scales
"""
scaling = {"w_adult": 1, "w_child": 1, "elast_size": 0}
excluding = ["neginc"]
screening = ["", ""]
ranking1 = {"w_adult": 1, "w_child": 1, "elast_size": 0}
ranking2 = {"w_adult": 1, "w_child": 1, "elast_size": 1}
ranking3 = {"w_adult": 1, "w_child": 1, "elast_size": 0.5}
ranking4 = {"w_adult": 0.7, "w_child": 0.5, "elast_size": 1}
ranking5 = {"w_adult": 0.5, "w_child": 0.3, "elast_size": 1}

# Equivalence scale of 1 (no reranking)
totaltax_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking1, scaling, excluding, screening)
totaltax_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking1, scaling, excluding, screening)
totalinc_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking1, scaling, excluding, screening)
totalinc_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking1, scaling, excluding, screening)
avgrate_pre1 = totaltax_pre1 / totalinc_pre1 * 100
avgrate_post1 = totaltax_post1 / totalinc_post1 * 100
# Size equivalence scale (divide by size of tax unit)
totaltax_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking2, scaling, excluding, screening)
totaltax_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking2, scaling, excluding, screening)
totalinc_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking2, scaling, excluding, screening)
totalinc_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking2, scaling, excluding, screening)
avgrate_pre2 = totaltax_pre2 / totalinc_pre2 * 100
avgrate_post2 = totaltax_post2 / totalinc_post2 * 100
# Square root equivalence scale (divide by square root of size of tax unit)
totaltax_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking3, scaling, excluding, screening)
totaltax_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking3, scaling, excluding, screening)
totalinc_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking3, scaling, excluding, screening)
totalinc_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking3, scaling, excluding, screening)
avgrate_pre3 = totaltax_pre3 / totalinc_pre3 * 100
avgrate_post3 = totaltax_post3 / totalinc_post3 * 100
# Oxford scale
totaltax_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking4, scaling, excluding, screening)
totaltax_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking4, scaling, excluding, screening)
totalinc_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking4, scaling, excluding, screening)
totalinc_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking4, scaling, excluding, screening)
avgrate_pre4 = totaltax_pre4 / totalinc_pre4 * 100
avgrate_post4 = totaltax_post4 / totalinc_post4 * 100
# OECD-modified scale
totaltax_pre5 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking5, scaling, excluding, screening)
totaltax_post5 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking5, scaling, excluding, screening)
totalinc_pre5 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking5, scaling, excluding, screening)
totalinc_post5 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking5, scaling, excluding, screening)
avgrate_pre5 = totaltax_pre5 / totalinc_pre5 * 100
avgrate_post5 = totaltax_post5 / totalinc_post5 * 100
tableS1 = pd.DataFrame({"Income group": rowlabel,
                        "None, pre": avgrate_pre1,
                        "None, post": avgrate_post1,
                        "Tax unit size, pre": avgrate_pre2,
                        "Tax unit size, post": avgrate_post2,
                        "Square root of size, pre": avgrate_pre3,
                        "Square root of size, post": avgrate_post3,
                        "Oxford scale, pre": avgrate_pre4,
                        "Oxford scale, post": avgrate_post4,
                        "OECD modified scale, pre": avgrate_pre5,
                        "OECD modified scale, post": avgrate_post5})
tableS1.to_csv('indiv_dist_tables/tableS_ranking.csv', index=False)

"""
Section 3: Sensitivity to reweighting
"""
ranking = {"w_adult": 1, "w_child": 1, "elast_size": 0}
excluding = ["neginc"]
screening = ["", ""]
scaling1 = {"w_adult": 1, "w_child": 1, "elast_size": 0}
scaling2 = {"w_adult": 1, "w_child": 1, "elast_size": 1}
scaling3 = {"w_adult": 1, "w_child": 1, "elast_size": 0.5}
scaling4 = {"w_adult": 1, "w_child": 0, "elast_size": 1}

# No reweighting (tax unit basis)
totaltax_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling1, excluding, screening)
totaltax_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling1, excluding, screening)
totalinc_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling1, excluding, screening)
totalinc_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling1, excluding, screening)
avgrate_pre1 = totaltax_pre1 / totalinc_pre1 * 100
avgrate_post1 = totaltax_post1 / totalinc_post1 * 100
# Reweighting by size of unit (population basis)
totaltax_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling2, excluding, screening)
totaltax_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling2, excluding, screening)
totalinc_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling2, excluding, screening)
totalinc_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling2, excluding, screening)
avgrate_pre2 = totaltax_pre2 / totalinc_pre2 * 100
avgrate_post2 = totaltax_post2 / totalinc_post2 * 100
# Reweighting by square root of unit
totaltax_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling3, excluding, screening)
totaltax_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling3, excluding, screening)
totalinc_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling3, excluding, screening)
totalinc_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling3, excluding, screening)
avgrate_pre3 = totaltax_pre3 / totalinc_pre3 * 100
avgrate_post3 = totaltax_post3 / totalinc_post3 * 100
# Reweighting by number of adults (adult population basis)
totaltax_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling4, excluding, screening)
totaltax_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling4, excluding, screening)
totalinc_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling4, excluding, screening)
totalinc_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling4, excluding, screening)
avgrate_pre4 = totaltax_pre4 / totalinc_pre4 * 100
avgrate_post4 = totaltax_post4 / totalinc_post4 * 100
tableS2 = pd.DataFrame({"Income group": rowlabel,
                        "None, pre": avgrate_pre1,
                        "None, post": avgrate_post1,
                        "Tax unit size, pre": avgrate_pre2,
                        "Tax unit size, post": avgrate_post2,
                        "Square root of size, pre": avgrate_pre3,
                        "Square root of size, post": avgrate_post3,
                        "Number of adults, pre": avgrate_pre4,
                        "Number of adults, post": avgrate_post4})
tableS2.to_csv('indiv_dist_tables/tableS_weighting.csv', index=False)

"""
Section 4: Sensitivity to the income measure
"""
scaling1 = {"w_adult": 1, "w_child": 1, "elast_size": 0}
ranking = {"w_adult": 1, "w_child": 1, "elast_size": 0}
excluding = ["neginc"]
screening = ["", ""]

# Expanded income
totaltax_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling, excluding, screening)
totaltax_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling, excluding, screening)
totalinc_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding, screening)
totalinc_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding, screening)
avgrate_pre1 = totaltax_pre1 / totalinc_pre1 * 100
avgrate_post1 = totaltax_post1 / totalinc_post1 * 100
# Adjusted gross income
totaltax_pre2 = distTable_km(calc_pre, calc_tcja, 'agi',
                             'totaltax', 'total1',
                             ranking, scaling, excluding, screening)
totaltax_post2 = distTable_km(calc_pre, calc_tcja, 'agi',
                              'totaltax', 'total2',
                              ranking, scaling, excluding, screening)
totalinc_pre2 = distTable_km(calc_pre, calc_tcja, 'agi',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding, screening)
totalinc_post2 = distTable_km(calc_pre, calc_tcja, 'agi',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding, screening)
avgrate_pre2 = totaltax_pre2 / totalinc_pre2 * 100
avgrate_post2 = totaltax_post2 / totalinc_post2 * 100
# Pre-tax, pre-benefit income
totaltax_pre3 = distTable_km(calc_pre, calc_tcja, 'nobenefits',
                             'totaltax', 'total1',
                             ranking, scaling, excluding, screening)
totaltax_post3 = distTable_km(calc_pre, calc_tcja, 'nobenefits',
                              'totaltax', 'total2',
                              ranking, scaling, excluding, screening)
totalinc_pre3 = distTable_km(calc_pre, calc_tcja, 'nobenefits',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding, screening)
totalinc_post3 = distTable_km(calc_pre, calc_tcja, 'nobenefits',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding, screening)
avgrate_pre3 = totaltax_pre3 / totalinc_pre3 * 100
avgrate_post3 = totaltax_post3 / totalinc_post3 * 100
tableS3 = pd.DataFrame({"Income group": rowlabel,
                        "Expanded income, pre": avgrate_pre1, 
                        "Expanded income, post": avgrate_post3,
                        "AGI, pre": avgrate_pre2, 
                        "AGI, post": avgrate_post3,
                        "Market income, pre": avgrate_pre3, 
                        "Market income, post": avgrate_post3})
tableS3.to_csv('indiv_dist_tables/tableS_income.csv', index=False)

"""
Section 5: Sensitivity to excluded groups
"""
scaling1 = {"w_adult": 1, "w_child": 1, "elast_size": 0}
ranking = {"w_adult": 1, "w_child": 1, "elast_size": 0}
screening = ["", ""]
excluding1 = ["neginc"]
excluding2 = ["neginc", "dependents"]
excluding3 = ["neginc", "dependents", "separate"]
excluding4 = ["neginc", "supertax"]

# Just exclude those with negative income
totaltax_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling, excluding1, screening)
totaltax_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling, excluding1, screening)
totalinc_pre1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding1, screening)
totalinc_post1 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding1, screening)
avgrate_pre1 = totaltax_pre1 / totalinc_pre1 * 100
avgrate_post1 = totaltax_post1 / totalinc_post1 * 100
# Exclude negative income and dependents
totaltax_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling, excluding2, screening)
totaltax_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling, excluding2, screening)
totalinc_pre2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding2, screening)
totalinc_post2 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding2, screening)
avgrate_pre2 = totaltax_pre2 / totalinc_pre2 * 100
avgrate_post2 = totaltax_post2 / totalinc_post2 * 100
# Exclude negative income, dependents, and those with tax > income
totaltax_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling, excluding3, screening)
totaltax_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling, excluding3, screening)
totalinc_pre3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding3, screening)
totalinc_post3 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding3, screening)
avgrate_pre3 = totaltax_pre3 / totalinc_pre3 * 100
avgrate_post3 = totaltax_post3 / totalinc_post3 * 100
# Exclude negative income and those with tax > income
totaltax_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'totaltax', 'total1',
                             ranking, scaling, excluding4, screening)
totaltax_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'totaltax', 'total2',
                              ranking, scaling, excluding4, screening)
totalinc_pre4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                             'expanded_income', 'total1',
                             ranking, scaling, excluding4, screening)
totalinc_post4 = distTable_km(calc_pre, calc_tcja, 'expanded',
                              'expanded_income', 'total2',
                              ranking, scaling, excluding4, screening)
avgrate_pre4 = totaltax_pre4 / totalinc_pre4 * 100
avgrate_post4 = totaltax_post4 / totalinc_post4 * 100
tableS4 = pd.DataFrame({"Income group": rowlabel,
                        "None pre": avgrate_pre4, 
                        "None, post": avgrate_post4,
                        "Dependents, pre": avgrate_pre4, 
                        "Dependents, post": avgrate_post4,
                        "Incomplete units, pre": avgrate_pre4, 
                        "Incomplete units, post": avgrate_post4,
                        "Tax > Income, pre": avgrate_pre4, 
                        "Tax > Income, post": avgrate_post4})
tableS4.to_csv('indiv_dist_tables/tableS_excluded.csv', index=False)

"""
Section 6: Distributional analysis for specific demographic groups
"""
# Married filing jointly
excluding = ["neginc"]
screening = ["married", ""]
tableD_married = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_married.to_csv('indiv_dist_tables/tableD_married.csv', index=False)

# Not married
excluding = ["neginc"]
screening = ["not_married", ""]
tableD_married = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_married.to_csv('indiv_dist_tables/tableD_notmarried.csv', index=False)

# No children in unit
excluding = ["neginc"]
screening = ["", "0"]
tableD_nokids = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_nokids.to_csv('indiv_dist_tables/tableD_nokids.csv', index=False)

# 1 child
excluding = ["neginc"]
screening = ["", "1"]
tableD_1kid = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_1kid.to_csv('indiv_dist_tables/tableD_1kid.csv', index=False)

# 2 children
excluding = ["neginc"]
screening = ["", "2"]
tableD_2kids = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_2kids.to_csv('indiv_dist_tables/tableD_2kids.csv', index=False)

# 3+ children
excluding = ["neginc"]
screening = ["", "3+"]
tableD_3pluskids = demogTable_km(calc_pre, calc_tcja, excluding, screening)
tableD_3pluskids.to_csv('indiv_dist_tables/tableD_3pluskids.csv', index=False)

"""
Section 7: Sensitivity of Kakwani index
"""
scaling_options = ['Weight by size', 'Weight by square root', 'Adults']
ranking_options = ['None', 'Size', 'Oxford', 'OECD']
excluding_options = ['Dependents', 'Incomplete units', 'Tax > Income']
income_options = []
rowlabels = ["Main estimates", "Using different equivalence scales",
             "None", "Size of tax unit", "Oxford", "OECD-modified",
             "Using different weighting systems", "Size of tax unit",
             "Square root of size", "Number of adults",
             "Using different income measures", "AGI", "Market income",
             "Excluding different groups", "Dependents", "Incomplete units",
             "Tax > Income"]
kakwani_table = pd.DataFrame({'Category': rowlabels})
year_options = [2018, 2020, 2022, 2024, 2026]
ranking_main = RANKING
scaling_main = SCALING
resultsdict = {}
for y in year_options:
    reslist = []
    calcA = copy.deepcopy(calc_pre)
    calcA.advance_to_year(y)
    calcA.calc_all()
    calcB = copy.deepcopy(calc_tcja)
    calcB.advance_to_year(y)
    calcB.calc_all()
    # Main estimate
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           ranking_main, scaling_main, ["neginc"]))
    reslist.append(0)
    # Alternative equivalence scales
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           {"w_adult": 1, "w_child": 1, "elast_size": 0},
                           scaling_main, ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           {"w_adult": 1, "w_child": 1, "elast_size": 1},
                           scaling_main, ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           {"w_adult": 0.7, "w_child": 0.5, "elast_size": 1},
                           scaling_main, ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           {"w_adult": 0.5, "w_child": 0.3, "elast_size": 1},
                           scaling_main, ["neginc"]))
    reslist.append(0)
    # Alternative weighting options
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax', ranking_main,
                           {"w_adult": 1, "w_child": 1, "elast_size": 1},
                           ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax', ranking_main,
                           {"w_adult": 1, "w_child": 1, "elast_size": 0.5},
                           ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax', ranking_main,
                           {"w_adult": 1, "w_child": 0, "elast_size": 1},
                           ["neginc"]))
    reslist.append(0)
    # Alternative income measures
    reslist.append(kakwani(calcA, calcB, 'agi', 'totaltax', ranking_main,
                           scaling_main, ["neginc"]))
    reslist.append(kakwani(calcA, calcB, 'nobenefits', 'totaltax',
                           ranking_main, scaling_main, ["neginc"]))
    reslist.append(0)
    # Alternative excluded groups
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           ranking_main, scaling_main,
                           ["neginc", "dependents"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           ranking_main, scaling_main,
                           ["neginc", "dependents", "separate"]))
    reslist.append(kakwani(calcA, calcB, 'expanded', 'totaltax',
                           ranking_main, scaling_main,
                           ["neginc", "supertax"]))
    kakwani_table[str(y)] = reslist
kakwani_table.to_csv('indiv_dist_tables/kakwani.csv', index=False)
