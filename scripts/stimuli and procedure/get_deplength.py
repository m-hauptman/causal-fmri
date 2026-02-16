### get_deplength.py ###
# purpose: calculate syntactic dependency length of stimuli sentences using
#		   the Stanford Parser
# written by MH

import os
import numpy as np
import re
import pandas as pd

# set directory

wd = "" # file path
os.chdir(wd)

# read in csv with sentences and convert to txt file
sentencepairs = np.genfromtxt("curr_stim.csv",delimiter = ',',dtype=str)
sentencepairs = sentencepairs.flatten()
np.savetxt("curr_stim.txt",sentencepairs,delimiter=" ",fmt='%s')

# bash commands to run parser
# main stim
# ./stanford-parser-full-2020-11-17/lexparser.sh curr_stim.txt > dependencies.txt
# loc stim
# ./stanford-parser-full-2020-11-17/lexparser.sh curr_stim_loc.txt > dependencies_loc.txt

# main stim analysis
# open file
with open('dependencies.txt') as f:
	lines = f.readlines()

# get absolute value of differences in syntactic position between words
lengths = {}
count = 0
sent_length = []
for line in lines:

	# sentences are separated by a newline
	if line != '\n':
		ints = re.findall(r'\d+', line)
		length = abs(int(ints[0])-int(ints[1]))
		sent_length.append(length)
	else:
		lengths[str(count)] = sent_length
		count=count+1
		sent_length=[]

# get averages per sentence and save
avgs = []
for key,vals in lengths.items():
	avg = sum(vals) / float(len(vals))
	avgs.append(avg)

# get average of pairs
counter = 0
avgs_1 = []
avgs_2 = []
comb_avgs = []
for x in range(len(avgs)):
	if counter > (len(avgs)-1):
		break
	avg1 = avgs[counter]
	avg2 = avgs[counter+1]
	comb_avg = (avg1+avg2)/2
	avgs_1.append(avg1)
	avgs_2.append(avg2)
	comb_avgs.append(comb_avg)
	counter = counter+2

# save
pd.DataFrame({'s1_deplength':avgs_1,'s2_deplength':avgs_2,'comb_deplength': comb_avgs}).to_csv("dependency_results.csv")

# loc stim analysis
# open file
with open('dependencies_loc.txt') as f:
	lines = f.readlines()

# get absolute value of differences in syntactic position between words
lengths = {}
count = 0
sent_length = []
for line in lines:

	if line != '\n':
		ints = re.findall(r'\d+', line)
		length = abs(int(ints[0])-int(ints[1]))
		sent_length.append(length)
	else:
		lengths[str(count)] = sent_length
		count=count+1
		sent_length=[]

# get averages and save
avgs = []
for key,vals in lengths.items():
	avg = sum(vals) / float(len(vals))
	avgs.append(avg)

# save
pd.DataFrame({'sent_deplength':avgs}).to_csv("dependency_results_loc.csv")
