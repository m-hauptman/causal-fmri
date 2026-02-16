### man_exp_present.py ###
# purpose: present main experiment trials
# written by MH, adapted from YFL

import psychopy
from psychopy import core, visual, event, gui
import pandas as pd
import numpy as np
import os
import pyxid2 as pyxid
import time
import random
import math
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
dlg.addField("Runs", "1,2,3,4,5,6")
dlg.addField("Stimuli group",choices=["A","B"])
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
group_ID = info[2]
aspect = (int(info[-3]),int(info[-2]))
position = (0,0)
txt_h=0.05

# set timing parameters
t_fixation = 12
t_bothsents = 7
t_space = 15
t_wait = 23

# set key parameters
magic_key = 1
nonmagic_key = 0
trigger = [5] # the keys in the scanner are labeled 1-6, but recognized by Python as 0-5!!
magic_key_kb = '0'
nonmagic_key_kb = '1'

# initialize the presentation window and some constant elements to be presented
win = visual.Window(size=aspect, fullscr=True, screen=1, allowGUI=False, color='black', monitor="testMonitor") #winType="pyglet"
fixation_cross = visual.TextStim(win, pos=(0,0), text="+")
wait_text = visual.TextStim(win, pos=(0,0), text="The experiment will begin soon.",color="white", alignText="center", anchorVert="center", height=txt_h*1.6)

for ii in run_vec:

    # grab run trials
    run_df = pd.read_csv("orders/%s/%s_main_ord_group%s_run%d.csv"%(sj_ID,sj_ID,group_ID,int(ii)-1))
    print(run_df)
    print("RUN %d STARTS NOW!\n"%ii)

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
    out_file = "logs/%s_main_resp_group%s_run%d.xlsx"%(sj_ID,group_ID,ii)
    o_f = pd.DataFrame(columns=["CAUSALITY", "type_id", "id", "UNIQUE_ID", "GROUP1", "GROUP2", "GROUP_NAME", "COND1", "COND2", "type", "Group", "SENT1", "SENT2", "SENT2 DEPL", "TARGET", "NAMES", "GENDER", "MECHTYPE", "ILLTYPE", "ILLCAUS", "ILLINF", "ILLORG", "rt", "rt_over", "magic_judg_raw","magic_judg_correct", "onset"])

    # track both the real elapsed time and the theoretical elapsed time, so that we can subtract the difference from the space trial to calibrate the difference
    t_elapse_theo = 0
    t_elapse_real = 0

    for counter,row in run_df.iterrows():

        row["rt"] = t_bothsents
        row["rt_over"] = np.nan
        row["onset"] = t_elapse_real
        row["magic_judg_raw"] = np.nan
        row["magic_judg_correct"] = 0

        # the behavior for a space trial
        if row["type"]==0:
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
        if row["type"]!=0:

            firstsent = row["SENT1"]
            secsent = row["SENT2"]
            truth = row["truth"]
            asts = '*' * len(secsent)

            show_firstsent = visual.TextStim(win, pos=(0,0.08),text=firstsent, color='white', alignText='center', anchorVert='center', height=txt_h*1.5, wrapWidth = 2)
            show_secsent = visual.TextStim(win, pos=(0,-0.08),text=secsent, color='white', alignText='center', anchorVert='center', height=txt_h*1.5)

            # present second sentence
            event.clearEvents()
            trial_clock = core.Clock()
            if devices:
                rb.clear_response_queue()
                rb.con.flush()
            t = 0
            answered = False
            while (not event.getKeys(["escape"])) and (t<=t_bothsents):
                t = trial_clock.getTime()
                show_firstsent.draw()
                show_secsent.draw()
                if devices:
                    rb.poll_for_response()
                    if rb.response_queue and not answered:
                        if rb.response_queue[-1]['key'] in [magic_key, nonmagic_key]:
                            response = rb.response_queue[-1]['key']
                            row["rt"] = t
                            subj_resp = int(response==magic_key)
                            row["magic_judg_raw"] = subj_resp
                            row["magic_judg_correct"] = int(subj_resp==truth)
                            answered = True
                if not devices:
                    response = event.getKeys([magic_key_kb,nonmagic_key_kb])
                    if response and not answered:
                        row["rt"] = t
                        subj_resp = int(response[0]==magic_key_kb)
                        row["magic_judg_raw"] = subj_resp
                        row["magic_judg_correct"] = int(subj_resp==truth)
                        answered = True
                win.flip()
            t_elapse_theo += t_bothsents
            t_elapse_real += t
            print(row["type"], row["rt"], row["magic_judg_correct"],row["magic_judg_raw"])

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
                    if rb.response_queue and not answered and row["rt"] == t_bothsents:
                        if rb.response_queue[-1]['key'] in [magic_key, nonmagic_key]:
                            response = rb.response_queue[-1]['key']
                            row["rt_over"] = t
                            subj_resp = int(response==magic_key)
                            row["magic_judg_raw"] = subj_resp
                            row["magic_judg_correct"] = int(subj_resp==truth)
                            answered = True
                if not devices:
                    response = event.getKeys([magic_key_kb,nonmagic_key_kb])
                    if response and not answered and row["rt"] == t_bothsents:
                        row["rt_over"] = t
                        subj_resp = int(response[0]==magic_key_kb)
                        row["magic_judg_raw"] = subj_resp
                        row["magic_judg_correct"] = int(subj_resp==truth)
                        answered = True
                win.flip()
            t_elapse_theo += t_fixation
            t_elapse_real += t

        o_f = o_f.append(row, ignore_index=True)
        o_f.to_excel(out_file, index=False)

    # calculate accuracy in run
    acc = (sum(o_f["magic_judg_correct"]))/(len(o_f))

    print("END OF RUN %d. ACCURACY = %f.\n"%(ii,acc))

    event.clearEvents()
    trial_clock = core.Clock()
    t = 0
    win.flip()

    while (t <= t_wait):
        t = trial_clock.getTime()
        win.flip()

    print("WAIT PERIOD HAS CONCLUDED! PROCEED.\n")
    event.clearEvents()
    trial_clock = core.Clock()
    t = 0
    win.flip()

to_fin = gui.Dlg()
to_fin.addText("DONE!")
to_fin.show()
finish = to_fin.OK

core.quit()
