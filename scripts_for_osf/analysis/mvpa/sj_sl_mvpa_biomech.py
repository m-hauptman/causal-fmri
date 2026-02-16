# sj_sl_mvpa_biomech.py
# run searchlight MVPA comparing illness-causal and mech-causal 
# MH adapted from GE

"""
Usage: sj_sl_mvpa_02_nv.py [--np=<np>] <subj> <hemi> <radius> <out-prefix>

Options:
  --np=<np>  Number of processes to open in parallel [default: 16].
"""

from docopt import docopt
args = docopt(__doc__)

# the warnings are **very** annoying!
import warnings
with warnings.catch_warnings():
  warnings.simplefilter("ignore")
  import numpy as np
  import mvpa2.suite as ms
  import nibabel as nib
  from nibabel import gifti
  from scipy.stats import binom
  import npdl_utils as nu
  from npdl_mvpa import CachedSurfaceQueryEngine as CSQE

import os
import re

study_dir = '/export/bedny/Projects/IRNX/'
os.chdir(study_dir)

# Read command line args.

nproc = int(args['--np'])
sub = args['<subj>']
hemi = args['<hemi>']
radius = float(args['<radius>'])
out_prefix = '{}/slmvpa_betamaps/{}-{}mm_sl-{}'.format(sub, args['<out-prefix>'], radius, hemi)

#------------------------------------------------------------------
# Load surface + searchlight
#------------------------------------------------------------------
print 'Loading surface and SLs...'
# Load subjects 32k_fs_LR midthickness surface.
# To be used in generating searchlight ROIs.
surf_path = 'SurfAnat/{}/surf/{}.32k_fs_LR.midthickness.surf.gii'.format(sub, hemi)
surf = gifti.read(surf_path)
coords, faces = [surf.darrays[i].data for i in 0, 1]
coords = coords.astype(np.float64)
faces = faces.astype(np.int32)
# Use pymvpa surface object
surf = ms.surf.Surface(coords, faces)
nverts = coords.shape[0]

# Initialize Surface-based query engine.
# The query engine returns a searchlight ROI for a given vertex, based on a
# supplied surface. The searchlight ROI is calculated as a circle on the
# subject's midthickness surface, using Dijkstra distance.
# surf_qe = ms.surfing.queryengine.SurfaceQueryEngine(surf, radius, fa_node_key='verts')

# There is an alternate method for finding searchlight ROIs. Rather than computing
# them on fly, we can load "cached" searchlight ROIs, based on 32k_fs_LR
# midthickness surface. This method is implemented in the CSQE class (cached
# surface query engine) in npdl_mvpa.py. It's noticeably faster. However, the
# searchlights are different from the other searchlight in a few important
# ways:
# - Searchlight circles are based on the group average 32k_fs_LR midthickness
#   surface, rather than on the subject's own anatomy, which is potentially less
#   accurate. However, searchlights won't be the same across people.
# - Searchlight circles are drawn using a geodesic distance algorithm, rather
#   than Dijkstra, which is potentially more accurate.
surf_qe = CSQE(hemi, radius, fa_node_key='verts')

# Get the cortex mask for this subject, based on their data coverage.
coverage_path = '{}/firstlevel_motspik/ir.{}.ffx/coverage.shape.gii'.format(sub, hemi)
coverage = nu.img_read(coverage_path).reshape(-1)
mask = (coverage == coverage.max()).astype(int)
mask_inds = mask.nonzero()[0]

#------------------------------------------------------------------
# Loading data
#------------------------------------------------------------------

# Load preprocessed, surface-mapped functional data as a (runs * TRs, verts) array.
print 'Loading data...'
num_runs = 6
funcs = []
for run in range(1, num_runs+1):
  func_f = 'mvpa_betamaps/zstat_maps/{}_zstat_run{}_{}.func.gii'.format(sub, run, hemi)
  func = nu.img_read(func_f)
  funcs.append(func)
funcs = np.vstack(funcs)

# Read sample attributes file.
attrs = np.genfromtxt('mvpa_betamaps/attributes/attributes.txt', dtype=object)
attrs = {'runs': attrs[:, 0].astype(int),'counts': attrs[:, 1].astype(int),
	'causality': attrs[:, 2].astype(str),'targets': attrs[:, 3].astype(str)}

# Create feature attributes (just vertex index for now).
feature_attrs = {'verts': np.arange(funcs.shape[1])}

# Create the pyMVPA Dataset object.
DS = ms.Dataset(funcs, sa=attrs, fa=feature_attrs)
#DS = ms.Dataset(funcs, sa=attrs)

# Remove unlabeled TRs and noun trs.
null_tr_mask = ((DS.sa['targets'].value == "bio") | (DS.sa['targets'].value == "mech"))
DS = DS[null_tr_mask, :]

#-------------------------------------------------------------------------------
# Searchlight classification (with cross-validation)
#-------------------------------------------------------------------------------

print 'Running searchlight classification with cross-validation...'
# Initialize classifier (linear svm).
classifier = ms.LinearCSVMC()

# Define permutation scheme.
# References in: Scripts/mvpa/sj_roi_perm_test_mvpa_02.py
# Use limit option to ensure that each run is permuted individually.
#permutator = ms.AttributePermutator('targets', count=num_perms, limit='runs')

# Note: as we'computing accuracy (not errors), we're interest in p-value
# measured from the right tail. This is different than what is outline on the
# pymvpa website.
#distr_est = ms.MCNullDist(permutator, tail='right', enable_ca=['dist_samples'])

# Define cross-validation scheme (even/odd runs).
cross_validator = ms.CrossValidation(classifier,
    ms.NFoldPartitioner(attr='runs'),
    errorfx=lambda p, t: np.mean(p == t),
    #null_dist=distr_est,
    enable_ca=['stats'])

# Define searchlight.
sl = ms.Searchlight(cross_validator, surf_qe, postproc=ms.mean_sample(), roi_ids=mask_inds, nproc=nproc)

# Run cross-validated searchlight classification.
results = sl(DS)
# Strip down to just the accuracy array.
acc_map = results.samples.reshape(-1)

#-------------------------------------------------------------------------------
# Inspect results
#-------------------------------------------------------------------------------

print 'Post-processing results...'
num_conds = 2.0
chance = 1. / num_conds
tests_per_chunk = [(DS.sa['runs'].value == i).sum() for i in [1,2,3,4,5,6]]
total_tests = sum(tests_per_chunk)

# extract the classification accuracy, averaged across runs
class_acc = results.samples[0, 0]

# Assuming binomial distribution
number_correct = int(np.round(class_acc * total_tests))
binom_pval = 1-binom.cdf(number_correct, total_tests, chance)
binom_logp = -np.log10(binom_pval)

#-------------------------------------------------------------------
# Save results
#------------------------------------------------------------------

print 'Saving data...'

# save sl map

for map_name, sl_map in zip(['acc', 'logp'], [acc_map, binom_logp]):
  img = np.zeros(nverts)
  img[mask_inds] = sl_map
  outf = '{}-{}.func.gii'.format(out_prefix, map_name)
  nu.img_save(outf, img, surf_path)
