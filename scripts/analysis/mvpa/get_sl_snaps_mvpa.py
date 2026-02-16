# get_sl_snaps_mvpa.py
# get snapshots of searchlight MVPA results
# written by MH

import os
from save_gii import save_gii
from save_gii import extract_gii

# set working directory
os.chdir('/export/bedny/Projects/IRNX')

# get snaps of group maps

# uncorrected
filename = 'Jobs/mvpa/grp_sl_freeview_snaps_job_n=20_2.txt'
f = open(filename, 'a')
f.close()

views = ["lateral","medial","inferior","posterior"]
hemis = ["lh","rh"]
tests = ["causality","biomech","bioncb","bioncm"]
thr = [0.55,0.65]

with open(filename, 'w') as f:
	for hemi in hemis:
		for test in tests:
			for view in views:
				stat_map = "Group/mvpa_betamaps_all_nonnorm/n=20/searchlight/%s_%s-10.0mm_sl-acc-combined_n=20.func.gii"%(test,hemi)
				snap_name = "Snapshots/n=20/mvpa_searchlight/grp_sl_10mm-%s-%s-%s_%f-%f"%(test,hemi,view,thr[0],thr[1])
				the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=%f,%f -viewport 3d -view %s -ss %s -noquit\n"%(hemi,hemi,stat_map,thr[0],thr[1],view,snap_name)
				f.write(the_cmd)
				f.write("freeview -unload surface\n")
f.close()

# permutation corrected
filename = 'Jobs/mvpa/grp_sl_corrected_freeview_snaps_job_n=20_0.5thr.txt'
f = open(filename, 'a')
f.close()

views = ["lateral","medial","inferior","posterior"]
hemis = ["lh","rh"]
tests = ["causality","biomech","bioncb","bioncm"]
thr = [0.50,0.65]

with open(filename, 'w') as f:
	for hemi in hemis:
		for test in tests:
			for view in views:
				stat_map = "Group/mvpa_betamaps_all_nonnorm/n=20/searchlight/%s_%s-10.0mm_sl-n=20-clustercorrected-acc_clust_vals.func.gii"%(test,hemi)
				snap_name = "Snapshots/n=20/mvpa_searchlight/corrected_grp_sl_10mm-%s-%s-%s_%f-%f"%(test,hemi,view,thr[0],thr[1])
				the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=%f,%f -viewport 3d -view %s -ss %s -noquit\n"%(hemi,hemi,stat_map,thr[0],thr[1],view,snap_name)
				f.write(the_cmd)
				f.write("freeview -unload surface\n")
f.close()
