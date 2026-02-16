# get_slmvpa_commands.py
# prepare commands for searchlight MVPA
# written by MH

import os
import numpy as np

os.chdir('/export/bedny/Projects/IRNX/')

# job for searchlight mvpa
subs = ["IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11",
          "IRNX_12","IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17",
          "IRNX_18","IRNX_19","IRNX_20","IRNX_22","IRNX_23","IRNX_24",
          "IRNX_25","IRNX_26"]
hemis = ["lh","rh"]
radius = 10
test = "causality" #bioncb, bioncm
val1 = "causal"
val2 = "noncausal"

# permutation test
filename = 'Jobs/mvpa/sj_sl_mvpa_permtest_%s.txt'%test
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:

	for sub in subs:
		for hemi in hemis:
			the_cmd = "python Scripts/mvpa/1map_per_run_nonnorm/sj_sl_mvpa_perm_test.py --np=1 %s %s %d %s %s %s\n"%(sub,hemi,radius,test,val1,val2)
				
			f.write(the_cmd)

f.close()

# perform correction
filename = 'Jobs/mvpa/sj_sl_mvpa_correction_1.txt'
f = open(filename, 'a')
f.close()

tests = ["biomech","bioncb","bioncm","causality"]

with open(filename, 'w') as f:

	for test in tests:
		for hemi in hemis:
			the_cmd = "python Scripts/mvpa/1map_per_run_nonnorm/pymvpa_sl_correction_betamaps.py --np=1 %s %s\n"%(test,hemi)
				
			f.write(the_cmd)

f.close()
