### calculate_avgfreq.py ###
# purpose: calculate average frequency of stimulus sentences for both main
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

# main exp stim

s1_freq, s2_freq, comb_freq = [],[],[]

# open dict with word frequencies
with open('wordDict.pickle', 'rb') as f:
	wordDict = pickle.load(f)

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
		words_freq = []

		# get word's logprob value
		for word in words:
			words_freq.append(wordDict[word][1])

		# append mean freq across words to appropriate array
		if which_pair == 0:
			s1_freq.append(np.nanmean(words_freq))
		else:
			s2_freq.append(np.nanmean(words_freq))

		which_pair+=1

	# get combined avg frequency across both sentences
	comb_freq.append(statistics.mean([s1_freq[count],s2_freq[count]]))

#  write results to csv
pd.DataFrame({'s1_freq': s1_freq, 's2_freq': s2_freq, 'comb_freq': comb_freq}).to_csv("wordfreq_results.csv")

# localizer stim

with open('wordDict.pickle', 'rb') as f:
	wordDict = pickle.load(f)

s_freq = []

# read in csv with sentences
sentences = np.genfromtxt("curr_stim_loc_nc.csv",delimiter = ',',dtype=str,encoding='utf-8-sig')

# each row is a pair of sentences
for count,sent in enumerate(sentences):

	print("Working on row %d\n"%count)

	sentence = sent

	# get arr of words; remove period from last word
	words = sentence.split()
	words[len(words)-1] = words[len(words)-1].strip(".")
	words_freq = []

	# get word's logprob value
	for word in words:
		words_freq.append(wordDict[word][1])

	# append mean freq across words to appropriate array
	s_freq.append(np.nanmean(words_freq))

#  write results to csv
pd.DataFrame({'s_freq': s_freq}).to_csv("wordfreq_results_loc.csv")
