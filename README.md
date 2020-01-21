# tax-distributor

This code runs the distributional and growth analysis in Kallen and Mathur (2018). 

# Current status

The model can be run in full. However, it remains under development. We hope to incorporate the following improvements:
 - Equity imputation improvements
   - The current version uses deteministic methods. This should be modified to a pseudorandom imputation using pre-generated random numbers.
   - We will improve the specific details of imputation to more fully utilize comparable measures in the PUF and SCF. 

# Model dependencies:
 - Python 3.6 or higher, using Anaconda packages
 - `taxcalc`, version 0.21.0, embedded here (for consistency)
 - IRS public use file for 2011, with modifications using `taxdata`, version as of PR [#283](https://github.com/PSLmodels/taxdata/pull/283)
 - SCF data files for 2016 in Stata format, including the summary extract public data file (`rscfp2016.dta`) and the full public data set (`p16i6.dta`)
 - Save these data files in the `data_files` folder.

Warning: If you have the conda taxcalc package installed, it may conflict with the local saved version 0.21.0. If the `main_executor.py` file imports the wrong version of taxcalc, it will not run (due to deprecation of the `Behavior` class).
# How to use the model

tax-distributor is run from the `main_executor.py` file. Once you open this file, the first changes to make are to correct the paths to the relevant ones on your computer.

The main file defines a Calculator for pre-TCJA law (calc_pre) and a Calculator for post-TCJA law (calc_tcja). It later makes alternative versions of these in different programs, but all such versions use current law for the TCJA and use the policy dictionary `param` for pre-TCJA law. If you wish to use alternative policy comparisons, modify these with care.

You also need to specify the change in corporate tax revenue in each year, also in the main file.

To run the dynamic model, you should specify changes to corporate and noncorporate business tax rules. The baseline (pre-TCJA) is in `policy_corp_base.csv` and `policy_noncorp_base.csv`. The reform (TCJA) is in `policy_corp_ref.csv` and `policy_noncorp_ref.csv`. 

To do the analysis of the SCF data, use `data_files\scf_analysis.do`.

Finally, you can modify the main assumptions we use, in `assumptions.py`. 




