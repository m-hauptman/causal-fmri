# all_psc_stats.R
# run stats on PSC results from different groups of vertices
# written by MH

library(ggplot2)
library(tidyr)
library(dplyr)
library(RColorBrewer)
library(hrbrthemes)
library(vioplot)
library(cowplot)
library(ggsignif)
library(stringr)

#### stats on PSC: peak to trough ####

## analyses where leave one run out technique was not used ##

wd = ""
setwd(wd)

# language

# frontal search space
data_lang_fr <- read.csv("data/all_FrontLang_lh_lang_vs_math_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  mutate(causal = ifelse((cond == "bio" | cond == "mech"),"causal","noncausal"))

# causality effect
a1 <- aov(psc ~ causal + Error(sub/causal), data = data_lang_fr)
capture_a1 <- summary(a1)
capture.output(print(a1), capture_a1, file = "stats/fr_lang_causal.txt")

# illness effect
a2 <- aov(psc ~ cond + Error(sub/cond), data = data_lang_fr)
capture_a2 <- summary(a2)
capture.output(print(a2), capture_a2, file = "stats/fr_lang_cond.txt")

# temporal search space
data_lang_tmp <- read.csv("data/all_TempLang_lh_lang_vs_math_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  mutate(causal = ifelse((cond == "bio" | cond == "mech"),"causal","noncausal")) #%>%

# causality effect
a3 <- aov(psc ~ causal + Error(sub/causal), data = data_lang_tmp)
capture_a3 <- summary(a3)
capture.output(print(a3), capture_a3, file = "stats/temp_lang_causal.txt")

# illness effect
a4 <- aov(psc ~ cond + Error(sub/cond), data = data_lang_tmp)
capture_a4 <- summary(a4)
capture.output(print(a4), capture_a4, file = "stats/temp_lang_cond.txt")

# pc - social vertices, main exp conditions

data_pc_lh <- read.csv("data/all_PC_lh_soc_vs_phys_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a5 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_lh)
capture_a5 <- summary(a5)
capture.output(print(a5), capture_a5, file = "stats/pc_lh_socphys_bio_v_mech.txt")

data_pc_rh <- read.csv("data/all_PC_rh_soc_vs_phys_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a6 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_rh)
capture_a6 <- summary(a6)
capture.output(print(a6), capture_a6, file = "stats/pc_rh_socphys_bio_v_mech.txt")

# tpj - social vertices, main exp conditions

data_tpj_lh <- read.csv("data/all_TPJ_lh_soc_vs_phys_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a7 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_lh)
capture_a7 <- summary(a7)
capture.output(print(a7), capture_a7, file = "stats/tpj_lh_socphys_bio_v_mech.txt")

data_tpj_rh <- read.csv("data/all_TPJ_rh_soc_vs_phys_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a8 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_rh)
capture_a8 <- summary(a8)
capture.output(print(a8), capture_a8, file = "stats/tpj_rh_socphys_bio_v_mech.txt")

# logic

data_log_lh <- read.csv("data/all_Logic_lh_log_vs_lang_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  mutate(causal = ifelse((cond == "bio" | cond == "mech"),"causal","noncausal"))

data_log_lh_cond <- data_log_lh %>%
  filter(cond == "bio" | cond == "mech")

# causality effect
a9 <- aov(psc ~ causal + Error(sub/causal), data = data_log_lh)
capture_a9 <- summary(a9)
capture.output(print(a9), capture_a9, file = "stats/log_causal.txt")

# illness effect
a10 <-  aov(psc ~ cond + Error(sub/cond), data = data_log_lh_cond)
capture_a10 <- summary(a10)
capture.output(print(a10), capture_a10, file = "stats/log_bio_v_mech.txt")

# pc - illness vertices, socphys localizer conditions

data_pc_lh <- read.csv("data/all_PC_lh_bio_vs_mech_conds=socphys_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "belief" | cond == "phys")

a11 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_lh)
capture_a11 <- summary(a11)
capture.output(print(a11), capture_a11, file = "stats/pc_lh_biomech_soc_v_phys.txt")

data_pc_rh <- read.csv("data/all_PC_rh_bio_vs_mech_conds=socphys_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "belief" | cond == "phys")

a12 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_rh)
capture_a12 <- summary(a12)
capture.output(print(a12), capture_a12, file = "stats/pc_rh_biomech_soc_v_phys.txt")

# tpj - illness vertices, socphys localizer conditions

data_tpj_lh <- read.csv("data/all_TPJ_lh_bio_vs_mech_conds=socphys_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "belief" | cond == "phys")

a11 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_lh)
capture_a11 <- summary(a11)
capture.output(print(a11), capture_a11, file = "stats/tpj_lh_biomech_soc_v_phys.txt")

data_tpj_rh <- read.csv("data/all_TPJ_rh_bio_vs_mech_conds=socphys_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "belief" | cond == "phys")

a12 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_rh)
capture_a12 <- summary(a12)
capture.output(print(a12), capture_a12, file = "stats/tpj_rh_biomech_soc_v_phys.txt")

## leave one run out analyses ##

wd = ""
setwd(wd)

# pc - illness vertices

data_pc_lh <- read.csv("data/all_PC_lh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a1 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_lh)
capture_a1 <- summary(a1)
capture.output(print(a1), capture_a1, file = "stats/pc_lh_bio_v_mech.txt")

data_pc_rh <- read.csv("data/all_PC_rh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a2 <- aov(psc ~ cond + Error(sub/cond), data = data_pc_rh)
capture_a2 <- summary(a2)
capture.output(print(a2), capture_a2, file = "stats/pc_rh_bio_v_mech.txt")

# pc - illness vertices, illness > noncaus

data_pc_lh <- read.csv("data/all_PC_lh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond != "mech") %>%
  mutate(cond2 = ifelse(cond == "noncaus1" | cond == "noncaus2", "nc", cond)) %>%
  group_by(cond2,TR,sub) %>%
  summarize(psc = mean(psc))

a3 <- aov(psc ~ cond2 + Error(sub/cond2), data = data_pc_lh)
capture_a3 <- summary(a3)
capture.output(print(a3), capture_a3, file = "stats/pc_lh_bio_v_nc.txt")

data_pc_rh <- read.csv("data/all_PC_rh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond != "mech") %>%
  mutate(cond2 = ifelse(cond == "noncaus1" | cond == "noncaus2", "nc", cond)) %>%
  group_by(cond2,TR,sub) %>%
  summarize(psc = mean(psc))

a4 <- aov(psc ~ cond2 + Error(sub/cond2), data = data_pc_rh)
capture_a4 <- summary(a4)
capture.output(print(a4), capture_a4, file = "stats/pc_rh_bio_v_nc.txt")

# tpj - illness vertices

data_tpj_lh <- read.csv("data/all_TPJ_lh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a5 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_lh)
capture_a5 <- summary(a5)
capture.output(print(a5), capture_a5, file = "stats/tpj_lh_bio_v_mech.txt")

data_tpj_rh <- read.csv("data/all_TPJ_rh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a6 <- aov(psc ~ cond + Error(sub/cond), data = data_tpj_rh)
capture_a6 <- summary(a6)
capture.output(print(a6), capture_a6, file = "stats/tpj_rh_bio_v_mech.txt")

# ppa - mechanical vertices

data_ppa_lh <- read.csv("data/all_PPAa_lh_mech_vs_bio_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a7 <- aov(psc ~ cond + Error(sub/cond), data = data_ppa_lh)
capture_a7 <- summary(a7)
capture.output(print(a7), capture_a7, file = "stats/ppaa_lh_mech_v_bio.txt")

data_ppa_rh <- read.csv("data/all_PPAa_rh_mech_vs_bio_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond == "bio" | cond == "mech")

a8 <- aov(psc ~ cond + Error(sub/cond), data = data_ppa_rh)
capture_a8 <- summary(a8)
capture.output(print(a8), capture_a8, file = "stats/ppaa_rh_mech_v_bio.txt")

# ppa - mechanical vertices, mech > noncaus

data_ppa_lh <- read.csv("data/all_PPAa_lh_mech_vs_bio_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond != "bio") %>%
  mutate(cond2 = ifelse(cond == "noncaus1" | cond == "noncaus2", "nc", cond)) %>%
  group_by(cond2,TR,sub) %>%
  summarize(psc = mean(psc))

a7 <- aov(psc ~ cond2 + Error(sub/cond2), data = data_ppa_lh)
capture_a7 <- summary(a7)
capture.output(print(a7), capture_a7, file = "stats/ppaa_lh_mech_v_nc.txt")

data_ppa_rh <- read.csv("data/all_PPAa_rh_mech_vs_bio_conds=biomech_top5_data.csv") %>%
  filter(TR != 1 & TR != 3) %>%
  filter(cond != "bio") %>%
  mutate(cond2 = ifelse(cond == "noncaus1" | cond == "noncaus2", "nc", cond)) %>%
  group_by(cond2,TR,sub) %>%
  summarize(psc = mean(psc))

a8 <- aov(psc ~ cond2 + Error(sub/cond2), data = data_ppa_rh)
capture_a8 <- summary(a8)
capture.output(print(a8), capture_a8, file = "stats/ppaa_rh_mech_v_nc.txt")

## comparing magnitude of bio > mech in 2 groups of vertices ##

# top illness vertices from leave one run out
data_loo <- read.csv("n=20_LOO/data/all_PC_lh_bio_vs_mech_conds=biomech_top5_data.csv") %>%
  filter(cond == "bio" | cond == "mech", TR != 1 & TR != 3) %>%
  group_by(cond,sub) %>%
  summarize(mean_psc = mean(psc)) %>%
  ungroup() %>%
  group_by(sub) %>%
  mutate(diffs = diff(mean_psc)*-1,vgroup = rep("loo")) %>%
  select(-cond,-mean_psc) %>%
  unique()

# top social vertices from soc/phys localizer
data_tom <- read.csv("n=20_noLOO/data/all_PC_lh_soc_vs_phys_conds=biomech_top5_data.csv") %>%
  filter(cond == "bio" | cond == "mech", TR != 1 & TR != 3) %>%
  group_by(cond,sub) %>%
  summarize(mean_psc = mean(psc)) %>%
  ungroup() %>%
  group_by(sub) %>%
  mutate(diffs = diff(mean_psc)*-1,vgroup = rep("tom")) %>%
  select(-cond,-mean_psc) %>%
  unique()

data_all <- rbind(data_loo,data_tom) 

# get means
means <- data_all %>%
  group_by(vgroup) %>%
  summarize(mean_diff = mean(diffs))

# statistical comparison of effects in each group
a1 <- aov(diffs ~ vgroup, data = data_all)
capture_a1 <- summary(a1)
capture.output(print(a1), capture_a1, file = "pc_lh_bioeffect_tom_vs_loo.txt")
