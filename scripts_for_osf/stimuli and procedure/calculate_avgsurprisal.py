### calculate_avgsurprisal.py ###
# purpose: calculate average surprisal of stimulus sentences for both main
# 		   and localizer experiments
# written by MH

import os
import pandas as pd
import numpy as np
import math
import time
import statistics
import getngrams
import pickle

# set directory

wd = "" # file path
os.chdir(wd)

# main stim

s1_surp, s2_surp, comb_surp = [],[],[]
n = 2 # bigram surprisal

# open dict
with open('gramDict_combined.pickle', 'rb') as f:
	gramDict = pickle.load(f)

# read in csv with sentences
sentencepairs = np.genfromtxt("curr_stim.csv",delimiter = ',',dtype=str,encoding='utf-8-sig')

# each row is a pair of sentences
for count,sentencepair in enumerate(sentencepairs):

	print("Working on row %d\n"%count)
	which_pair = 0

	# get individual sentences within pair
	for sentence in sentencepair:

		# get arr of words; remove period from last word
		words = sentence.split()
		words[len(words)-1] = words[len(words)-1].strip(".")

		# get grams
		test_grams = [words[i:i+n] for i in range(len(words)-n+1)]
		test_grams = [" ".join(test_grams[i]) for i in range(len(test_grams))]
		grams_surp = []

		# get surprisal
		for test_gram in test_grams:
			grams_surp.append(gramDict[test_gram][2])

		# append mean freq across words to appropriate array
		if which_pair == 0:
			s1_surp.append(np.nanmean(grams_surp))
		else:
			s2_surp.append(np.nanmean(grams_surp))

		which_pair+=1

	# get combined avg surprisal across both sentences
	comb_surp.append(statistics.mean([s1_surp[count],s2_surp[count]]))

#  write results to csv
pd.DataFrame({'s1_surp': s1_surp, 's2_surp': s2_surp, 'comb_surp': comb_surp}).to_csv("surprisal_results_2grams.csv")

# localizer stim

n = 2 # bigram surprisal

# open dict
with open('gramDict_combined.pickle', 'rb') as f:
	gramDict = pickle.load(f)

# read in csv with sentences
sentences = np.genfromtxt("curr_stim_loc_nc.csv",delimiter = ',',dtype=str,encoding='utf-8-sig')

s_surp = []

# each row is a pair of sentences
for count,sent in enumerate(sentences):

	print("Working on row %d\n"%count)
	sentence = sent

	# get arr of words; remove period from last word
	words = sentence.split()
	words[len(words)-1] = words[len(words)-1].strip(".")

	# get grams
	test_grams = [words[i:i+n] for i in range(len(words)-n+1)]
	test_grams = [" ".join(test_grams[i]) for i in range(len(test_grams))]
	grams_surp = []

	# get surprisal
	for test_gram in test_grams:
		grams_surp.append(gramDict[test_gram][2])

	# append mean freq across words to appropriate array
	s_surp.append(np.nanmean(grams_surp))

#  write results to csv
pd.DataFrame({'s_surp': s_surp}).to_csv("surprisal_results_2grams_loc.csv")
