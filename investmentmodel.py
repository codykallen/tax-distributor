# -*- coding: utf-8 -*-
"""
Created on Mon Nov  5 09:57:52 2018

Calculates and saves the changes in investment for each asset type and year.

"""

"""
Section 1: Investment incentives
"""
startyear = 2018
# Note: startyear prevents retroactive responses to the TCJA's tax cuts.

cpolicy_base = pd.read_csv('policy_corp_base.csv')
cpolicy_ref = pd.read_csv('policy_corp_ref.csv')
ncpolicy_base = pd.read_csv('policy_noncorp_base.csv')
ncpolicy_ref = pd.read_csv('policy_noncorp_ref.csv')
econdata_base = pd.read_csv('data_files/econ_params.csv')
econdata_ref = copy.deepcopy(econdata_base)
industrydata = pd.read_csv("data_files/industry_data.csv")
ownertaxes = pd.read_csv("intermediate_results/owner_level_taxes.csv")
theta_results = pd.read_csv("intermediate_results/theta_results.csv")


def calcA_expensing(tau, theta):
    """
    Present value of the tax shield from expensing. 
    """
    return theta * tau

def calcA_econ1tax(tau, theta, bonus, delta, r):
    """
    Present value of the tax shield from true depreciation.
    Assume constant tax rate.
    """
    A0 = theta * tau * delta / (r + delta)
    A = bonus * tau + (1 - bonus) * A0
    return A

def calcA_econ2tax(tau0, tau1, ts, theta, bonus, delta, r):
    """
    Present value of the tax shield from true depreciation.
    Assume tax rate changes from tau0 to tau1 at time ts
    """
    A0 = theta * tau0 * delta / (r + delta)
    Ach = (theta * delta / (r + delta) * np.exp(-(r + delta) * ts) *
           (tau1 - tau0))
    A = bonus * tau0 + (1 - bonus) * (A0 + Ach)
    return A

def calcA_macrs1tax(tau, theta, life, n, bonus, r, pi):
    """
    Present value of the tax shield from MACRS depreciation.
    Assume constant tax rate.
    """
    Adb = (theta * tau * n / (life * (r + pi) + n) *
           (1 - np.exp(1 - n - life * (r + pi) + life * (r + pi) / n)))
    Asl = (theta * tau * n / life / (r + pi) *
           np.exp(1 - n - life * (r + pi)) * (np.exp(life * (r + pi) / n) - 1))
    A = bonus * tau + (1 - bonus) * (Adb + Asl)
    return A

def calcA_macrs2taxearly(tau0, tau1, ts, theta, life, n, bonus, r, pi):
    """
    Present value of the tax shield from MACRS depreciation.
    Assume tax rate changes at time ts < life * (1 - 1/n)
    """
    assert ts < life * (1 - 1/n)
    Adb1 = (theta * tau0 * n / (life * (r + pi) + n) *
            (1 - np.exp(-(r + pi + n/life) * ts)))
    Adb2 = (theta * tau1 * n / (life * (r + pi) + n) *
            (np.exp(-(r + pi + n/life) * ts) -
             np.exp(1 - n - life * (r + pi) + life * (r + pi) / n)))
    Asl = (theta * tau1 * n / life / (r + pi) *
           np.exp(1 - n - life * (r + pi)) * (np.exp(life * (r + pi) / n) - 1))
    A = bonus * tau0 + (1 - bonus) * (Adb1 + Adb2 + Asl)
    return A

def calcA_macrs2taxlate(tau0, tau1, ts, theta, life, n, bonus, r, pi):
    """
    Present value of the tax shield from MACRS depreciation. 
    Assume tax rate changes at time ts > life * (1 - 1/n)
    """
    assert ts > life * (1 - 1/n)
    Adb = (theta * tau0 * n / (life * (r + pi) + n) *
           (1 - np.exp(1 - n - life * (r + pi) + life * (r + pi) / n)))
    Asl1 = (theta * tau0 * n / life / (r + pi) * np.exp(1 - n) *
            (np.exp(-life * (r + pi) + life * (r + pi) / n) -
             np.exp(-(r + pi) * ts)))
    Asl2 = (theta * tau1 * n / life / (r + pi) * np.exp(1 - n) *
            (np.exp(-(r + pi) * ts) - np.exp(-(r + pi) * life)))
    A = bonus * tau0 + (1 - bonus) * (Adb + Asl1 + Asl2)
    return A

def calcA_macrs2taxeven(tau0, tau1, ts, theta, life, n, bonus, r, pi):
    """
    Present value of the tax shield from MACRS depreciation.
    Assume tax rate changes at time ts = life * (1 - 1/n)
    """
    assert ts == life * (1 - 1/n)
    Adb = (theta * tau0 * n / (life * (r + pi) + n) *
           (1 - np.exp(1 - n - life * (r + pi) + life * (r + pi) / n)))
    Asl = (theta * tau1 * n / life / (r + pi) *
           np.exp(1 - n - life * (r + pi)) * (np.exp(life * (r + pi) / n) - 1))
    A = bonus * tau0 + (1 - bonus) * (Adb + Asl)
    return A

def calcA(method, life, bonus, theta, delta, r, pi, tau0, cred = 0,
          tau1=None, ts=None):
    """
    Determines how to calculate the present value of the tax shield from
    capital cost recovery and calls the appropriate function. 
    First, check acceptable values. 
    """
    assert method in ["DB2", "DB1.5", "EXP", "SL", "ECON"]
    assert life > 0
    assert (bonus >= 0) and (bonus <= 1)
    assert delta > 0
    assert r > 0
    assert (tau0 >= 0) and (tau0 <= 1)
    if tau1 is not None:
        assert ts is not None
        assert (tau1 >= 0) and (tau1 <= 1)
    if ts is not None:
        assert tau1 is not None
        assert ts > 0
    if method == "EXP":
        A = calcA_expensing(tau0, theta)
    elif method == "ECON":
        if ts is None:
            A = calcA_econ1tax(tau0, theta, bonus, delta, r)
        else:
            A = calcA_econ2tax(tau0, tau1, ts, theta, bonus, delta, r)
    else:
        if method == "DB2":
            n = 2.0
        elif method == "DB1.5":
            n = 1.5
        else:
            n = 1.0
        if ts is None:
            A = calcA_macrs1tax(tau0, theta, life, n, bonus, r, pi)
        else:
            t1 = life * (1 - 1/n)
            if ts < t1:
                A = calcA_macrs2taxearly(tau0, tau1, ts, theta, life, n,
                                         bonus, r, pi)
            elif ts == t1:
                A = calcA_macrs2taxeven(tau0, tau1, ts, theta,life, n,
                                        bonus, r, pi)
            elif ts < life:
                A = calcA_macrs2taxlate(tau0, tau1, ts, theta, life, n,
                                        bonus, r, pi)
            else:
                A = calcA_macrs1tax(tau0, theta, life, n, bonus, r, pi)
    A2 = A * (1 - cred) + cred
    return A2

def calcF_taxshield(Delta, delta, i, r, profit, theta, dedlimit, tau0,
                    tau1=None, ts=None):
    """
    Calculate present value of the tax shield from interest deductibility.
    """
    nid = min(Delta * i, dedlimit * (profit + delta))
    shield0 = nid * theta * tau0 / (r + delta)
    if ts is not None:
        assert tau1 is not None
        shieldch = nid * theta * (tau1 - tau0) / (r + delta)
    else:
        shieldch = 0
    shield = shield0 + shieldch
    return shield

def calcF_iitaxdistortion(Delta, delta, r, tauD, tauE):
    """
    Calculate the distortion from the differential taxation of income from
    debt and from equity.
    """
    dist = Delta * (tauE - tauD) / (r + delta)
    return dist

def calcF(Delta, delta, i, r, profit, theta, dedlimit, tauD, tauE, tau0,
          tau1=None, ts=None):
    """
    Calculate the total financing distortion.
    """
    shield = calcF_taxshield(Delta, delta, i, r, profit, theta, dedlimit,
                             tau0, tau1, ts)
    otherdist = calcF_iitaxdistortion(Delta, delta, r, tauD, tauE)
    F = shield + otherdist
    return F

def calcT(theta, gamma, r, delta, tau0, tau1=None, ts=None):
    """
    Calculates the effective tax rate on gross profit. 
    """
    if ts is None:
        T = theta * gamma * tau0
    else:
        assert tau1 is not None
        T = theta * gamma * (tau0 + (tau1 - tau0) * np.exp(-(r + delta) * ts))
    return T

def calcCoC(method, life, bonus, theta, delta, r, pi, tau0, rdcred, tau1, ts,
            Delta, i, dedlimit, tauD, tauE, gamma, firmprofit):
    """
    Calculates the user cost of capital.
    """
    A = calcA(method, life, bonus, theta, delta, r, pi, tau0, rdcred, tau1, ts)
    F = calcF(Delta, delta, i, r, firmprofit, theta, dedlimit, tauD, tauE,
              tau0, tau1, ts)
    T = calcT(theta, gamma, r, delta, tau0, tau1, ts)
    Q = (1 - A - F) / (1 - T) * (r + delta)
    return Q

def calcEATR(method, life, bonus, theta, delta, r, pi, tau0, rdcred, tau1, ts,
             Delta, i, dedlimit, tauD, tauE, gamma, projprofit, firmprofit):
    """
    Calculates the effective average tax rate.
    """
    Rstar = (projprofit - r) / (r + delta)
    A = calcA(method, life, bonus, theta, delta, r, pi, tau0, rdcred, tau1, ts)
    F = calcF(Delta, delta, i, r, firmprofit, theta, dedlimit, tauD, tauE,
              tau0, tau1, ts)
    T = calcT(theta, gamma, r, delta, tau0, tau1, ts)
    R = -1 + A + F + (projprofit + delta) * (1 - T) / (r + delta)
    P = projprofit / (r + delta)
    eatr = (Rstar - R) / P
    return eatr

def getTaxRates(firmtype, year, baseline):
    """
    Figures out the tax rates, allowing up to one rate change.
    """
    if baseline:
        if firmtype == "corp":
            taxlist = np.array(cpolicy_base["tau_c"][year:])
        else:
            taxlist = np.array(ownertaxes["tau_nc_base"][year:])
    else:
        if firmtype == "corp":
            taxlist = np.array(cpolicy_ref["tau_c"][year:])
        else:
            taxlist = np.array(ownertaxes["tau_nc_ref"][year:])
    tau0 = taxlist[0]
    if year == 2027:
        tau1 = None
        ts = None
    else:
        tau1 = None
        ts = None
        for y in range(len(taxlist)):
            if abs(taxlist[y] - tau0) >= 0.01:
                tau1 = taxlist[y]
                ts = y - 0.5
    return (tau0, tau1, ts)
    
def getParams(industry, asset, firmtype, year, baseline):
    """
    Obtains all the parameters necessary to calculate the cost of capital
    and the EATR. 
    """
    assert firmtype in ["corp", "noncorp"]
    assert asset in ["equip1", "equip2", "equip3",
                     "struc1", "struc2", "struc3", "rentres",
                     "iprd", "ipsoft", "ipart"]
    year2 = min(int(year), 2027) - 2014
    # Choose policy and economic parameters to use
    if baseline:
        if firmtype == "corp":
            paramdata = copy.deepcopy(cpolicy_base)
        else:
            paramdata = copy.deepcopy(ncpolicy_base)
        econdata = copy.deepcopy(econdata_base)
    else:
        if firmtype == "corp":
            paramdata = copy.deepcopy(cpolicy_ref)
        else:
            paramdata = copy.deepcopy(ncpolicy_ref)
        econdata = copy.deepcopy(econdata_ref)
    # Get asset-specific information
    if asset == "equip1":
        method = paramdata["equip_depr_method1"][year2]
        life = paramdata["equip_depr_life1"][year2].item()
        bonus = paramdata["equip_depr_bonus1"][year2].item()
        delta = econdata['delta_equip'][0].item()
    elif asset == "equip2":
        method = paramdata["equip_depr_method2"][year2]
        life = paramdata["equip_depr_life2"][year2].item()
        bonus = paramdata["equip_depr_bonus2"][year2].item()
        delta = econdata['delta_equip'][0].item()
    elif asset == "equip3":
        method = paramdata["equip_depr_method3"][year2]
        life = paramdata["equip_depr_life3"][year2].item()
        bonus = paramdata["equip_depr_bonus3"][year2].item()
        delta = econdata['delta_equip'][0].item()
    if asset == "struc1":
        method = paramdata["struc_depr_method1"][year2]
        life = paramdata["struc_depr_life1"][year2].item()
        bonus = paramdata["struc_depr_bonus1"][year2].item()
        delta = econdata['delta_struc'][0].item()
    elif asset == "struc2":
        method = paramdata["struc_depr_method2"][year2]
        life = paramdata["struc_depr_life2"][year2].item()
        bonus = paramdata["struc_depr_bonus2"][year2].item()
        delta = econdata['delta_struc'][0].item()
    elif asset == "struc3":
        method = paramdata["struc_depr_method3"][year2]
        life = paramdata["struc_depr_life3"][year2].item()
        bonus = paramdata["struc_depr_bonus3"][year2].item()
        delta = econdata['delta_struc'][0].item()
    elif asset == "rentres":
        method = paramdata["rentres_depr_method"][year2]
        life = paramdata["rentres_depr_life"][year2].item()
        bonus = paramdata["rentres_depr_bonus"][year2].item()
        delta = econdata['delta_rentres'][0].item()
    elif asset == "iprd":
        method = paramdata["iprd_depr_method"][year2]
        life = paramdata["iprd_depr_life"][year2].item()
        bonus = paramdata["iprd_depr_bonus"][year2].item()
        delta = econdata['delta_iprd'][0].item()
    elif asset == "ipsoft":
        method = paramdata["ipsoft_depr_method"][year2]
        life = paramdata["ipsoft_depr_life"][year2].item()
        bonus = paramdata["ipsoft_depr_bonus"][year2].item()
        delta = econdata['delta_ipsoft'][0].item()
    elif asset == "ipart":
        method = paramdata["ipart_depr_method"][year2]
        life = paramdata["ipart_depr_life"][year2].item()
        bonus = paramdata["ipart_depr_bonus"][year2].item()
        delta = econdata['delta_ipart'][0].item()
    if asset == "iprd":
        rdcred = paramdata["iprd_depr_credrate"][year2].item()
    else:
        rdcred = 0
    # Get entity-specific information
    if firmtype == "corp":
        Delta = econdata["f_c"][0].item()
        i = econdata["r_d"][year2].item()
        r_e = econdata["r_e_c"][year2].item()
        r = Delta * i + (1 - Delta) * r_e
    else:
        Delta = econdata["f_nc"][0].item()
        i = econdata["r_d"][year2].item()
        r_e = econdata["r_e_nc"][year2].item()
        r = Delta * i + (1 - Delta) * r_e
    pi = econdata["pi"][year2].item()
    dedlimit = paramdata["int_dedlimit"][year2].item()
    # Get info for domestic production deduction
    s199rate = paramdata["s199_rate"][year2].item()
    indid = industrydata["Industry"] == industry
    s199base = industrydata["DPDbase"][indid].item()
    gamma = 1 - s199base * s199rate
    projprofit = econdata["p_project"][0].item()
    firmprofit = econdata["p_firm"][0].item()
    if baseline:
        if firmtype == "corp":
            tauD = ownertaxes["tau_dc_base"][year2].item()
            tauE = ownertaxes["tau_e_base"][year2].item()
            theta = theta_results["theta_base"][year2].item()
        else:
            tauD = ownertaxes["tau_dnc_base"][year2].item()
            tauE = 0.0
            theta = 1.0
    else:
        if firmtype == "corp":
            tauD = ownertaxes["tau_dc_ref"][year2].item()
            tauE = ownertaxes["tau_e_ref"][year2].item()
            theta = theta_results["theta_ref"][year2].item()
        else:
            tauD = ownertaxes["tau_dnc_ref"][year2].item()
            tauE = 0.0
            theta = 1.0
    (tau0, tau1, ts) = getTaxRates(firmtype, year2, baseline)
    return (method, life, bonus, delta, Delta, i, r, pi, rdcred,
            dedlimit, gamma, projprofit, firmprofit,
            tauD, tauE, theta, tau0, tau1, ts)

def getCoC(industry, asset, firmtype, baseline, year):
    """
    Calculates the cost of capital for the given asset type and firm type in
    the given year under the baseline or the reform.
    """
    (method, life, bonus,
     delta, Delta, i, r,
     pi, rdcred, dedlimit,
     gamma, projprofit,
     firmprofit, tauD,
     tauE, theta, tau0,
     tau1, ts) = getParams(industry, asset, firmtype, year, baseline)
    coc = calcCoC(method, life, bonus, theta, delta, r, pi, tau0, rdcred,
                  tau1, ts, Delta, i, dedlimit, tauD, tauE, gamma, firmprofit)
    return coc

def getEATR(industry, asset, firmtype, baseline, year):
    """
    Calculates the EATR for the given asset type and firm type in the given
    year under the baseline or the reform.
    """
    (method, life, bonus,
     delta, Delta, i, r,
     pi, rdcred, dedlimit,
     gamma, projprofit,
     firmprofit, tauD,
     tauE, theta, tau0,
     tau1, ts) = getParams(industry, asset, firmtype, year, baseline)
    eatr = calcEATR(method, life, bonus, theta, delta, r, pi, tau0, rdcred,
                    tau1, ts, Delta, i, dedlimit, tauD, tauE, gamma,
                    projprofit, firmprofit)
    return eatr

def getChangeCoC(asset, firmtype, year):
    """
    Calculates the change in cost of capital for the given asset type and firm
    type in the given year, using weighted average across industries.
    """
    assert firmtype in ["corp", "noncorp"]
    assert asset in ["equip1", "equip2", "equip3",
                     "struc1", "struc2", "struc3", "rentres",
                     "iprd", "ipsoft", "ipart"]
    indlist = np.array(industrydata["Industry"])
    if asset in ["equip1", "equip2", "equip3"]:
        invweight = np.array(industrydata["ishare_equip"])
    elif asset in ["struc1", "struc2", "struc3"]:
        invweight = np.array(industrydata["ishare_struc"])
    elif asset == "rentres":
        invweight = np.array(industrydata["ishare_rentres"])
    elif asset == "iprd":
        invweight = np.array(industrydata["ishare_iprd"])
    elif asset == "ipsoft":
        invweight = np.array(industrydata["ishare_ipsoft"])
    elif asset == "ipart":
        invweight = np.array(industrydata["ishare_ipart"])
    # Get the relevant parameters
    coc_base = np.zeros(len(indlist))
    coc_ref = np.zeros(len(indlist))
    for i in range(len(indlist)):
        coc_base[i] = getCoC(indlist[i], asset, firmtype, True, year)
        coc_ref[i] = getCoC(indlist[i], asset, firmtype, False, year)
    pch_coc = coc_ref / coc_base - 1
    pch_coctot = sum(pch_coc * invweight)
    return pch_coctot

def getChangeEATR(asset, year):
    """
    Calculates the change in EATR for the given asset type and firm
    type in the given year, using weighted average across industries.
    """
    assert asset in ["equip1", "equip2", "equip3",
                     "struc1", "struc2", "struc3", "rentres",
                     "iprd", "ipsoft", "ipart"]
    indlist = np.array(industrydata["Industry"])
    if asset in ["equip1", "equip2", "equip3"]:
        invweight = np.array(industrydata["ishare_equip"])
    elif asset in ["struc1", "struc2", "struc3"]:
        invweight = np.array(industrydata["ishare_struc"])
    elif asset == "rentres":
        invweight = np.array(industrydata["ishare_rentres"])
    elif asset == "iprd":
        invweight = np.array(industrydata["ishare_iprd"])
    elif asset == "ipsoft":
        invweight = np.array(industrydata["ishare_ipsoft"])
    elif asset == "ipart":
        invweight = np.array(industrydata["ishare_ipart"])
    # Get the relevant parameters
    eatr_base = np.zeros(len(indlist))
    eatr_ref = np.zeros(len(indlist))
    for i in range(len(indlist)):
        eatr_base[i] = getEATR(indlist[i], asset, "corp", True, year)
        eatr_ref[i] = getEATR(indlist[i], asset, "corp", False, year)
    ch_eatr = eatr_ref - eatr_base
    ch_eatrtot = sum(ch_eatr * invweight)
    return ch_eatrtot

def getChangeInv(asset, year, elast_coc_corp, elast_coc_nc, selast_mne):
    """
    Calculates the percent change in investment in the given asset type in the
    given year.
    """
    corpshare = 0.54566
    noncorpshare = 0.396291804
    mneshare = 0.13444942
    if asset == "equip":
        pcoc1 = getChangeCoC("equip1", "corp", year)
        pcoc2 = getChangeCoC("equip2", "corp", year)
        pcoc3 = getChangeCoC("equip2", "corp", year)
        pcoc4 = getChangeCoC("equip1", "noncorp", year)
        pcoc5 = getChangeCoC("equip2", "noncorp", year)
        pcoc6 = getChangeCoC("equip3", "noncorp", year)
        deatr1 = getChangeEATR("equip1", year)
        deatr2 = getChangeEATR("equip2", year)
        deatr3 = getChangeEATR("equip3", year)
        pcoc_c = (pcoc1 + pcoc2 + pcoc3) / 3
        pcoc_nc = (pcoc4 + pcoc5 + pcoc6) / 3
        peatr = (deatr1 + deatr2 + deatr3) / 3
    elif asset == "struc":
        pcoc1 = getChangeCoC("struc1", "corp", year)
        pcoc2 = getChangeCoC("struc2", "corp", year)
        pcoc3 = getChangeCoC("struc2", "corp", year)
        pcoc4 = getChangeCoC("struc1", "noncorp", year)
        pcoc5 = getChangeCoC("struc2", "noncorp", year)
        pcoc6 = getChangeCoC("struc3", "noncorp", year)
        deatr1 = getChangeEATR("struc1", year)
        deatr2 = getChangeEATR("struc2", year)
        deatr3 = getChangeEATR("struc3", year)
        pcoc_c = (pcoc1 + pcoc2 + pcoc3) / 3
        pcoc_nc = (pcoc4 + pcoc5 + pcoc6) / 3
        peatr = (deatr1 + deatr2 + deatr3) / 3
    elif asset == "rentres":
        pcoc_c = getChangeCoC("rentres", "corp", year)
        pcoc_nc = getChangeCoC("rentres", "noncorp", year)
        peatr = getChangeEATR("rentres", year)
    elif asset == "iprd":
        pcoc_c = getChangeCoC("iprd", "corp", year)
        pcoc_nc = getChangeCoC("iprd", "noncorp", year)
        peatr = getChangeEATR("iprd", year)
    elif asset == "ipsoft":
        pcoc_c = getChangeCoC("ipsoft", "corp", year)
        pcoc_nc = getChangeCoC("ipsoft", "noncorp", year)
        peatr = getChangeEATR("ipsoft", year)
    elif asset == "ipart":
        pcoc_c = getChangeCoC("ipart", "corp", year)
        pcoc_nc = getChangeCoC("ipart", "noncorp", year)
        peatr = getChangeEATR("ipart", year)
    pinv = (pcoc_c * elast_coc_corp * corpshare +
            pcoc_nc * elast_coc_nc * noncorpshare +
            peatr * selast_mne * mneshare)
    return pinv

def allInvChanges(elast_coc_corp, elast_coc_nc, selast_mne):
    """
    This function calculates the percent change in investment in each asset
    type for all years startyear-2027. All years beyond 2027 use the same
    result as in 2027.
    """
    assert startyear in range(2015, 2027)
    assert elast_coc_corp <= 0
    assert elast_coc_nc <= 0
    assert selast_mne <= 0
    pch_equip = np.zeros(14)
    pch_struc = np.zeros(14)
    pch_rentres = np.zeros(14)
    pch_iprd = np.zeros(14)
    pch_ipsoft = np.zeros(14)
    pch_ipart = np.zeros(14)
    for year in range(2014, startyear):
        pch_equip[year-2014] = 0
        pch_struc[year-2014] = 0
        pch_rentres[year-2014] = 0
        pch_iprd[year-2014] = 0
        pch_ipsoft[year-2014] = 0
        pch_ipart[year-2014] = 0
    for year in range(startyear, 2028):
        pch_equip[year-2014] = getChangeInv("equip", year, elast_coc_corp,
                 elast_coc_nc, selast_mne)
        pch_struc[year-2014] = getChangeInv("struc", year, elast_coc_corp,
                 elast_coc_nc, selast_mne)
        pch_rentres[year-2014] = getChangeInv("rentres", year, elast_coc_corp,
                   elast_coc_nc, selast_mne)
        pch_iprd[year-2014] = getChangeInv("iprd", year, elast_coc_corp,
                elast_coc_nc, selast_mne)
        pch_ipsoft[year-2014] = getChangeInv("ipsoft", year, elast_coc_corp,
                  elast_coc_nc, selast_mne)
        pch_ipart[year-2014] = getChangeInv("ipart", year, elast_coc_corp,
                 elast_coc_nc, selast_mne)
    results = pd.DataFrame({"Year": range(2014, 2028),
                            "pch_equip": pch_equip,
                            "pch_struc": pch_struc,
                            "pch_rentres": pch_rentres,
                            "pch_iprd": pch_iprd,
                            "pch_ipsoft": pch_ipsoft,
                            "pch_ipart": pch_ipart})
    results.to_csv("intermediate_results/invresults.csv", index=False)
    return None

