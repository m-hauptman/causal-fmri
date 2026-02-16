### getngrams_dict_freq.py ###
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
import pickle

# set directory
wd = "" # file path
os.chdir(wd)

# set year you want to select (2019=219)
startyr = 217
endyr = 220
new_dict = False
freq0_words = []

# either start anew or open old dict
if new_dict:
	wordDict = {}
else:
	with open('wordDict.pickle', 'rb') as f:
		wordDict = pickle.load(f)

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
		words_freq = []

		for word in words: #freq0_words

			# if dict does not already contain this word, run query
			if wordDict.get(word) == None:

				# decide which word to query (issue w apostrophes)
				if word != "sister's" and word != "brother's" and word != "mother's" and word != "Now" and word != "women's" and word != "x_ray":
					query_word = word
				elif word == "sister's":
					query_word = "sister"
				elif word == "brother's":
					query_word = "brother"
				elif word == "mother's":
					query_word = "mother"
				elif word == "Now":
					query_word = "now"
				elif word == "women's":
					query_word = "women"
				elif word == "x_ray":
					query_word = "xray"

				time.sleep(10)
				print("querying %s\n"%query_word)
				params = "%s -corpus=eng_us_2019 -endYear=2019"%(query_word)
				df = getngrams.runQuery(params)

				# subset df to 2019 and take log
				if not df.empty:
					prob = np.nanmean(df.iloc[startyr:endyr]["timeseries"])
					logprob = -math.log(prob)
					wordDict[word] = [prob,logprob]
				else:
					freq0_words.append(word)

# save dict
with open('wordDict.pickle', 'wb') as f:
	pickle.dump(wordDict, f)
