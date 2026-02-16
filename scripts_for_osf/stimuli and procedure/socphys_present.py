### socphys_present.py ###
# purpose: present social/physical localizer trials
# written by MH, adapted from YFL

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
dlg.addField("Order seed", "1")
dlg.addField("Version seed", "1")
dlg.addField("Scr.Width", "1680")
dlg.addField("Scr.Height","1050")
dlg.addField("Test function", initial=False)

info = dlg.show()
if dlg.OK:
    print(info)

sj_ID = info[0]
run_vec = info[1]
run_vec = run_vec.split(",")
run_vec = [int(ii) for ii in run_vec]
order_seed = int(info[2])
version_seed = int(info[3])
aspect = (int(info[-3]),int(info[-2]))
inside_test = info[-1]
position = (0,0)
txt_h=0.05

# (10 trials per run) * (12 sec fixation + 14 sec story) + (12 sec fixation)
# plus 15 sec pause at beginning of each run.

t_fixation = 12
t_story = 12
t_quest = 4
t_space = 15

true_key = 1
false_key = 0
trigger = [5] # the keys in the scanner are labeled 1-6, but recognized by Python as 0-5!!
true_key_kb = '1'
false_key_kb = '0'
tf = "False                                      True"

# initialize the presentation window and some constant elements to be presented
win = visual.Window(size=aspect, screen=1, fullscr=True,allowGUI=False, color='black', monitor="testMonitor")
fixation_cross = visual.TextStim(win, pos=(0,0), text="+")
wait_text = visual.TextStim(win, pos=(0,0), text="The experiment will begin soon.",color="white", alignText="center", anchorVert="center", height=txt_h*1.6)

# loop for each run (2 total)
for run in run_vec:

    # pull up the right version for this participant
    run_df = pd.read_excel("orders/ord%d_vers%d_socphys_trials_allruns.xlsx"%(order_seed,version_seed))
    run_df = run_df[run_df["run"] == run]
    print(run_df)
    print("RUN %d STARTS NOW!\n"%run)

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
    out_file = "logs/%s_ord%d_vers%d_socphys_resp_run%d.xlsx"%(sj_ID,order_seed,version_seed,run)
    o_f = pd.DataFrame(columns=["story", "question", "answer", "correct", "condition","type_id", "id", "type", "run"])

    # track both the real elapsed time and the theoretical elapsed time, so that we can subtract the difference from the space trial to calibrate the difference
    t_elapse_theo = 0
    t_elapse_real = 0

    for counter,row in run_df.iterrows():

        row["rt1"] = t_story
        row["rt2"] = t_quest
        row["rt_over"] = np.nan
        row["correct"] = 0
        row["onset"] = t_elapse_real

        # the behavior for a space trial (beginning of run)
        if row["condition"]=="rest":
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
        if row["condition"]!="rest":

            story = row["story"]
            quest = row["question"]
            truth = row["answer"]

            show_story = visual.TextStim(win, pos=(0,0),text=story, color='white', alignText='left', anchorVert='center', height=txt_h*1.5)
            show_quest = visual.TextStim(win, pos=(0,0),text=quest, color='white', alignText='left', anchorVert='center', height=txt_h*1.5)
            show_tf = visual.TextStim(win, pos=(0,-0.4),text=tf, color='white', alignText='left', anchorVert='center', height=txt_h*1.5)

            # present story
            event.clearEvents()
            trial_clock = core.Clock()
            t = 0
            answered = False
            while (not event.getKeys(["escape"])) and (t<=t_story):
                t = trial_clock.getTime()
                show_story.draw()
                win.flip()
            t_elapse_theo += t_story
            t_elapse_real += t

            # present second sentence
            event.clearEvents()
            trial_clock = core.Clock()
            if devices:
                rb.clear_response_queue()
                rb.con.flush()
            t = 0
            answered = False
            while (not event.getKeys(["escape"])) and (t<=t_quest):
                t = trial_clock.getTime()
                show_quest.draw()
                show_tf.draw()
                if devices:
                    rb.poll_for_response()
                    if rb.response_queue and not answered:
                        if rb.response_queue[-1]['key'] in [true_key, false_key]:
                            response = rb.response_queue[-1]['key']
                            sj_ans = int(response==true_key)
                            row["correct"] = int(sj_ans==truth)
                            row["rt2"] = t
                            answered = True
                if not devices:
                    response = event.getKeys([true_key_kb,false_key_kb])
                    if response and not answered:
                        sj_ans = int(response[0]==true_key_kb)
                        row["correct"] = int(sj_ans==truth)
                        row["rt2"] = t
                        answered = True
                win.flip()
            t_elapse_theo += t_quest
            t_elapse_real += t

            # present fixation cross
            event.clearEvents()
            trial_clock = core.Clock()
            t = 0
            answered = False
            while (not event.getKeys(["escape"])) and (t<=t_fixation):
                t = trial_clock.getTime()
                fixation_cross.draw()
                if devices:
                    rb.poll_for_response()
                    if rb.response_queue and not answered and row["rt2"] == t_quest:
                        if rb.response_queue[-1]['key'] in [true_key, false_key]:
                            response = rb.response_queue[-1]['key']
                            sj_ans = int(response==true_key)
                            row["correct"] = int(sj_ans==truth)
                            row["rt_over"] = t
                            answered = True
                if not devices:
                    response = event.getKeys([true_key_kb,false_key_kb])
                    if response and not answered and row["rt2"] == t_quest:
                        sj_ans = int(response[0]==true_key_kb)
                        row["correct"] = int(sj_ans==truth)
                        row["rt_over"] = t
                        answered = True
                win.flip()
            t_elapse_theo += t_fixation
            t_elapse_real += t
            print((row["condition"], row["correct"]*"RIGHT"+(not row["correct"])*"WRONG", row["rt1"], row["rt2"]))

        # log trial
        o_f = o_f.append(row, ignore_index=True)
        o_f.to_excel(out_file, index=False)

    acc = (sum(o_f["correct"]))/(len(o_f))
    print("END OF RUN %d. ACCURACY = %f.\n"%(run,acc))

    event.clearEvents()
    trial_clock = core.Clock()
    t = 0
    win.flip()

to_fin = gui.Dlg()
to_fin.addText("DONE!")
to_fin.show()
finish = to_fin.OK

core.quit()
