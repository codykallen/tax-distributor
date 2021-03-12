# -*- coding: utf-8 -*-
"""
This file compiles all of the assumptions and decisions for comparing filers.
"""
# Our preferred distributional comparison decisions
RANKING = {"w_adult": 1, "w_child": 1, "elast_size": 0.5}
SCALING = {"w_adult": 1, "w_child": 1, "elast_size": 1}
EXCLUDING = ["neginc"]
SCREENING = ["", ""]

# Share of corporate tax burden going to each group
hhshare = 0.668920896
npshare = 0.047345087
fedshare = 0.001261413
slgshare = 0.085778364
rowshare = 0.196694239
# Share of corporate income paid out as dividends
divshare = 0.44
# Shares of capital gains realized as short-term and long-term gains. 
# Remaining amount is held until death
cgsplit = [0.034, 0.496]

# Choose distribution inputs and assumptions of burden split
# Assumption for how nonprofit stakholders split a windfall
nonprofit_split = {"services": 0.208, "compensation": 0.78, "donors": 0, "foreign": 0.012}
# Assumption of how state/local governments "spend" a windfall
slgov_split = {"benefits": 0.0, "compensation": 1.0, "taxes": 0.0}

# Behavioral responses
# Choose year for effects to begin (to prevent response to retroactive changes)
startyear = 2018
# Set elasticity of taxable income (w.r.t. 1 - MTR)
eti = 0.25
# Elasticities of investmnet w.r.t. user cost of capital
ELAST_INV_CORP = -1.0
ELAST_INV_NONCORP = -1.0
# Semielasticity of MNE investment w.r.t. the EATR
SELAST_INV_MNE = -3.0
