### getngrams_caller_freq.py ###
# purpose: call RunQuery function to get frequency values from GoogleNgrams
#		   and save outputs
# written by MH

import os
import pandas as pd
import numpy as np
import math
import time
import statistics
import getngrams

# set directory
wd = "" # file path
os.chdir(wd)

# set year you want to select (2019=219)
startyr = 217
endyr = 220
s1_freq, s2_freq, comb_freq, freq0_words = [],[],[],[]

# either start anew or open old dict
wordDict = {}

with open('wordDict.pickle', 'rb') as f:
	wordDict = pickle.load(f)

# read in csv with stimuli sentences
sentencepairs = np.genfromtxt("curr_stim.csv",delimiter = ',',dtype=str)

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

		for word in words:

			# if word was already queried, save its freq value
			if wordDict.get(word) != None:
				words_freq.append(wordDict[word])

			else:
				# perform query
				time.sleep(10)
				params = "%s -corpus=eng_us_2019 -endYear=2019"%(word)
				df = getngrams.runQuery(params)

				# subset df to 2019 and take log of frequency value
				if not df.empty:
					result = -math.log(np.nanmean(df.iloc[startyr:endyr]["timeseries"]))
					wordDict[word] = result
				else:
					freq0_words.append(word)
					result = np.nan

				words_freq.append(result)

		# append mean freq across words to appropriate array
		if which_pair == 0:
			s1_freq.append(np.nanmean(words_freq))
		else:
			s2_freq.append(np.nanmean(words_freq))

		which_pair+=1

	comb_freq.append(statistics.mean([s1_freq[count],s2_freq[count]]))

#  write results to csv
pd.DataFrame({'s1_freq': s1_freq, 's2_freq': s2_freq, 'comb_freq': comb_freq}).to_csv("wordfreq_results.csv")

# save dict with updated frequency values
with open('wordDict.pickle', 'wb') as f:
	pickle.dump(wordDict, f)
