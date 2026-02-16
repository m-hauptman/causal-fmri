# extract_psc_noloo
# extract psc, not using leave one run out technique
# written by MH, adapted from YFL
# to run: python extract_psc_noloo.py

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

# function to extract PSC for given conditions from given vertices
def extract_roi(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_names,flevel):

	for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
		for hh in hemis:
			for pp in parcels:
				for c_name,cc,ffx_name in zip(c_names,c_nums,ffx_names):

					mask = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/ROI/All_ROIs/%s_%s.shape.gii"%(pp,hh)))

					# select top vtx based on the specified contrast
					if subj == "IRNX_24" and ffx_name == "sp":
						con_zstat = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/IRNX_24/firstlevel_motspik/sp_02.lh.glm/stats/zstat3.func.gii"))
					else:
						con_zstat = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/%s/%s/%s.%s.ffx/zstat%d.func.gii"%(subj,flevel,ffx_name,hh,cc)))
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
					save_gii(con_zstat,"%s/fROIs_noLOO/%s_%s_%s_top%d.gii"%(subj,pp,hh,c_name,top_n))

					print("\n##### roi is %s %s number voxels is %d#####\n"%(pp,hh,top_n_ex))

					for cond_grp in cond_grps:

						cmd = "roi_extract --mode=\"classic fir hrf\" --roi=%s/fROIs_noLOO/%s_%s_%s_top%d.gii --runs=\""%(subj,pp,hh,c_name,top_n)
						cmd += " ".join(["/export/bedny/Projects/IRNX/%s/preproc/ir_%.2d.feat/%s.32k_fs_LR.surfed_data.func.gii"%(subj,rr,hh) for rr in range(1,runs+1)])
						cmd += "\" "

						if cond_grp == "biomech":
							conds = ["bio","mech","ncm","ncb","magic"]
						elif cond_grp == "objplc":
							conds = ["OBJ","PLC","bio","ncm","ncb","magic"]
						elif cond_grp == "illcaus":
							conds = ["PATH","LIFE","ENV","GEN","mech","ncm","ncb","magic"]

						for cond in conds:
							cond_list = "--cond=\""+cond+": "
							cond_list += " ".join(["%s/timing/ir_%.2d-%s.txt"%(subj,rr,cond) for rr in range(1,runs+1)])
							cond_list += "\" "
							cmd += cond_list

						cmd += "--out=%s/fROIs_noLOO/%s_%s_%s_conds=%s_top%d_noLOO"%(subj,pp,hh,c_name,cond_grp,top_n)
						os.system(cmd)
						print(cmd)

	return

# function to compile the results
def compile_LOO_copy(top_n,ptp_n,hemis,parcels,c_names,cond_grps):

	for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
		for hh in hemis:
			for pp in parcels:
				for c_name in c_names:
					for cond_grp in cond_grps:

						# grab all filenames
						root, dirs, files = os.walk("%s/fROIs_noLOO/"%subj).next()
						match_dirs = [i for i in dirs if "%s_%s_%s_conds=%s_top%d_noLOO"%(pp,hh,c_name,cond_grp,top_n) in i]
						print(match_dirs)

						# grab PSC
						csv_collect = []
						for count,md in enumerate(match_dirs):
							# save
							cmd = "cp %s/fROIs_noLOO/%s/fir_results.csv %s/fROIs_noLOO/psc_fir/%s_%s_%s_%s_conds=%s_top%d.csv"%(subj,md,subj,subj,pp,hh,c_name,cond_grp,top_n)
							os.system(cmd)
							print(cmd)
	return

# to run!

# set number of vertices
ns = [10,1000]

for top_n in ns:

	# pc/tpj
	runs=6
	ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
	hemis=["lh","rh"]
	parcels=["PC","TPJ"]
	c_names=["soc_vs_phys","caus_vs_rest","bio_vs_mech"]
	c_nums=[3,14,6]
	cond_grps=["biomech"]
	ffx_names=["sp","ir","ir"]
	flevel="firstlevel_motspik"

	# call functions
	extract_roi(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_names,flevel)
	compile_LOO_copy(top_n,ptp_n,hemis,parcels,c_names,cond_grps)

	# lang/log (all lang)
	runs=6
	ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
	hemis=["lh"]
	parcels=["Logic", "Lang"]
	c_names=["log_vs_lang","lang_vs_math"]
	c_nums=[6,4]
	cond_grps=["biomech"]
	ffx_names=["ll","ll"]
	flevel="firstlevel_motspik"

	extract_roi(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_names,flevel)
	compile_LOO_copy(top_n,ptp_n,hemis,parcels,c_names,cond_grps)

	# frontal, temporal lang
	runs=6
	ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
	hemis=["lh"]
	parcels=["FrontLang","TempLang"]
	c_names=["lang_vs_math"]
	c_nums=[4]
	cond_grps=["biomech"]
	ffx_names=["ll"]
	flevel="firstlevel_motspik"

	extract_roi(top_n,runs,ptp_n,hemis,parcels,c_names,c_nums,cond_grps,ffx_names,flevel)
	compile_LOO_copy(top_n,ptp_n,hemis,parcels,c_names,cond_grps)
