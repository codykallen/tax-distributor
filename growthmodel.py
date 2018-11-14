# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 13:46:55 2018

@author: cody_
"""

import numpy as np
import pandas as pd
import copy

econdata = pd.read_csv('econ_params.csv')
invresults = pd.read_csv('invresults.csv')
laborresults = pd.read_csv('laborresults.csv')
forecasts = pd.read_csv('forecasts.csv')

# Starting year is 2015
maxyear = 2200
# Create baseline GDP vectors
GDP0 = [forecasts['gdp'][0].item()]
GDPgrowth0 = [0]
govshare0 = [forecasts['govshare'][0].item()]
govinc0 = [GDP0[0] * govshare0[0]]
privinc0 = [GDP0[0] - govinc0[0]]
# Create baseline capital vectors
Kequip0 = [7755.802]
Kstruc0 = [13824.675]
Krentres0 = [2786.454]
Kiprd0 = [1676.124]
Kipsoft0 = [938.639]
Kipart0 = [674.508]
# Create baseline labor vector
labor = [1.0]
# Create baseline investment vectors
Iequip0 = [976.579]
Istruc0 = [426.470]
Irentres0 = [97.315]
Iiprd0 = [243.857]
Iipsoft0 = [325.707]
Iipart0 = [79.413]
# Create reform investment vectors
Iequip1 = [Iequip0[0]]
Istruc1 = [Istruc0[0]]
Irentres1 = [Irentres0[0]]
Iiprd1 = [Iiprd0[0]]
Iipsoft1 = [Iipsoft0[0]]
Iipart1 = [Iipart0[0]]
# Create reform capital vectors
Kequip1 = [Kequip0[0]]
Kstruc1 = [Kstruc0[0]]
Krentres1 = [Krentres0[0]]
Kiprd1 = [Kiprd0[0]]
Kipsoft1 = [Kipsoft0[0]]
Kipart1 = [Kipart0[0]]
# Create new income vectors
dYequip = [0]
dYstruc = [0]
dYrentres = [0]
dYiprd = [0]
dYipsoft = [0]
dYipart = [0]
dYlabor = [0]
dY = [0]
# Create new GDP vectors
govinc1 = [govinc0[0]]
privinc1 = [privinc0[0]]
GDP1 = [GDP0[0]]
GDPgrowth1 = [GDPgrowth0[0]]
GDPratio = [1.0]
# Save the necessary parameters
delta_equip = econdata['delta_equip'][0].item()
delta_struc = econdata['delta_struc'][0].item()
delta_rentres = econdata['delta_rentres'][0].item()
delta_iprd = econdata['delta_iprd'][0].item()
delta_ipsoft = econdata['delta_ipsoft'][0].item()
delta_ipart = econdata['delta_ipart'][0].item()
alpha_equip = econdata['alpha_equip'][0].item()
alpha_struc = econdata['alpha_struc'][0].item()
alpha_rentres = econdata['alpha_rentres'][0].item()
alpha_iprd = econdata['alpha_iprd'][0].item()
alpha_ipsoft = econdata['alpha_ipsoft'][0].item()
alpha_ipart = econdata['alpha_ipart'][0].item()
alpha_labor = econdata['alpha_labor'][0].item()

# Begin growth model
for year in range(2016, maxyear):
    # Determine growth forecast
    if year <= 2027:
        GDP0.append(forecasts['gdp'][year-2015].item())
        GDPgrowth0.append(GDP0[-1] / GDP0[-2] - 1.0)
        govshare0.append(forecasts['govshare'][year-2015].item())
    elif year <= 2047:
        GDPgrowth0.append(forecasts['gdp_growth'][year-2015].item())
        GDP0.append(GDP0[-1] * (1 + GDPgrowth0[-1]))
        govshare0.append(govshare0[-1])
    else:
        GDPgrowth0.append(GDPgrowth0[-1])
        GDP0.append(GDP0[-1] * (1 + GDPgrowth0[-1]))
        govshare0.append(govshare0[-1])
    govinc0.append(GDP0[-1] * govshare0[-1])
    privinc0.append(GDP0[-1] - govinc0[-1])
    # Update capital stocks based on previous year's investment
    Kequip0.append(Kequip0[-1] * (1 - delta_equip) + Iequip0[-1])
    Kequip1.append(Kequip1[-1] * (1 - delta_equip) + Iequip1[-1])
    Kstruc0.append(Kstruc0[-1] * (1 - delta_struc) + Istruc0[-1])
    Kstruc1.append(Kstruc1[-1] * (1 - delta_struc) + Istruc1[-1])
    Krentres0.append(Krentres0[-1] * (1 - delta_rentres) + Irentres0[-1])
    Krentres1.append(Krentres1[-1] * (1 - delta_rentres) + Irentres1[-1])
    Kiprd0.append(Kiprd0[-1] * (1 - delta_iprd) + Iiprd0[-1])
    Kiprd1.append(Kiprd1[-1] * (1 - delta_iprd) + Iiprd1[-1])
    Kipsoft0.append(Kipsoft0[-1] * (1 - delta_ipsoft) + Iipsoft0[-1])
    Kipsoft1.append(Kipsoft1[-1] * (1 - delta_ipsoft) + Iipsoft1[-1])
    Kipart0.append(Kipart0[-1] * (1 - delta_ipart) + Iipart0[-1])
    Kipart1.append(Kipart1[-1] * (1 - delta_ipart) + Iipart1[-1])
    # Update baseline investment using GDP growth rate
    Iequip0.append(Iequip0[-1] * GDP0[-1] / GDP0[-2])
    Istruc0.append(Istruc0[-1] * GDP0[-1] / GDP0[-2])
    Irentres0.append(Irentres0[-1] * GDP0[-1] / GDP0[-2])
    Iiprd0.append(Iiprd0[-1] * GDP0[-1] / GDP0[-2])
    Iipsoft0.append(Iipsoft0[-1] * GDP0[-1] / GDP0[-2])
    Iipart0.append(Iipart0[-1] * GDP0[-1] / GDP0[-2])
    # Update reform investment using baseline and response
    year2 = min(year, 2027)
    Iequip1.append(Iequip0[-1] * (1 + invresults['pch_equip'][year2-2014].item()))
    Istruc1.append(Istruc0[-1] * (1 + invresults['pch_struc'][year2-2014].item()))
    Irentres1.append(Irentres0[-1] * (1 + invresults['pch_rentres'][year2-2014].item()))
    Iiprd1.append(Iiprd0[-1] * (1 + invresults['pch_iprd'][year2-2014].item()))
    Iipsoft1.append(Iipsoft0[-1] * (1 + invresults['pch_ipsoft'][year2-2014].item()))
    Iipart1.append(Iipart0[-1] * (1 + invresults['pch_ipart'][year2-2014].item()))
    # Change in aggregate productive capacity based on change in capital growth rate
    dYequip.append((Kequip1[-1] / Kequip1[-2] - Kequip0[-1] / Kequip0[-2]) * alpha_equip)
    dYstruc.append((Kstruc1[-1] / Kstruc1[-2] - Kstruc0[-1] / Kstruc0[-2]) * alpha_struc)
    dYrentres.append((Krentres1[-1] / Krentres1[-2] - Krentres0[-1] / Krentres0[-2]) * alpha_rentres)
    dYiprd.append((Kiprd1[-1] / Kiprd1[-2] - Kiprd0[-1] / Kiprd0[-2]) * alpha_iprd)
    dYipsoft.append((Kipsoft1[-1] / Kipsoft1[-2] - Kipsoft0[-1] / Kipsoft0[-2]) * alpha_ipsoft)
    dYipart.append((Kipart1[-1] / Kipart1[-2] - Kipart0[-1] / Kipart0[-2]) * alpha_ipart)
    # Change in aggregate productive capacity based change in labor growth rate
    if year <= 2027:
        labor.append(1.0 + laborresults['pch_labor'][year-2014].item())
    else:
        labor.append(labor[-1])
    dYlabor.append((labor[-1] / labor[-2] - 1) * alpha_labor)
    dY.append(dYequip[-1] + dYstruc[-1] + dYrentres[-1] + dYiprd[-1] + dYipsoft[-1] + dYipart[-1] + dYlabor[-1])
    govinc1.append(govinc0[-1])
    privinc1.append(privinc1[-1] * (privinc0[-1] / privinc0[-2] + dY[-1]))
    GDP1.append(govinc1[-1] + privinc1[-1])
    GDPgrowth1.append(GDP1[-1] / GDP1[-2] - 1.0)
    GDPratio.append(GDP1[-1] / GDP0[-1])

GDPratioResults = GDPratio[3:13]
GDPratioResults.append(GDPratio[-1])
yearlist = list(range(2018,2028))
yearlist.append(maxyear)
GDPresult = pd.DataFrame({"Year": yearlist, "GDP ratio": GDPratioResults})
GDPresult.to_csv("growtheffects.csv", index=False)

GDPforplot = pd.DataFrame({"Year": range(2017, 2048), 
                           "GDP baseline": GDP0[2:33],
                           "GDP reform": GDP1[2:33]})
GDPforplot.to_csv('GDPdata.csv', index=False)
growdiffs1 = np.array(GDPgrowth1[:13]) - np.array(GDPgrowth0[:13])
growdiff_tab = pd.DataFrame({"Year": range(2015, 2028), "gfactors": growdiffs1})
growdiff_tab.to_csv("growdiffs.csv")

