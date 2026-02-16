### socphys_randomize.py ###
# purpose: create trial orders for socphys localizer via pseudorandomization
# written by MH

import pandas as pd
import numpy as np
import random
import os

# set directory
wd = "" # file path
os.chdir(wd)

# defaults
vers_per_ord = 6 # how many versions you want per order
run_len = 11
random_seed = 0
orders = [["01212212112", "02121121221"],
          ["02121121221", "01212212112"]]

# for each order
for which_ord in range(len(orders)):

    for vers in range(vers_per_ord):

        # initalize run and determine trial order
        print("WORKING ON VERSION %d, ORDER %d" %(vers,which_ord))
        startOver = False
        finished = False

        while startOver == False and finished == False:

            df = pd.read_excel("socphys_roster_2conds.xlsx")
            all_trials = pd.DataFrame()
            print("loading data\n")

            for run in range(len(orders[which_ord])):

                order = "".join(orders[which_ord][run])
                order = [int(dd) for dd in order]
                tf_record = []
                run_trials = pd.DataFrame()
                prev = -1

                # select trial in accordance with trial order
                for count,oo in enumerate(order):

                    # if rest trial
                    if oo == 0:
                        temp_row = pd.DataFrame({"story":np.nan, "question":np.nan, "answer":np.nan, "condition":"rest","type_id":np.nan, "id":np.nan, "type":0, "run":np.nan},index=[count])

                    # else, pseudorandomize order
                    else:
                        sub_ord = df[(df["type"]==oo) & (df["answer"]!=prev)]

                        # if run out of trials, start over
                        if len(sub_ord) == 0:
                            startOver = True
                            print("ran out of trials. starting over...\n")
                            break

                        random.seed(random_seed)
                        rand_idx = random.randint(0,len(sub_ord)-1)
                        temp_row = sub_ord.iloc[[rand_idx]]
                        id = temp_row["id"].values[0]
                        random_seed+=1

                        tf = temp_row["answer"].values[0]
                        tf_record.append(tf)
                        if len(tf_record) > 1:
                            if tf_record[len(tf_record)-1] == tf_record[len(tf_record)-2]:
                                prev = tf
                            else:
                                prev = -1

                        df=df[df["id"]!=id]

                    run_trials = pd.concat([run_trials,temp_row],ignore_index = True)

                # check to see if need to start over
                if startOver == True:
                    print("need to start over.\n")
                    startOver = False
                    break

                # save
                run_trials["run"] = [run + 1] * run_len
                all_trials = pd.concat([all_trials,run_trials],ignore_index = True)
                if len(all_trials) == 2 * run_len:
                    print("finished!\n")
                    finished = True
                    outfile = "orders/ord%d_vers%d_socphys_trials_allruns.xlsx"%(which_ord+1,vers+1)
                    all_trials.to_excel(outfile, index=False)
                    break
