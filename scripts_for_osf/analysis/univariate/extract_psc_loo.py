# extract_psc_loo
# extract psc using leave one run out technique
# written by MH, adapted from YFL
# to run: python extract_psc_loo.py

import os
import re
from save_gii import extract_gii
from save_gii import save_gii
from irnx_utils import create_dir
import numpy as np
import pandas as pd

# set directory
wd = ""
os.chdir(wd)

# function to perform leave one run out univariate analysis
# get fixed effects model for every configuration of leave one run out
def loo_ffx(runs,ptp_n,hemis,ffx_name,flevel):

	for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
		for hh in hemis:
			# create all versions of ffx without the left out run
			for rr in runs:

				ffx_dir = "/export/bedny/Projects/IRNX/%s/%s/%s_exclude%.2d.%s.ffx"%(subj,flevel,ffx_name,rr,hh)
				if not os.path.isdir(ffx_dir):
					this_cmd = "fixedfx %s %s \""%(hh,ffx_dir)
					for ffxrr in runs:
						if ffxrr==rr:
							continue
						this_cmd += "/export/bedny/Projects/IRNX/%s/%s/%s_%.2d.%s.glm "%(subj,flevel,ffx_name,ffxrr,hh)
					this_cmd +="\""
					os.system(this_cmd)
	return

# function to extract PSC for given conditions from given vertices
def leave_one_run_out(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_name,flevel):

	# now that you have ffx ready, proceed with analyses involving specific ROIs
	for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
		for hh in hemis:
			for pp in parcels:
				for c_name,cc in zip(c_names,c_nums):

					mask = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/ROI/All_ROIs/%s_%s.shape.gii"%(pp,hh)))

					for rr in runs:

						# select top vtx based on the selected contrast
						con_zstat = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/%s/%s/%s_exclude%.2d.%s.ffx/zstat%d.func.gii"%(subj,flevel,ffx_name,rr,hh,cc)))
						mask_idx = np.array(range(len(mask)))
						mask_idx = mask_idx[mask>0]
						zstat_masked = con_zstat[mask>0]
						if c_name == "mech_vs_bio" or c_name == "phys_vs_soc":
							zstat_masked = zstat_masked*-1
						if top_n == 5:
							top_n_ex = int(0.05*len(zstat_masked))
						elif top_n == 10:
							top_n_ex = int(0.1*len(zstat_masked))
						elif top_n == 11111:
							top_n_ex = len(zstat_masked)
						else:
							top_n_ex = top_n
						selected_idx = mask_idx[zstat_masked.argsort()[-top_n_ex:]]
						con_zstat[selected_idx] = 999
						con_zstat[con_zstat!=999] = 0
						con_zstat[con_zstat==999] = 1
						save_gii(con_zstat,"%s/LOO_fROIs/%s_%s_%s_top%d_exclude%.2d.gii"%(subj,pp,hh,c_name,top_n,rr))

						# print statement for tracking purposes
						print("\n##### roi is %s %s number voxels is %d#####\n"%(pp,hh,top_n_ex))

						for cond_grp in cond_grps:
							if cond_grp == "biomech":
								cmd = "roi_extract --mode=\"classic fir hrf\" --roi=%s/LOO_fROIs/%s_%s_%s_top%d_exclude%.2d.gii --runs="%(subj,pp,hh,c_name,top_n,rr)
								cmd += "\"/export/bedny/Projects/IRNX/%s/preproc/ir_%.2d.feat/%s.32k_fs_LR.surfed_data.func.gii\" "%(subj,rr,hh)

								conds = ["bio","mech","ncm","ncb","magic"]

								for cond in conds:
									cmd += "--cond="
									cmd += "\"%s: "%cond+"/export/bedny/Projects/IRNX/%s/timing/ir_%.2d-%s.txt"%(subj,rr,cond)+"\" "

								cmd += "--out=%s/LOO_fROIs/%s_%s_%s_conds=%s_top%d_exclude%.2d"%(subj,pp,hh,c_name,cond_grp,top_n,rr)
								os.system(cmd)

							elif cond_grp == "socphys" and subj != "IRNX_24":
								cmd = "roi_extract --mode=\"classic fir hrf\" --roi=%s/LOO_fROIs/%s_%s_%s_top%d_exclude%.2d.gii --runs="%(subj,pp,hh,c_name,top_n,rr)
								cmd += "\"/export/bedny/Projects/IRNX/%s/preproc/sp_%.2d.feat/%s.32k_fs_LR.surfed_data.func.gii\" "%(subj,rr,hh)
								#cmd += "\" "

								conds = ["belief","phys"]

								for cond in conds:
									cmd += "--cond="
									cmd += "\"%s: "%cond+"/export/bedny/Projects/IRNX/%s/timing/sp_%.2d-%s.txt"%(subj,rr,cond)+"\" "

								cmd += "--out=%s/LOO_fROIs/%s_%s_%s_conds=%s_top%d_exclude%.2d"%(subj,pp,hh,c_name,cond_grp,top_n,rr)
								os.system(cmd)

						print(cmd)
	return

# function to compile the results
def compile_LOO(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps):

	for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
		for hh in hemis:
			for pp in parcels:
				for c_name in c_names:
					for cond_grp in cond_grps:

						if cond_grp == "biomech":
							file_len = 15
						elif cond_grp == "socphys":
							file_len = 20

						print("here's where error happened:\n")
						print("%s_%s_%s_%s_%s"%(subj,hh,pp,c_name,cond_grp))

						# grab all filenames
						root, dirs, files = os.walk("%s/LOO_fROIs/"%subj).next()
						match_dirs = [i for i in dirs if "%s_%s_%s_conds=%s_top%d_exclude"%(pp,hh,c_name,cond_grp,top_n) in i]

						# grab PSC
						csv_collect = []
						for count,md in enumerate(match_dirs):
							temp_csv = pd.read_csv("%s/LOO_fROIs/%s/fir_results.csv"%(subj,md))
							csv_collect.append(temp_csv)

						# take average
						sum_vals = 0
						for temp in csv_collect:

							sum_vals = sum_vals + temp.iloc[:,3:file_len]
							print(sum_vals)

						print(sum_vals)
						print(len(csv_collect))
						mean_vals = sum_vals/len(csv_collect)

						# save
						mean_vals.to_csv("%s/LOO_fROIs/psc_fir/%s_%s_%s_%s_conds=%s_top%d_avg.csv"%(subj,subj,pp,hh,c_name,cond_grp,top_n))

	return


# to run!

# PC illness > mech
ns = [5]
for top_n in ns:

	runs=[1,2,3,4,5,6]
	ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25]
	hemis=["lh","rh"]
	parcels=["PC","TPJ"]
	c_names=["bio_vs_mech"]
	c_nums=[6]
	cond_grps=["biomech"]
	ffx_name="ir"
	flevel="firstlevel_motspik"

	# get leave one out ffx (only need to run once)
	loo_ffx(runs,ptp_n,hemis,ffx_name)

	# extract psc
	leave_one_run_out(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_name,flevel)

	# average and format resulting PSC
	compile_LOO(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps)

# PPA mech > illness
ns = [5]
for top_n in ns:

	runs=[1,2,3,4,5,6]
	ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
	hemis=["lh","rh"]
	parcels=["PPAa","physicsComb"]
	c_names=["mech_vs_bio","mech_vs_noncaus"]
	c_nums=[6,9]
	cond_grps=["biomech"]
	ffx_name="ir"
	flevel="firstlevel_motspik"

	leave_one_run_out(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_name,flevel)
	compile_LOO(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps)
