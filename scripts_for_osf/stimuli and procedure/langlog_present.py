### langlog_present.py ###
# purpose: present language/logic localizer trials
# written by YFL, adapted by MH

from psychopy import core, visual, event, gui
import pandas as pd
import numpy as np
import os
import pyxid2 as pyxid
import time
import random
from numpy.random import permutation

# set directory
wd = "" # file path
os.chdir(wd)

# detect button box
devices = False
devices = pyxid.get_xid_devices()
print(devices)

if devices:
    rb = devices[0]

if not devices:
    print("Where's the Cedrus button box?\nFine, let's use the keyboard instead!")

# initialize some information
dlg = gui.Dlg(title="Info")
dlg.addField("Subj.ID", "myself")
dlg.addField("Runs", "1,2")
dlg.addField("Batch seed", "0")
dlg.addField("Item seed", "0")
dlg.addField("Ans Group",choices=[1,2])
dlg.addField("Scr.Width", "1680")
dlg.addField("Scr.Height","1050")

info = dlg.show()
if dlg.OK:
    print(info)

# gather inputs
sj_ID = info[0]
run_vec = info[1]
run_vec = run_vec.split(",")
run_vec = [int(ii) for ii in run_vec]
batch_seed = int(info[2])
item_seed = int(info[3])
group_ID = int(info[4])
aspect = (int(info[5]),int(info[6]))
inside_test = info[-1]
position = (0,0)
txt_h=0.05

# some parameters
n_per_cond = 16
n_cond = 3
the_conds = ["equation", "sentence", "logic"]
n_per_run = 24
n_cond_gp_per_run = n_per_run//n_cond
n_run = 2

t_fixation = 1
t_premise = 3
t_conclusion = 16
t_space = 5
t_feedback = 10

cont_key = "space"
true_key = 1
false_key = 0
trigger = [5] # the keys in the scanner are labeled 1-6, but recognized by Python as 0-5!!
true_key_kb = '1'
false_key_kb = '0'

df = pd.read_excel("localizer_roster_shortened.xlsx")
df = df.drop(columns=["tf_%d"%(1+(group_ID==1))]).rename(columns={"tf_%d"%group_ID : "tf"})

# randomize trial order
random.seed(batch_seed)
batch_order = [1,2]
if batch_seed == 0:
    shuffled_batch = [1,2]
else:
    shuffled_batch = [2,1]
batch_dict = {bb:ss for bb,ss in zip(batch_order, shuffled_batch)}
print(df)
for ii,row in df.iterrows():
    df.at[ii,'batch'] = batch_dict[df.at[ii, 'batch']]
print(df)
random.seed()

# initialize the presentation window and some constant elements to be presented
print("setting up window")
win = visual.Window(size=aspect, fullscr = 1, screen=1, allowGUI=False, color='black', monitor="testMonitor")
fixation_cross = visual.TextStim(win, pos=(0,0), text="+")
wait_text = visual.TextStim(win, pos=(0,0), text="The experiment will begin soon.",color="white", alignText="center", anchorVert="center", height=txt_h*1.6)

for ii in run_vec:

    run_df = df[df["batch"]==ii]#.reset_index().drop(columns=["index"])
    print(run_df)
    random.seed(item_seed+ii)

    # ordering scheme, not flexible at all. Should change if any of the following changes:
    # number of items per run, number of conditions
    order = ["02113", "03123", "03322", "02331", "01321", "01122"]
    order = "".join(random.sample(order, len(order)))
    order = [int(dd) for dd in order]
    cond_dict = {id:cc for id,cc in zip([1,2,3], random.sample(the_conds,3))}
    cond_item_index = {}
    for cc in the_conds:
        cond_df = run_df[run_df["type"]==cc]
        cond_item_index[cc] = list(cond_df.index)
        cond_item_index[cc] = random.sample(cond_item_index[cc], len(cond_item_index[cc]))

    tpr = [] # originally comes from "trials per run"
    for oo in order:
        if oo==0:
            tpr += [('space',999)]
        else:
            tpr += [(cond_dict[oo], cond_item_index[cond_dict[oo]].pop(0))]

    # Just... waiting for the trigger!
    event.clearEvents()
    if devices:
        rb.clear_response_queue()
        rb.con.flush()
    print("Waiting for the trigger.")
    ced_no_response = True
    while (ced_no_response and (not event.getKeys(["escape"]))):
        if devices:
            ced_no_response = ((not rb.response_queue) or (not rb.response_queue[-1]['key'] in trigger))
            rb.poll_for_response()
        wait_text.draw()
        win.flip()
    print("YES!! I have the trigger!!\n")

    # initialize the df used to record subject response
    out_file = "logs/%s_[3in1]_group%d_run%d.xlsx"%(sj_ID,group_ID,ii)
    o_f = pd.DataFrame(columns=["type", "item", "premise", "conclusion", "tf", "correct", "rt", "onset"])

    # track both the real elapsed time and the theoretical elapsed time, so that we can subtract the difference from the space trial to calibrate the difference
    t_elapse_theo = 0
    t_elapse_real = 0

    for pp in tpr:
        # initialize the row that's to be appended to the data df
        this_row = {"type":"", "item":0, "premise":"", "conclusion":"", "tf":9, "correct":0, "judg_raw":999, "rt":t_conclusion, "onset":t_elapse_real}

        the_cond = pp[0]
        the_item = pp[1]
        this_row["type"] = the_cond
        this_row["item"] = the_item

        # the behavior for a space trial
        if the_cond=="space":
            print("==========")
            t_space_real = t_space - (t_elapse_real-t_elapse_theo)*(t_elapse_real>t_elapse_theo)

            # present nothing in the space trial
            event.clearEvents()
            trial_clock = core.Clock()
            t = 0
            while (not event.getKeys(["escape"])) and (t<=t_space_real):
                t = trial_clock.getTime()
                win.flip()
            t_elapse_theo += t_space
            t_elapse_real += t

        # the behavior for real trials
        if the_cond!="space":
            truth = run_df.at[the_item, "tf"]
            premise = run_df.at[the_item, "prompt"]
            conclusion = run_df.at[the_item, "same"*truth+"diff"*(not truth)]

            this_row["tf"] = truth
            this_row["premise"] = premise
            this_row["conclusion"] = conclusion

            show_premise = visual.TextStim(win, pos=(0,0),text=premise, color='white', alignText='center', anchorVert='center', height=txt_h*1.5)

            show_conclusion = visual.TextStim(win, pos=(0,-0.4),text=conclusion, color='white', alignText='center', anchorVert='center', height=txt_h*1.5)

            # present fixation cross
            event.clearEvents()
            trial_clock = core.Clock()
            t = 0
            while (not event.getKeys(["escape"])) and (t<=t_fixation):
                t = trial_clock.getTime()
                fixation_cross.draw()
                win.flip()
            t_elapse_theo += t_fixation
            t_elapse_real += t

            # present premise
            event.clearEvents()
            trial_clock = core.Clock()
            t = 0
            while (not event.getKeys(["escape"])) and (t<=t_premise):
                t = trial_clock.getTime()
                show_premise.draw()
                win.flip()
            t_elapse_theo += t_premise
            t_elapse_real += t

            # present premise + conclusion
            event.clearEvents()
            trial_clock = core.Clock()
            if devices:
                rb.clear_response_queue()
                rb.con.flush()
            t = 0
            answered = False
            while (not event.getKeys(["escape"])) and (t<=t_conclusion):
                t = trial_clock.getTime()
                show_premise.draw()
                show_conclusion.draw()
                if devices:
                    rb.poll_for_response()
                    if rb.response_queue and not answered:
                        if rb.response_queue[-1]['key'] in [true_key, false_key]:
                            response = rb.response_queue[-1]['key']
                            sj_ans = int(response==true_key)
                            this_row["judg_raw"] = sj_ans
                            this_row["correct"] = int(sj_ans==truth)
                            this_row["rt"]=t
                            answered = True
                if not devices:
                    response = event.getKeys([true_key_kb,false_key_kb])
                    if response and not answered:
                        sj_ans = int(response[0]==true_key_kb)
                        this_row["correct"] = int(sj_ans==truth)
                        this_row["rt"]=t
                        answered = True
                win.flip()
            t_elapse_theo += t_conclusion
            t_elapse_real += t
            print((this_row["type"], this_row["correct"]*"RIGHT"+(not this_row["correct"])*"WRONG", this_row["rt"]))
        o_f = o_f.append(this_row, ignore_index=True)
        o_f.to_excel(out_file, index=False)
    print()

    # visual feedback of the performance in this run
    NN = n_per_run
    acc_ratio = float(o_f["correct"].sum())/NN
    acc = 100*acc_ratio
    speed_raw = o_f[o_f.type!="space"]["rt"].mean()
    print("Performance in this run: ACC = %f, RT = %f"%(acc_ratio,speed_raw))
    speed_scale = 1-(speed_raw/t_conclusion)
    speed_meter = [speed_scale>0.8, speed_scale>0.6, speed_scale>0.4, speed_scale>0.2, speed_scale>=0]
    speed_text_dict = {1:"Very\nSlow", 2:"Slow", 3:"Medium", 4:"Fast", 5:"Very\nFast"}
    speed_text = speed_text_dict[sum(speed_meter)]

    feedback_title = visual.TextStim(win, pos=(0,0.7), text="Here's your performance in this run!", color="white", alignText="center", anchorVert="center", height=txt_h*1.6)
    feedback_acc = visual.TextStim(win, pos=(-0.2,-0.6), text="Accuracy", color="white", alignText="center", anchorVert="center", height=txt_h*1.8)
    feedback_acc_val = visual.TextStim(win, pos=(-0.3,0), text="%.0f %%"%(acc), color="white", anchorHoriz="right", anchorVert="center", height=txt_h*2.1)
    feedback_speed = visual.TextStim(win, pos=(0.2,-0.6), text="Speed", color="white", alignText="center", anchorVert="center", height=txt_h*1.8)
    feedback_speed_text = visual.TextStim(win, pos=(0.3,0), text=speed_text, color="white", anchorHoriz="left", anchorVert="center", height=txt_h*2.1)

    all_bar_width = 0.1
    acc_frame = visual.Rect(win=win, height=1, width=all_bar_width, fillColor="black")
    acc_frame.pos = [-0.2, 0]
    speed_frame = visual.Rect(win=win, height=1, width=all_bar_width, fillColor="black")
    speed_frame.pos = [0.2,0]

    acc_bar = visual.Rect(win=win, height=acc_ratio, width=all_bar_width, fillColor=[0.3,0.9,0.3], lineWidth=0)
    acc_bar.pos = [-0.2, -(1-acc_ratio)/2]
    speed_bar = visual.Rect(win=win, height=speed_scale, width=all_bar_width, fillColor=[0.3,0.9,0.3], lineWidth=0)
    speed_bar.pos = [0.2, -(1-speed_scale)/2]

    event.clearEvents()
    trial_clock = core.Clock()
    t = 0
    while (not event.getKeys(["escape"])) and (t<=t_feedback):
        t = trial_clock.getTime()
        feedback_title.draw()
        feedback_acc.draw()
        feedback_acc_val.draw()
        feedback_speed.draw()
        feedback_speed_text.draw()
        acc_frame.draw()
        speed_frame.draw()
        acc_bar.draw()
        speed_bar.draw()
        win.flip()

    event.clearEvents()
    trial_clock = core.Clock()
    t = 0
    win.flip()

to_fin = gui.Dlg()
to_fin.addText("DONE!")
to_fin.show()
finish = to_fin.OK

core.quit()
