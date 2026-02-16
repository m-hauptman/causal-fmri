# sj_roi_mvpa_biomech.py
# run MVPA comparing illness-causal and mech-causal in given fROI
# MH adapted from GE

"""
Usage: sj_roi_mvpa_biomech.py [--num-perm=<n>] <subj> <hemi> <roi> <contrast> <v_num> <out-prefix>

Options:
  --num-perm=<n>    Number of permutations to perform [default: 1000].
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
  #from matplotlib import pyplot as plt
  from scipy.stats import binom
  import npdl_utils as nu

import os

study_dir = '/export/bedny/Projects/IRNX'
os.chdir(study_dir)

# Read command line args.

num_perms = int(args['--num-perm'])

sub = args['<subj>']
hemi = args['<hemi>']
roi_name = args['<roi>']
contrast = args['<contrast>']
v_num = args['<v_num>']

roi = "{}/fROIs_noLOO/{}_{}_{}_top{}.gii".format(sub, roi_name, hemi, contrast, v_num)

roi = nu.img_read(roi).reshape(-1)
out_prefix = '{}/mvpa_zbetamaps/{}_{}_{}_{}_top{}_nonnorm'.format(sub, args['<out-prefix>'], roi_name, hemi, contrast, v_num)

#-------------------------------------------------------------------------------
# Loading data
#-------------------------------------------------------------------------------

# Load concatenated zstat maps
# Stack them in a (runs * TRs, verts) array.
print('Loading data...')
num_runs = 6
funcs = []
for run in range(1, num_runs+1):
  func_f = 'mvpa_betamaps/zstat_maps/{}_zstat_run{}_{}.func.gii'.format(sub, run, hemi)
  func = nu.img_read(func_f)
  # Mask with ROI
  func = func[:, roi==1]
  funcs.append(func)
funcs = np.vstack(funcs)

# Read attributes files.
attrs = np.genfromtxt('mvpa_betamaps/attributes/attributes.txt', dtype=object)
attrs = {'runs': attrs[:, 0].astype(int), 'chunks': attrs[:, 1].astype(int),
         'causality': attrs[:, 2].astype(str),'targets': attrs[:, 3].astype(str)}

# Create the pyMVPA Dataset object.
DS = ms.Dataset(funcs, sa=attrs)

# no normalization!
# ms.zscore(DS, chunks_attr='runs')

# Remove unlabeled TRs and noun trs.
null_tr_mask = ((DS.sa['targets'].value == "bio") | (DS.sa['targets'].value == "mech"))
DS = DS[null_tr_mask, :]

#-------------------------------------------------------------------------------
# Classification (with cross-validation)
#-------------------------------------------------------------------------------

print('Running classification with permutation testing...')
# Initialize classifier (linear svm).
classifier = ms.LinearCSVMC()

# Define permutation scheme.
# From: http://www.pymvpa.org/tutorial_significance.html#null-hypothesis-testing
# Use limit option to ensure that each run is permuted individually.
permutator = ms.AttributePermutator('targets', count=num_perms, limit='runs')
# Note that we're computing accuracy, not errors so we're interested in p-value
# measured from the right tail. This is different than what is outlined on the
# pymvpa website.
distr_est = ms.MCNullDist(permutator, tail='right', enable_ca=['dist_samples'])

# Define cross-validation scheme (even/odd runs).
cross_validator = ms.CrossValidation(classifier,
    ms.NFoldPartitioner(attr='runs'),
    errorfx=lambda p, t: np.mean(p == t),
    postproc=ms.mean_sample(),
    null_dist=distr_est,
    enable_ca=['stats'])

# Run cross-validated classification.
results = cross_validator(DS)

#-------------------------------------------------------------------------------
# Inspect results
#-------------------------------------------------------------------------------

print('Post-processing results and saving data...')
num_conds = 2.0
chance = 1. / num_conds
tests_per_chunk = [(DS.sa['runs'].value == i).sum() for i in [0, 1]]
total_tests = sum(tests_per_chunk)

# extract the classification accuracy, averaged across runs.
class_acc = results.samples[0, 0]

#-------------------------------------------------------------------------------
# Calculate significance
#-------------------------------------------------------------------------------

# Assuming binomial distribution.
number_correct = int(np.round(class_acc * total_tests))
binom_pval = 1-binom.cdf(number_correct, total_tests, chance)
binom_logp = -np.log10(binom_pval)

# Using empirical null distribution.
perm_pval = cross_validator.ca.null_prob.samples[0, 0]
perm_logp = -np.log10(perm_pval)

#-------------------------------------------------------------------------------
# Save results
#-------------------------------------------------------------------------------

# Save results summary
results_header = "# Subject hemi ROI Total.acc V_num Binom.log10pval Perm.log10pval"
results = [sub, hemi, roi_name, class_acc, v_num, binom_logp, perm_logp]
results = '{:s} {:s} {:s} {:.3f} {:s} {:.3f} {:.3f}'.format(*results)
results = results_header + '\n' + results + '\n'

results_f = open('{}-acc.txt'.format(out_prefix), 'w')
results_f.write(results)
results_f.close()

# Save permutation null distribution
null_dist = cross_validator.null_dist.ca.dist_samples.samples.reshape(-1)
null_dist_f = '{}-null_dist.txt'.format(out_prefix)
np.savetxt(null_dist_f, null_dist, fmt='%.6f')
