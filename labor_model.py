# -*- coding: utf-8 -*-
"""
Created on Wed Nov  7 08:41:54 2018

@author: cody_
"""
# Set elasticity of taxable income (w.r.t. 1 - MTR)
eti = 0.25
# Choose year for effects to begin (to prevent response to retroactive changes)
startyear = 2018
"""
Section 1. Calculation of the labor response
    This section calculates the percent change in labor supply for each year,
    using the elasticity of taxable income with respect to the marginal 
    net-of-tax rate. The results are then stored for the growth model.
"""

def calcLaborResponse(calc1, calc2, elast_sub):
    """
    Calculates the labor response from calc1 to calc2, using elast_sub as the
    substition elasticity (percent change in labor supply w.r.t. percent
    change in marginal net-of-tax rate).
    """
    assert elast_sub >= 0
    # Get marginal tax rates
    mtr1p = calc1.mtr('e00200p', calc_all_already_called=True)[2]
    mtr1s = calc1.mtr('e00200s', calc_all_already_called=True)[2]
    mtr2p = calc2.mtr('e00200p', calc_all_already_called=True)[2]
    mtr2s = calc2.mtr('e00200s', calc_all_already_called=True)[2]
    # Get labor income
    wagep = calc1.array('e00200p')
    wages = calc1.array('e00200s')
    wgt = calc1.array('s006')
    mars = calc1.array('MARS')
    # Calculate each unit's labor response
    primary_response = ((1 - mtr2p) / (1 - mtr1p) - 1) * elast_sub
    second_response = np.where(mars == 2, ((1 - mtr2s) / (1 - mtr1s) - 1) * elast_sub, 0.)
    response = (sum((primary_response * wagep + second_response * wages) *
                    wgt) / sum((wagep + wages) * wgt))
    return response

def allLaborChanges(calcA, calcB, elast_sub):
    """
    Calculates and saves the labor effect for every year.
    """
    assert startyear in range(2015, 2027)
    assert elast_sub >= 0
    calc1 = copy.deepcopy(calcA)
    calc2 = copy.deepcopy(calcB)
    labeffect = []
    for year in range(2014, 2028):
        if year < startyear:
            labeffect.append(0)
        else:
            calc1.advance_to_year(year)
            calc1.calc_all()
            calc2.advance_to_year(year)
            calc2.calc_all()
            labeffect.append(calcLaborResponse(calc1, calc2, elast_sub))
    labresults = pd.DataFrame({"Year": range(2014, 2028),
                               "pch_labor": labeffect})
    labresults.to_csv("intermediate_results/laborresults.csv", index=False)
    print("Labor response calculated and saved")
    return None

"""
Section 2. Calculation of other weighted average marginal tax rates.
"""

def calcTauNC(calc):
    """
    Calculates the effective marginal tax rate on pass-through business
    income.
    """
    mtr1 = calc.mtr('e00900p')[2]
    mtr2 = calc.mtr('e26270')[2]
    mtr3 = calc.mtr('e02000')[2]
    inc1 = np.abs(calc.array('e00900'))
    inc2 = np.abs(calc.array('e26270'))
    inc3 = np.abs(calc.array('e02000') - calc.array('e26270'))
    wgt = calc.array('s006')
    MTR = sum((mtr1 * inc1 + mtr2 * inc2 + mtr3 * inc3) * wgt) / sum((inc1 + inc2 + inc3) * wgt)
    return MTR

def calcTauDnc(calc):
    """
    Calculates the effective marginal tax rate on pass-through debt.
    """
    taxableshare = 0.763
    mtr1 = calc.mtr('e00300')[2]
    inc1 = calc.array('e00300')
    wgt = calc.array('s006')
    MTR = taxableshare * sum(mtr1 * inc1 * wgt) / sum(inc1 * wgt)
    return MTR

def calcTauDc(calc):
    """
    Calculates the effective marginal tax rate on corporate debt.
    """
    taxableshare = 0.523
    mtr1 = calc.mtr('e00300')[2]
    inc1 = calc.array('e00300')
    wgt = calc.array('s006')
    MTR = taxableshare * sum(mtr1 * inc1 * wgt) / sum(inc1 * wgt)
    return MTR

def calcTauE(calc):
    """
    Calculates the effective marginal tax rate on corporate equity income.
    """
    taxableshare = 0.572
    ltshare = 0.496
    stshare = 0.034
    divshare = 0.44
    h_scg = 0.5
    h_lcg = 8.0
    r_e = 0.082
    mtr1 = calc.mtr('p22250')[2]
    mtr2 = calc.mtr('p23250')[2]
    mtr3 = calc.mtr('e00650')[2]
    mtr4 = calc.mtr('e00600')[2]
    inc1 = np.abs(calc.array('p22250'))
    inc2 = np.abs(calc.array('p23250'))
    inc3 = calc.array('e00650')
    inc4 = calc.array('e00600') - calc.array('e00650')
    wgt = calc.array('s006')
    qdivshare = sum(inc3 * wgt) / sum((inc3 + inc4) * wgt)
    # Accrual-effective tax rate on short-term gains
    tau_scg1 = sum(mtr1 * inc1 * wgt) / sum(inc1 * wgt)
    tau_scg = (1 - (np.log(np.exp((1 - divshare) * r_e * h_scg) *
                           (1 - tau_scg1) + tau_scg1) /
               ((1 - divshare) * r_e * h_scg)))
    # Accrual-effective tax rate on long-term gains
    tau_lcg1 = sum(mtr2 * inc2 * wgt) / sum(inc2 * wgt)
    tau_lcg = (1 - (np.log(np.exp((1 - divshare) * r_e * h_lcg) *
                           (1 - tau_lcg1) + tau_lcg1) /
               ((1 - divshare) * r_e * h_lcg)))
    tau_cg = ltshare * tau_lcg + stshare * tau_scg
    tau_qdiv = sum(mtr3 * inc3 * wgt) / sum(inc3 * wgt)
    tau_nqdiv = sum(mtr4 * inc4 * wgt) / sum(inc4 * wgt)
    tau_div = qdivshare * tau_qdiv + (1 - qdivshare) * tau_nqdiv
    tau_taxableequity = divshare * tau_div + (1 - divshare) * tau_cg
    MTR = taxableshare * tau_taxableequity
    return MTR
    
def allOwnerTaxes(calcA, calcB):
    """
    Calculates and saves the labor effect for every year.
    """
    mtr_nc_base = []
    mtr_e_base = []
    mtr_d_c_base = []
    mtr_d_nc_base = []
    mtr_nc_ref = []
    mtr_e_ref = []
    mtr_d_c_ref = []
    mtr_d_nc_ref = []
    calc1 = copy.deepcopy(calcA)
    calc2 = copy.deepcopy(calcB)
    for year in range(2014, 2028):
        calc1.advance_to_year(year)
        calc1.calc_all()
        calc2.advance_to_year(year)
        calc2.calc_all()
        mtr_nc_base.append(calcTauNC(calc1))
        mtr_nc_ref.append(calcTauNC(calc2))
        mtr_e_base.append(calcTauE(calc1))
        mtr_e_ref.append(calcTauE(calc2))
        mtr_d_c_base.append(calcTauDc(calc1))
        mtr_d_c_ref.append(calcTauDc(calc2))
        mtr_d_nc_base.append(calcTauDnc(calc1))
        mtr_d_nc_ref.append(calcTauDnc(calc2))
    results = pd.DataFrame({"Year": range(2014, 2028),
                            "tau_nc_base": mtr_nc_base, "tau_nc_ref": mtr_nc_ref,
                            "tau_e_base": mtr_e_base, "tau_e_ref": mtr_e_ref,
                            "tau_dc_base": mtr_d_c_base, "tau_dc_ref": mtr_d_c_ref,
                            "tau_dnc_base": mtr_d_nc_base, "tau_dnc_ref": mtr_d_nc_ref})
    results.to_csv("intermediate_results/owner_level_taxes.csv", index=False)
    print("Owner level taxes calculated and saved")
    return None



