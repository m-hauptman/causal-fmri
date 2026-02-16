# get_groupstats_snaps.py
# get whole cortex snapshots of univariate results
# written by MH

import os

# set directory
wd = ""
os.chdir(wd)

## whole cortex analyses for select contrasts ##
hemis = ["lh","rh"]
copes = ["cope6","cope7","cope8","cope9","cope10","cope11","cope12"]
views = ["posterior","lateral","medial","inferior"]
threshs = [5]
dir = "abs"
filename = 'Jobs/basic_pipeline/groupstats/n=20/fvw_snaps_forfigs5.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:
    for cope in copes:
        for hemi in hemis:
            for view in views:
                for thr in threshs:
                    tmp = "Group/groupstats/n=20/ir_n=20.%s.rfx/%s/con1/perm_5000_01_%s.sig.masked.mgh"%(hemi,cope,dir)
                    data = extract_gii(tmp)
                    stat_map = "Group/groupstats/n=20/ir_n=20.%s.rfx/%s/con1/perm_5000_01_%s.sig.masked.func.gii"%(hemi,cope,dir)
                    save_gii(data,stat_map)
                    snap_name = "Snapshots/n=20/groupstats_final/%s-fwer01-%s_1.3-%d_-%s-%s"%(cope,dir,thr,hemi,view)
                    the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=1.3,%d -viewport 3d -view %s -ss %s -noquit\n"%(hemi,hemi,stat_map,thr,view,snap_name)
                    f.write(the_cmd)
                    f.write("freeview -unload surface\n")

f.close()

## prior study PC rois on top ##
filename = 'Jobs/basic_pipeline/groupstats/n=20/old_PC_rois_medial.txt'
f = open(filename, 'a')
f.close()

hemis = ["rh","lh"]
cope = "cope6"

with open(filename, 'w') as f:
    for hemi in hemis:


        stat_map = "Group/groupstats/n=20/ir_n=20.%s.rfx/%s/con1/perm_5000_01_abs.sig.masked.func.gii"%(hemi,cope)
        snap_name = "Snapshots/n=20/groupstats/Fairhall_PC_thr2-5_%s-fwer01-abs_p01-%s"%(cope,hemi)
        the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=2,5:label=ROI/PC_prior_work/Fairhall_%s.label:label_color=yellow:label_outline=yes -viewport 3d -view medial -ss %s -noquit\n"%(hemi,hemi,stat_map,hemi,snap_name)
        f.write(the_cmd)
        f.write("freeview -unload surface\n")

        stat_map = "Group/groupstats/n=20/ir_n=20.%s.rfx/%s/con1/perm_5000_01_abs.sig.masked.func.gii"%(hemi,cope)
        snap_name = "Snapshots/n=20/groupstats/NV_PC_thr2-5_%s-fwer01-abs_p01-%s"%(cope,hemi)
        the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=2,5:label=ROI/PC_prior_work/NV_anpl_%s.label:label_color=yellow:label_outline=yes -viewport 3d -view medial -ss %s -noquit\n"%(hemi,hemi,stat_map,hemi,snap_name)
        f.write(the_cmd)
        f.write("freeview -unload surface\n")

f.close()

## localizers, one tailed ##
loc_names = ["sp","ll","ll"]
loc_copes = ["cope3","cope4","cope6"]
ns = [19,20,20]
hemis = ["lh","rh"]
views = ["lateral","medial"]
filename = 'Jobs/basic_pipeline/groupstats/n=20/fvw_snaps_0.01_uncor_all_loc.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:
    for name,cope,n in zip(loc_names,loc_copes,ns):

        for hemi in hemis:

            stat_map = "Group/groupstats/n=20/%s_n=%d.%s.rfx/%s/con1/sig.mgh"%(name,n,hemi,cope)
            out_map = "Group/groupstats/n=20/%s_n=%d.%s.rfx/%s/con1/sig_0.01_cluster20.func.gii"%(name,n,hemi,cope)

            the_cmd = "mri_surfcluster --in %s --thmin 2 --thmax 30 \
                    --sign abs --no-adjust --subject 32k_fs_LR --hemi %s \
                    --minarea 20 --o %s" %(stat_map,hemi,out_map)
            os.system(the_cmd)

            stat_map = "Group/groupstats/n=20/%s_n=%d.%s.rfx/%s/con1/sig_0.01_cluster20.func.gii"%(name,n,hemi,cope)
            out_map = "Group/groupstats/n=20/%s_n=%d.%s.rfx/%s/con1/NO_BLUE_sig_0.01_cluster20.func.gii"%(name,n,hemi,cope)

            tmp = extract_gii(stat_map)
            tmp[tmp<0] = 0
            save_gii(tmp,out_map)

            for view in views:
                stat_map = "Group/groupstats/n=20/%s_n=%d.%s.rfx/%s/con1/NO_BLUE_sig_0.01_cluster20.func.gii"%(name,n,hemi,cope)
                snap_name = "Snapshots/n=20/groupstats/all_loc/NO_BLUE_%s_%s-uncor01-cluster20-%s-%s"%(name,cope,hemi,view)
                the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=2,5 -viewport 3d -view %s -ss %s -noquit\n"%(hemi,hemi,stat_map,view,snap_name)

                f.write(the_cmd)
                f.write("freeview -unload surface\n")
f.close()

## prior study PPA rois on top ##

filename = 'Jobs/basic_pipeline/groupstats/n=20/PPA_mech_ventral2.txt'
f = open(filename, 'a')
f.close()

hemis = ["rh","lh"]
cope = "cope17"

with open(filename, 'w') as f:
    for hemi in hemis:

        stat_map = "Group/groupstats/n=20/ir_n=20.%s.rfx/cope6/con1/mechint_%s.func.gii"%(hemi,hemi)
        #stat_map = "Group/groupstats/n=20/ir_n=20_biovall.%s.rfx/%s/con1/perm_5000_01_pos.sig.masked.func.gii"%(hemi,cope)
        snap_name = "Snapshots/n=20/groupstats/anterior_PPA_int_thr1.3-5_%s-fwer01_p05-%s"%(cope,hemi)
        the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=1.3,5:label=ROI/PPA_anterior/NV_antPPA_%s.label:label_color=blue:label_outline=yes -viewport 3d -view inferior -ss %s -noquit\n"%(hemi,hemi,stat_map,hemi,snap_name)
        f.write(the_cmd)
        f.write("freeview -unload surface\n")

        snap_name = "Snapshots/n=20/groupstats/perceptual_PPA_int_thr1.3-5_%s-fwer01_p05-%s"%(cope,hemi)
        the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=1.3,5:label=ROI/PPA_perceptual/%s.CoS.PlaceSelectivity.Weiner_32k.label:label_color=blue:label_outline=yes -viewport 3d -view inferior -ss %s -noquit\n"%(hemi,hemi,stat_map,hemi,snap_name)
        f.write(the_cmd)
        f.write("freeview -unload surface\n")

f.close()

## intersection map of mech > nc, mech > bio ##

import copy
import numpy as np
hemis = ["lh","rh"]

filename = 'Jobs/basic_pipeline/groupstats/n=20/univ_intersection_mech_mean.txt'
f = open(filename, 'a')
f.close()

with open(filename, 'w') as f:
    for hemi in hemis:
        tmp = "Group/groupstats/n=20/ir_n=20.%s.rfx/cope6/con1/perm_5000_01_neg.sig.masked.func.gii"%hemi
        map1 = abs(np.squeeze(extract_gii(tmp)))
        tmp = "Group/groupstats/n=20/ir_n=20.%s.rfx/cope9/con1/perm_5000_01_pos.sig.masked.func.gii"%hemi
        map2 = np.squeeze(extract_gii(tmp))
        int_map = copy.deepcopy(map1)
        int_map[0:] = 0
        for i in range(len(map1)):
            if (map1[i] > 0) & (map2[i] > 0):
                int_map[i] = np.mean([map1[i],map2[i]])
        new_name = "Group/groupstats/n=20/ir_n=20.%s.rfx/cope6/con1/mechint_mean_%s.func.gii"%(hemi,hemi)
        save_gii(int_map, new_name)
        for view in views:
            snap_name = "Snapshots/n=20/groupstats/mechint_mean_cope8cope9-fwer01_1.3-5-%s-%s"%(hemi,view)
            the_cmd = "freeview -f /export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.inflated:curvature=/export/bedny/Projects/IRNX/SurfAnat/32k_fs_LR/surf/%s.curv:overlay=%s:overlay_threshold=1.3,5 -viewport 3d -view %s -ss %s -noquit\n"%(hemi,hemi,new_name,view,snap_name)
            f.write(the_cmd)
            f.write("freeview -unload surface\n")
f.close()
