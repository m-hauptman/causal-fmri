# compare_ill_soc_PC.py
# compare top illness vs. top mentalizing vertices in PC
# written by MH

import os
from save_gii import extract_gii
from save_gii import save_gii
import numpy as np
import pandas as pd

# set directory and defaults
wd = ""
os.chdir(wd)
top_ns = [5]
ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
hemis=["lh","rh"]
parcels=["PC"]
c_names=["bio_vs_mech"]
c_nums=[6,3]
cond_grps=["biomech"]
ffx_names=["ir","sp"]
flevel="firstlevel_motspik"

# visualize
filename = 'Jobs/basic_pipeline/groupstats/n=20/illsoc_union_snaps_tpj.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:
    for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
        for hh in hemis:
            for pp in parcels:
                for top_n in top_ns:

                    # get union map in indvidual participants
                    # one value for top illness, one for top ment., one for overlap
                    soc_map = np.array(extract_gii("%s/fROIs_noLOO/%s_%s_%s_top%f.gii"%(subj,pp,hh,"soc_vs_phys",top_n)))*15
                    ill_map = np.array(extract_gii("%s/fROIs_noLOO/%s_%s_%s_top%f.gii"%(subj,pp,hh,"bio_vs_mech",top_n)))*5
                    uni_map = soc_map+ill_map
                    uni_map = np.where(uni_map == 20,11,uni_map)
                    uni_name = "%s/fROIs_noLOO/%s_%s_%s_top%f.gii"%(subj,pp,hh,"illsoc_union",top_n)
                    save_gii(uni_map,uni_name)

                    # freeview command to take snap of union map
                    snap_name = "Snapshots/n=20/pc_vis/%s_%s_%s_top%f_ill_vs_soc"%(subj,pp,hh,top_n)
                    the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=5,15:overlay_color=colorwheel:overlay_method=linear -viewport 3d -view lateral -ss %s -noquit\n"%(hh,hh,uni_name,snap_name)
                    f.write(the_cmd)
                    f.write("freeview -unload surface\n")
f.close()

# coordinate analysis: identify peaks for each contrast in each ptp

# defaults
ptp_n=[5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,22,23,24,25,26]
c_names=["bio_vs_mech","soc_vs_phys"]
c_nums=[6,3]
ffx_names=["ir","sp"]
flevel="firstlevel_motspik"
top_n = 1
hh = "lh"
pp = "PC"

for subj in ["IRNX_%.2d"%ii for ii in ptp_n]:
    for (c_name,cc,ffx_name) in zip(c_names,c_nums,ffx_names):

        mask = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/ROI/All_ROIs/%s_%s.shape.gii"%(pp,hh)))

        # select top vtx based on the specified contrast
        if subj == "IRNX_24" and ffx_name == "sp":
            con_zstat = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/IRNX_24/firstlevel_motspik/sp_02.lh.glm/stats/zstat3.func.gii"))
        else:
            con_zstat = np.squeeze(extract_gii("/export/bedny/Projects/IRNX/%s/%s/%s.%s.ffx/zstat%d.func.gii"%(subj,flevel,ffx_name,hh,cc)))
        mask_idx = np.array(range(len(mask)))
        mask_idx = mask_idx[mask>0]
        zstat_masked = con_zstat[mask>0]

        # save map with just the one peak
        selected_idx = mask_idx[zstat_masked.argsort()[-top_n:]]
        con_zstat[selected_idx] = 999
        con_zstat[con_zstat!=999] = 0
        con_zstat[con_zstat==999] = 1
        save_gii(con_zstat,"%s/fROIs_noLOO/one_peak_%s_%s_%s.gii"%(subj,pp,hh,c_name))

        # mri surfcluster to identify the MNI coordinates of the peak
        the_cmd = "mri_surfcluster --in ./%s/fROIs_noLOO/one_peak_%s_%s_%s.gii --thmin 0.9 --thmax 1.1 --sign pos --no-adjust --subject 32k_fs_LR --hemi lh --minarea 0 --o ./%s/fROIs_noLOO/one_peak_%s_%s_%s_clust.func.gii --sum ./Group/pc_voxel_coords/%s_%s.txt"%(subj, pp, hh, c_name, subj, pp, hh, c_name, subj, c_name)
        os.system(the_cmd)
