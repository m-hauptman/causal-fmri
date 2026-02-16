# sl_correction_betamaps.py
# run permutation correction of MVPA searchlight results on group level
# MH adapted from GE

"""
Usage: sl_correction.py [--np=<np>] <testtype> <hemi>

Options:
  --np=<np>  Number of processes to open in parallel [default: 16].

Useful terms:
    meanmap: pymvpa dsets of group result map to be corrected (accuracy map)
    perms:    pymvpa dset with all perms per subject, each as a sample, with subject number in sa.chunks (make sure input here has proper feature (fa) and dataset (a) attributes, perhaps take them from mean_map
    NN:       Nearest neighbor clustering method - determines what voxels are contiguous / count as a cluster, 1: touch sides, 3: sides,edges,corners
    feature_thresh_prob,n_bootstrap, fwe_rate: see pymvpa doc for GroupClusterThreshold()

"""

from docopt import docopt
args = docopt(__doc__)

import warnings
with warnings.catch_warnings():
  warnings.simplefilter("ignore")
  import numpy as np
  import pandas as pd
  import mvpa2.suite as ms
  import npdl_utils as nu
  import mvpa2.algorithms.group_clusterthr as gct
  import pprocess # this allows you to run stuff on different cores

import os
study_dir = '/export/bedny/Projects/IRNX/'
os.chdir(study_dir)

# Read command line args.
n_proc = int(args['--np'])
testtype = args['<testtype>']
hemi = args['<hemi>']
out_prefix = 'Group/mvpa_betamaps_all_nonnorm/n=20/searchlight/{}_{}-10.0mm_sl-n=20-clustercorrected'.format(testtype, hemi)

subs = ["IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11",
          "IRNX_12","IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17",
          "IRNX_18","IRNX_19","IRNX_20","IRNX_22","IRNX_23","IRNX_24",
          "IRNX_25","IRNX_26"]

#-------------------------------------------------------------------------------
# Load data
#-------------------------------------------------------------------------------

# First, load averaged accuracy map and store as Dataset
meanmap_name = 'Group/mvpa_betamaps_all_nonnorm/n=20/searchlight/{}_{}-10.0mm_sl-acc-combined_n=20.func.gii'.format(testtype, hemi)
meanmap = nu.img_read(meanmap_name)
meanmap = ms.Dataset(meanmap)

# Next, load permuted maps. These were created in a previous step.
# Create pymvpa dset with all perms per subject, each as a sample, with subject number in sa.chunks
print 'Loading data...'
num_perms = 100
all_funcs, all_subs = [],[]
for sub in subs:
   all_subs = all_subs + ([sub] * num_perms)
   for perm in range(1, num_perms+1):
      func_ind_f = '{}/sl_permtests/{}-10.0mm_sl-{}-acc_perm_test-{}.func.gii'.format(sub, testtype, hemi, perm)
      func_ind = nu.img_read(func_ind_f)
      all_funcs.append(func_ind)
all_funcs = np.vstack(all_funcs)
all_verts = np.arange(func_ind.shape[1])

# Permutation dataset should contain the following:
# Data (all_funcs) of size X * Y, samples attribute (sa) of size X, features attribute (fa) of size Y
# To clarify further: samples attribute of size X where X = number of subjects * number of permutations
perms = ms.Dataset(all_funcs,
            sa=dict(chunks=all_subs),
            fa=dict(fid=all_verts))

#-------------------------------------------------------------------------------
# Run two-step correction
#-------------------------------------------------------------------------------

# GroupClusterThreshold object, which specifies number of desired bootstrap samples, vertex wise threshold, cluster size threshold
clthr = gct.GroupClusterThreshold(n_bootstrap=10000,
                              feature_thresh_prob=0.001,
                              fwe_rate=0.05)#, n_proc=n_proc)

# Perform permutation procedure
clthr.train(perms)

# Threshold the original map
res = clthr(meanmap)
thr = res.fa.featurewise_thresh
acc_map = res.fa.clusters_fwe_thresh.reshape(-1)

#-------------------------------------------------------------------------------
# Save results
#-------------------------------------------------------------------------------

surf_path = 'SurfAnat/32k_fs_LR/surf/{}.midthickness.surf.gii'.format(hemi)

for map_name, sl_map in zip(['acc_map', 'thresh_map'], [acc_map, thr]):
   outf = '{}-{}.func.gii'.format(out_prefix, map_name)
   nu.img_save(outf, sl_map, surf_path)

clstr_info = res.a.clusterstats
pd.DataFrame(clstr_info).T.to_csv('{}-clusterinfo.csv'.format(out_prefix))
