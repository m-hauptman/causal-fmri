### mainexp_randomize.py ###
# purpose: create main exp trial order for individual participant via
#          pseudorandomization
# written by MH

from psychopy import gui
import pandas as pd
import numpy as np
import os
import time
import random
import math
from numpy.random import permutation

# set directory
wd = "" # file path
os.chdir(wd)

# initialize some information
dlg = gui.Dlg(title="Info")
dlg.addField("Order number", "0")
dlg.addField("Random seed", "0")
dlg.addField("Stimuli group",choices=["A","B"])
dlg.addField("PTP ID","IRNX")

info = dlg.show()
if dlg.OK:
    print(info)

# gather inputs
which_runs = int(info[0])
random_seed = int(info[1])
group_ID = info[2]
ptp_ID = info[3]

# set order of the runs based on input
# use existing order skeleton, then select corresponding trials randomly
print("GETTING TRIALS.\n")
run_orders = pd.read_excel("orders/allorders_skeleton_main.xlsx").iloc[:33,0:6].values.T
shuffle = pd.read_excel("orders/allruns_skeleton_main.xlsx").iloc[:6,0:6].values.T[which_runs]
run_orders = [run_orders[int(i)-1] for i in shuffle]

run_collection = {}
run_names = ["1","2","3","4","5","6"]
converged = False
attempt = 1

# grab random trials, make sure group_name condition is satisified
while converged == False:

    converged = True

    trials = pd.read_excel("main_roster_%s.xlsx"%group_ID)

    for run_count,run_order in enumerate(run_orders):

        run_order = [i for i in run_order if math.isnan(i)==False]
        grp_list = []
        prev = ""

        # prepare df for each run
        run_df = pd.DataFrame(columns=["CAUSALITY", "type_id", "id", "UNIQUE_ID", "GROUP1", "GROUP2", "GROUP_NAME", "COND1", "COND2", "type", "Group", "SENT1", "SENT2", "SENT2 DEPL", "TARGET", "NAMES", "SENT2 DEPL TYPE", "GENDER", "MECHTYPE", "ILLTYPE", "ILLCAUS", "ILLINF", "ILLORG", "truth"])

        for ord_count,ord in enumerate(run_order):

            # if at the beginning, start afresh with rest trial
            if ord == 0:
                temp_row = pd.DataFrame({"CAUSALITY":0, "type_id":0, "id":0, "UNIQUE_ID":0, "GROUP1":0, "GROUP2":0, "GROUP_NAME":0, "COND1":0, "COND2":0, "type":0, "Group":0, "SENT1":0, "SENT2":0, "SENT2 DEPL":0, "TARGET":0, "NAMES":0, "SENT2 DEPL TYPE":0, "GENDER":0, "MECHTYPE":0, "ILLTYPE":0, "ILLCAUS":0, "ILLINF":0, "ILLORG":0, "truth":100},index=[ord_count])

            # otherwise, select trial that matches with order
            else:
                random.seed(random_seed)
                sub_trials = trials[(trials["type"]==ord)]
                aa = trials[(trials["type"]==ord)]
                if ord != 5:
                     sub_trials = sub_trials[~np.isin(sub_trials["GROUP_NAME"], grp_list) & (sub_trials["group_name_type"]!=prev)]
                if len(sub_trials) == 0:
                    converged = False
                    print("didn't converge. run_order is %d. trying again.\n"%(run_count))
                    break
                rand_idx = random.randint(0,len(sub_trials)-1)
                temp_row = sub_trials.iloc[[rand_idx]]
                if ord != 5:
                    grp_list.append(temp_row["GROUP_NAME"].values[0])
                    prev = temp_row["group_name_type"].values[0]
                id = temp_row["id"].values[0]
                trials=trials[trials["id"]!=id]
                random_seed+=1

            run_df = pd.concat([run_df,temp_row],ignore_index = True)


        if converged == False:
            break

        run_collection[run_names[run_count]] = run_df

print("DONE GETTING TRIALS. SAVING. RANDOM SEED IS %d\n"%random_seed)

# save trial order csv
os.mkdir("orders/%s"%ptp_ID)
for count,run in enumerate(run_collection):
    run_collection[run].to_csv("orders/%s/%s_main_ord_group%s_run%d.csv"%(ptp_ID,ptp_ID,group_ID,count))
