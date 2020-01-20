clear all
** Build measures from underlying data
set maxvar 6000
use "p16i6.dta", clear
// Measure of comparable income
gen compincome = X5702 + X5704 + X5714 + X5706 + X5708 + X5710 + 5716 + X5722
// Amount in Roth IRA
gen rothira = X6551 + X6559 + X6567
// Amount in regular IRA
gen ira = X6553 + X6561 + X6569 + X6552 + X6560 + X6568
// Amount in Keogh account
gen keogh = X6554 + X6562 + X6570
replace keogh = 0 if keogh < 0
// Separate spending accounts by tax-preferred status (HSA, 529, Coverdell)
gen sav1 = 0
replace sav1 = X3730 if X3732==2
gen sav2 = 0
replace sav2 = X3736 if X3738==2
gen sav3 = 0
replace sav3 = X3742 if X3744==2
gen sav4 = 0
replace sav4 = X3748 if X3750==2
gen sav5 = 0
replace sav5 = X3754 if X3756==2
gen sav6 = 0
replace sav6 = X3760 if X3762==2
gen spendaccts_notax = sav1 + sav2 + sav3 + sav4 + sav5 + sav6
gen spendaccts_tax = X3730 + X3736 + X3742 + X3748 + X3754 + X3760 - spendaccts_notax
replace spendaccts_tax = 0 if spendaccts_tax < 0
// Other retirement savings accounts (401(k), 403(b), TSP, 457)
gen ret1 = 0
replace ret1 = X11032 if X11001==2
gen ret2 = 0
replace ret2 = X11132 if X11101==2
gen ret3 = 0
replace ret3 = X11332 if X11301==2
gen ret4 = 0
replace ret4 = X11432 if X11401==2
gen otherretaccts = ret1 + ret2 + ret3 + ret4
replace otherretaccts = 0 if otherretaccts < 0
// Total in savings accounts
gen totalinaccts = rothira + ira + keogh + spendaccts_notax + spendaccts_tax + otherretaccts
// Total that in accounts taxed at withdrawal
gen totaltaxdistribution = ira + keogh + otherretaccts + spendaccts_tax
gen disttaxshare = totaltaxdistribution / totalinaccts
// Save the results to add to main dataset
keep Y1 compincome disttaxshare
save "compincome.dta", replace


use "rscfp2016.dta", clear
merge 1:1 Y1 using "compincome.dta"
drop _merge

** Assign age groups
gen agecat = .
replace agecat = 0 if age < 35
replace agecat = 1 if age >= 35 & age < 45
replace agecat = 2 if age >= 45 & age < 55
replace agecat = 3 if age >= 55 & age < 65
replace agecat = 4 if age >= 65 & age < 75
replace agecat = 5 if age >= 75 & age < 100

sum hequity if agecat==0 [aweight=wgt]
sum hequity if agecat==1 [aweight=wgt]
sum hequity if agecat==2 [aweight=wgt]
sum hequity if agecat==3 [aweight=wgt]
sum hequity if agecat==4 [aweight=wgt]
sum hequity if agecat==5 [aweight=wgt]

** Assign income groups, nested in age groups
foreach i of numlist 0/5 {
gen compinc_`i' = compincome if agecat==`i'
xtile comppct_`i' = compinc_`i' [aweight=wgt], nq(100)
}
egen comppct = rowmean(comppct_0 comppct_1 comppct_2 comppct_3 comppct_4 comppct_5)
gen compinccat = .
replace compinccat = 0 if comppct >= 0 & comppct <= 20
replace compinccat = 1 if comppct > 20 & comppct <= 40
replace compinccat = 2 if comppct > 40 & comppct <= 60
replace compinccat = 3 if comppct > 60 & comppct <= 80
replace compinccat = 4 if comppct > 80 & comppct <= 90
replace compinccat = 5 if comppct > 90 & comppct <= 95
replace compinccat = 6 if comppct > 95 & comppct <= 99
replace compinccat = 7 if comppct == 100

** Adjustments: merge top two income categories for young group
ta compinccat agecat
replace compinccat = 6 if agecat==0 & compinccat==7
ta compinccat agecat

** Choose variables to export
// Having equity: hequity
// Equity amount (log), conditional on having equity
gen lequity = log(equity)
// Directly held equity share
gen deqshare = deq / equity
// Non-equity financial assets
gen oassets = fin - equity
gen hoassets = 0
replace hoassets = 1 if oassets>0
gen loassets = log(oassets)


// Save the results
collapse (mean) hequity lequity deqshare hoassets loassets disttaxshare (sd) s_equity=lequity s_oassets=loassets [aweight=wgt], by(agecat compinccat)
rename compinccat group_income
rename agecat group_age
rename hequity prob_stock
rename hoassets prob_oassets
export delimited using "scf_results.csv", replace

