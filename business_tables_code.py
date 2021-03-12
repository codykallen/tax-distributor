# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 08:57:09 2018

@author: cody_
Distribution of corporate tax changes (static)
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

# Distribution of equity and equity income
equitydist = equityDistribution(equity, dshare, calc_pre, RANKING, SCALING,
                       EXCLUDING, SCREENING)
equitydist.to_csv('business_dist_tables/equity_table.csv', index=False)

# Generate the distributional tables for every year
for year in YEARLIST:
    dtab = fullDistComparison(calc_pre, calc_tcja, year,
                              equity, dshare, wtshare,
                              nonprofit_split, slgov_split,
                              RANKING, SCALING, EXCLUDING, SCREENING)
    dtab.to_csv('business_dist_tables/mainfullstatic' + str(year) + '.csv',
                index=False)
