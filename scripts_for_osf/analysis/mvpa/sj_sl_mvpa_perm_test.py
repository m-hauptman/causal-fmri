# sj_sl_mvpa_perm_test.py
# run permutation test of searchlight MVPA in individual participants to generate
# null distribution
# MH adapted from GE

"""
Usage: sj_sl_mvpa_perm_test_03_anpl.py [--np=<np>] <subj> <hemi> <radius> <out-prefix> <val1> <val2>

Options:
  --np=<np>  Number of processes to open in parallel [default: 16].
"""

from docopt import docopt
args = docopt(__doc__)

import matplotlib as mp
mp.use('Agg')

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
  import pprocess # this allows you to run stuff on different cores
  #from matplotlib import pyplot as plt

import datetime
import os
import re

study_dir = '/export/bedny/Projects/IRNX/'
os.chdir(study_dir)

# Read command line args.

nproc = int(args['--np'])
sub = args['<subj>']
hemi = args['<hemi>']
radius = float(args['<radius>'])
test = args['<out-prefix>']
val1 = args['<val1>']
val2 = args['<val2>']
out_prefix = '{}/sl_permtests/{}-{}mm_sl-{}'.format(sub, args['<out-prefix>'], radius, hemi)

#------------------------------------------------------------------
# Load surface + searchligt
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
# Loading "cached" searchlight ROIs, based on 32k_fs_LR
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

if test == "causality":
  attrs = {'runs': attrs[:, 0].astype(int),'counts': attrs[:, 1].astype(int),
  'targets': attrs[:, 2].astype(str),'conds': attrs[:, 3].astype(str)}
else:
  attrs = {'runs': attrs[:, 0].astype(int),'counts': attrs[:, 1].astype(int),
  'causality': attrs[:, 2].astype(str),'targets': attrs[:, 3].astype(str)}

# Create feature attributes (just vertex index for now).
feature_attrs = {'verts': np.arange(funcs.shape[1])}

# Create the pyMVPA Dataset object.
DS = ms.Dataset(funcs, sa=attrs, fa=feature_attrs)

# Remove unlabeled TRs and noun trs.
null_tr_mask = ((DS.sa['targets'].value == val1) | (DS.sa['targets'].value == val2))
DS = DS[null_tr_mask, :]

# Permute attributes
num_perms = 100
permutator = ms.AttributePermutator('targets', count=num_perms, limit='runs')
perm_attrs = permutator.generate(DS)

# Initialize classifier (linear svm).
classifier = ms.LinearCSVMC()

# Define cross-validation scheme
cross_validator = ms.CrossValidation(classifier,
    ms.NFoldPartitioner(attr='runs'),
    errorfx=lambda p, t: np.mean(p == t),
    enable_ca=['stats'])

# Define searchlight.
sl = ms.Searchlight(cross_validator, surf_qe, postproc=ms.mean_sample(), roi_ids=mask_inds, nproc=nproc)

# Initialize permutation counter
perm_count=1

for ds in perm_attrs:

  print 'Permutation {} ...'.format(perm_count)
  print datetime.datetime.now()

  DS = ds
  print 'DS attributes'
  print DS.sa
  #-------------------------------------------------------------------------------
  # Searchlight classification (with cross-validation)
  #-------------------------------------------------------------------------------

  print 'Running searchlight classification with cross-validation...'

  # Run cross-validated searchlight classification.
  results = sl(DS)
  print 'Strip down to just the accuracy array.'
  acc_map = results.samples.reshape(-1)

  #-------------------------------------------------------------------------------
  # Inspect results
  #-------------------------------------------------------------------------------

  print 'Post-processing results...'
  num_conds = 2.0

  # extract the classification accuracy, averaged across runs
  class_acc = results.samples[0, 0]

  #-------------------------------------------------------------------
  # Save results
  #------------------------------------------------------------------

  print 'Saving data...'

  # Save sl map
  for map_name, sl_map in zip(['acc'], [acc_map]):
    img = np.zeros(nverts)
    img[mask_inds] = sl_map
    outf = '{}-{}_perm_test-{}.func.gii'.format(out_prefix, map_name, perm_count)
    nu.img_save(outf, img, surf_path)

  perm_count += 1
