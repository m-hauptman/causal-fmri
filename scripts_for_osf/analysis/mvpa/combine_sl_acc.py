# combine_sl_acc.py
# combine individual searchlight MVPA results to create map for visualization
# written by MH

import os
from save_gii import save_gii
from save_gii import extract_gii

# set working directory
os.chdir('/export/bedny/Projects/IRNX')

# set defaults
subs = ["IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11",
          "IRNX_12","IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17",
          "IRNX_18","IRNX_19","IRNX_20","IRNX_22","IRNX_23","IRNX_24",
          "IRNX_25","IRNX_26"]
hemis = ["lh","rh"]
tests = ["causality","biomech","bioncb","bioncm"]

# get average acc map

for test in tests:
    for hemi in hemis:
        sub_arr = []
        for sub in subs:
            acc_map = "%s/slmvpa_betamaps/%s-10.0mm_sl-%s-acc.func.gii" %(sub,test,hemi)
            temp = extract_gii(acc_map)
            sub_arr.append(temp)

        # average
        avg_arr = np.average(sub_arr,axis=0)
        save_dir = "Group/mvpa_betamaps_all_nonnorm/n=20/searchlight/%s_%s-10.0mm_sl-acc-combined_n=20.func.gii"%(test,hemi)
        save_gii(avg_arr, save_dir)
