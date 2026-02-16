### getngrams_dict_surprisal.py ###
# purpose: call RunQuery function to get frequency values for bigrams, calculate
#		   surprisal values and save outputs
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

# merge freq dictionaries
def merge_dicts(dict1, dict2):
	for i in dict2.keys():
		dict1[i]=dict2[i]
	return dict1

# set year you want to select (2019=219)
startyr = 217
endyr = 220
dict_type = "merge"
n = 2
freq0_grams, alltest_grams = [],[]

# either start anew, open old dict, or merge dicts
if dict_type == "new":
	gramDict = {}
elif dict_type == "old":
	with open('gramDict_combined.pickle', 'rb') as f:
		gramDict = pickle.load(f)
elif dict_type == "merge":
	with open('gramDict_combined.pickle', 'rb') as f:
		dict1 = pickle.load(f)
	with open('wordDict.pickle', 'rb') as f:
		dict2 = pickle.load(f)
	gramDict = merge_dicts(dict1, dict2)

# read in csv with sentences
sentencepairs = np.genfromtxt("curr_stim.csv",delimiter = ',',dtype=str,encoding='utf-8-sig')

# each row is a pair of sentences
for count,sentencepair in enumerate(sentencepairs):

	print("Working on row %d\n"%count)

	# get individual sentences within pair
	for sentence in sentencepair:

		# get arr of words; remove period from last word
		words = sentence.split()
		words[len(words)-1] = words[len(words)-1].strip(".")

		# get grams: target gram and gram with one fewer than target
		test_grams = [words[i:i+n] for i in range(len(words)-n+1)]
		alltest_grams = alltest_grams + test_grams
		oneoff_grams = [words[i:i+(n-1)] for i in range(len(words)-(n-1)+1)]
		grams = test_grams + oneoff_grams
		grams = [" ".join(grams[i]) for i in range(len(grams))]

		# perform query
		for gram in grams: #freq0_grams

			# if dict does not already contain this gram, run query
			if gramDict.get(gram) == None:

				# decide which gram to query
				query_gram = gram
				print("querying %s\n"%query_gram)

				time.sleep(10)
				params = "%s -corpus=eng_us_2019 -endYear=2019"%(query_gram)
				df = getngrams.runQuery(params)

				# subset df to 2019 and take log
				if not df.empty and not np.nanmean(df.iloc[startyr:endyr]["timeseries"]) == 0.0:
					prob = np.nanmean(df.iloc[startyr:endyr]["timeseries"])
					logprob = -math.log(prob)
					gramDict[gram] = [prob,logprob]
				else:
					freq0_grams.append(gram)

# if gram had no entries in corpus, set to nan
for gram in freq0_grams:
	gramDict[gram] = [np.nan]

# at this point, all grams entered in corpus should be in dict.
# unite list of strings first
alltest_grams = [" ".join(alltest_grams[i]) for i in range(len(alltest_grams))]
alltest_grams = np.unique(alltest_grams)
failed_grams = []
for gram in alltest_grams:
	splitgram = gram.split()
	oneoff_gram = " ".join(splitgram[0:len(splitgram)-1])

	# if possible to calculate surprisal, do so
	if not math.isnan(gramDict[gram][0]) and not math.isnan(gramDict[oneoff_gram][0]):

		testgram_prob = gramDict[gram][0]
		oneoffgram_prob = gramDict[oneoff_gram][0]

		# calculate surprisal
		surprisal = -math.log((testgram_prob/oneoffgram_prob),2)
		if len(gramDict[gram]) < 3:
			gramDict[gram].append(surprisal)
		else:
			gramDict[gram][2] = surprisal
	# else, keep track of grams where surprisal could not be calculated
	else:
		failed_grams.append(gram)

# now, get max suprisal value
surp_max = 0
prob_min = 0
the_gram = np.nan

for gram in alltest_grams:
	item = gramDict[gram]
	if not math.isnan(gramDict[gram][0]):
		if item[2] > surp_max:
			surp_max = item[2]
			prob_min = item[0]
			the_gram = gram

# set grams without surprisal value to highest surprisal value
for failed_gram in failed_grams:
	gramDict[failed_gram] = [np.nan,np.nan,surp_max]

# save dict
with open('gramDict_combined.pickle', 'wb') as f:
	pickle.dump(gramDict, f)

# deal with error
# shave down each dict entry to its original first two items.
for key,vals in gramDict.items():
	gramDict[key] = vals[:2]

# get test grams.
alltest_grams = []
for count,sentencepair in enumerate(sentencepairs):

	# get individual sentences within pair
	for sentence in sentencepair:

		# get arr of words; remove period from last word
		words = sentence.split()
		words[len(words)-1] = words[len(words)-1].strip(".")

		# get grams: target gram and gram w one fewer than target
		test_grams = [words[i:i+n] for i in range(len(words)-n+1)]
		alltest_grams = alltest_grams + test_grams

# save
alltest_grams = [" ".join(alltest_grams[i]) for i in range(len(alltest_grams))]
pd.DataFrame({'testgrams': alltest_grams}).to_csv("alltest_grams.csv")
pd.DataFrame({'failedgrams': failed_grams}).to_csv("failed_grams.csv")
