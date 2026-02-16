# written by Miriam, 2.2023

import os
import numpy as np

os.chdir('/export/bedny/Projects/IRNX/')

# job for roi mvpa

subs = ["IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11",
          "IRNX_12","IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17",
          "IRNX_18","IRNX_19","IRNX_20","IRNX_22","IRNX_23","IRNX_24",
          "IRNX_25","IRNX_26"]
v_nums = [300]

# soc 
hemis = ["lh","rh"]
tests = ["bioncm"]
rois = ["TPJ","PC"]
contrasts = ["caus_vs_rest","soc_vs_phys"]

filename = 'Jobs/mvpa/sj_roi_mvpa_job_n=20_all3.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:

	for sub in subs:
		for hemi in hemis:
			for test in tests:
				for contrast in contrasts:
					for roi in rois:
						for v_num in v_nums:

							the_cmd = "python Scripts/mvpa/1map_per_run_nonnorm/sj_roi_mvpa_%s.py %s %s %s %s %d %s\n"%(test,sub,hemi,roi,contrast,v_num,test)
						
							f.write(the_cmd)

f.close()


# lang/log
hemis = ["lh"]
tests = ["bioncm"]
rois =["Lang","Logic"]
contrasts = ["lang_vs_math","log_vs_lang"]

filename = 'Jobs/mvpa/sj_roi_mvpa_job_n=20_all4.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:

	for sub in subs:
		for hemi in hemis:
			for test in tests:
				for contrast,roi in zip(contrasts,rois):
					for v_num in v_nums:

						the_cmd = "python Scripts/mvpa/1map_per_run_nonnorm/sj_roi_mvpa_%s.py %s %s %s %s %d %s\n"%(test,sub,hemi,roi,contrast,v_num,test)
					
						f.write(the_cmd)

f.close()