# analyze_RT_acc.R
# analyze behavioral results recorded during fMRI experiment
# written by MH

# load libraries
library(readr)
library(dplyr)
library(tidyr)
library(stringr)
library(forcats)
library("readxl")
library(ggplot2)

read_logs <- function(ptp,caus_ratings) {
  
  ### start with main_exp ###
  setwd("")
  filenames <- list.files(path=".",pattern=".xlsx")
  dir.create(paste0(getwd(),"/timing"))
  dir.create(paste0(getwd(),"/orig_logs"))
  
  # read in individual ptp's log files for each run and change variable names
  all_trials <- NULL
  run_count <- 1
  for (filename in filenames) {
    run_trials <- read_excel(filename)
    run_trials <- run_trials %>% 
      mutate(RUN = rep(run_count),
             cond = case_when(type == "1" ~ "bio",
                              type == "2" ~ "mech",
                              type == "3" ~ "ncb",
                              type == "4" ~ "ncm",
                              type == "5" ~ "magic"),
             illness_type = case_when(type == "1" ~ group_name_type,
                                      type == "2" ~ MECHTYPE,
                                      type == "3" ~ group_name_type,
                                      type == "4" ~ group_name_type,
                                      type == "5" ~ "nan"),
             illness_type = case_when(illness_type == "NA power outage" ~ "PLC",
                                      illness_type == "NA leak" ~ "OBJ",
                                      illness_type == "NA puddle" ~ "OBJ",
                                      illness_type == "HIV-AIDS" ~ "HIVAIDS",
                                      TRUE ~ illness_type),
             MECHTYPE = case_when(MECHTYPE == "NA power outage" ~ "PLC",
                                  MECHTYPE == "NA leak" ~ "OBJ",
                                  MECHTYPE == "NA puddle" ~ "OBJ",
                                  TRUE ~ MECHTYPE))
    

    
    write.csv(run_trials,paste("orig_logs/",ptp,"_ir_run",run_count,".csv",sep=""))

    all_trials <- rbind(all_trials,run_trials)
    
    run_count <- run_count+1
    
  }
    
  # get overall accuracy and accuracy per run
  # also, perform RT transformation
  all_trials <- all_trials %>%
    filter(type != 0) %>%
    mutate(RT = ifelse(rt == 7, rt + rt_over, rt),
           rawjudg = magic_judg_raw,
           mag = ifelse(truth==1,"magic","nonmagic"))
  
  write.csv(all_trials,"main_all_trials.csv")
  
  total_acc <- all_trials %>%
    summarize(mean_acc = mean(magic_judg_correct))
  
  acc_by_run <- all_trials %>%
    group_by(RUN) %>%
    summarize(mean_acc = mean(magic_judg_correct))
  
  write.csv(acc_by_run,"main_accbyrun.csv")
  
  acc_by_cond <- all_trials %>%
    group_by(cond) %>%
    summarize(mean_acc = mean(magic_judg_correct))
  
  write.csv(acc_by_cond,"main_accbycond.csv")
  
  # factorize
  all_trials$CAUSALITY <- factor(all_trials$CAUSALITY)
  all_trials$mag <- factor(all_trials$mag)
  all_trials$cond <- factor(all_trials$cond)

  # get RT summary
  RT_all_means <- all_trials %>%
    group_by(cond) %>%
    summarize(mean_RT = mean(RT,na.rm = TRUE), sd_RT = sd(RT,na.rm=TRUE))

  RT_caus_means <- all_trials %>%
    group_by(CAUSALITY) %>%
    summarize(mean_RT = mean(RT,na.rm = TRUE), sd_RT = sd(RT,na.rm = TRUE))

  write.csv(RT_all_means,"main_RTallmeans.csv")
  write.csv(RT_caus_means,"main_RTcausmeans.csv")

  ### next, soc_phys ###
  setwd("")
  filenames <- list.files(path=".",pattern=".xlsx")
  dir.create(paste0(getwd(),"/timing"))

  # read in individual ptp's log files for each run
  all_trials <- NULL
  run_count <- 1
  for (filename in filenames) {
    run_trials <- read_excel(filename)
    run_trials <- run_trials %>% mutate(RUN = rep(run_count))
    all_trials <- rbind(all_trials,run_trials)
    run_count <- run_count+1
  }

  # get overall accuracy and accuracy per run
  # also, perform RT transformation
  all_trials <- all_trials %>%
    filter(type != 0) %>%
    mutate(RT = ifelse(rt2 == 4, rt2 + rt_over, rt2))

  write.csv(all_trials,"socphys_all_trials.csv")

  total_acc <- all_trials %>%
    summarize(mean_acc = mean(correct))

  acc_by_cond <- all_trials %>%
    group_by(condition) %>%
    summarize(mean_acc = mean(correct))

  write.csv(acc_by_cond,"socphys_accbycond.csv")

  # get RT summary
  RT_all_means <- all_trials %>%
    group_by(condition) %>%
    summarize(mean_RT = mean(RT), sd_RT = sd(RT))

  write.csv(RT_all_means,"socphys_RTallmeans.csv")

  ### next, langlog ###
  setwd("")
  filenames <- list.files(path=".",pattern=".xlsx")
  dir.create(paste0(getwd(),"/timing"))

  # read in individual ptp's log files for each run
  all_trials <- NULL
  run_count <- 1
  for (filename in filenames) {
    run_trials <- read_excel(filename)
    run_trials <- run_trials %>% mutate(RUN = rep(run_count))
    all_trials <- rbind(all_trials,run_trials)
    run_count <- run_count+1
  }

  # get overall accuracy and accuracy per run
  # also, perform RT transformation
  all_trials <- all_trials %>%
    filter(type != 0)

  write.csv(all_trials,"langlog_all_trials.csv")

  total_acc <- all_trials %>%
    summarize(mean_acc = mean(correct))

  acc_by_cond <- all_trials %>%
    group_by(type) %>%
    summarize(mean_acc = mean(correct))

  write.csv(acc_by_cond,"langlog_accbycond.csv")

  # get RT summary
  RT_all_means <- all_trials %>%
    group_by(type) %>%
    summarize(mean_RT = mean(rt), sd_RT = sd(rt))

  write.csv(RT_all_means,"langlog_RTallmeans.csv")

}

# to run

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
ptps <- c("IRNX_05")

for (ptp in ptps) {
  read_logs(ptp,caus_ratings)
}

# get group accuracy and RT, plot, stats

ptps <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")

### MAIN EXP ###
## accuracy ##
all_accs <- NULL
all_accs_cond <- NULL

# gather: total accuracy and accuracy by condition
for (ptp in ptps) {
  sub_acc <- read.csv("main_accbyrun.csv") %>%
    summarize(acc = mean(mean_acc)) %>%
    mutate(ptp = ptp)
  all_accs <- rbind(all_accs,sub_acc)
  cond_acc <- read.csv("main_accbycond.csv")[ ,2:3] %>%
    mutate(ptp = ptp)
  all_accs_cond <- rbind(all_accs_cond,cond_acc)
}

# descriptive stats
all_accs_stats <- all_accs %>%
  summarize(mean = mean(acc),SD = sd(acc))

all_accs_cond_stats <- all_accs_cond %>%
  group_by(cond) %>%
  summarize(mean = mean(mean_acc),SD=sd(mean_acc))

write.csv(all_accs,"mainexp_accuracy_byptp.csv")
write.csv(all_accs_stats,"mainexp_accuracy_descrip_stats.csv")
write.csv(all_accs_cond,"mainexp_accuracy_bycond_byptp.csv")
write.csv(all_accs_cond_stats,"mainexp_accuracy_bycond_descrip_stats.csv")

# stats

# every cond compared, exclude magic
all_accs_cond <- read.csv("mainexp_accuracy_bycond_byptp.csv")
accs_cond <- all_accs_cond %>%
  filter(cond != "magic")
a1 <- aov(mean_acc ~ cond + Error(ptp/cond), data=accs_cond)
summary(a1)
pwc1 <- pairwise.t.test(accs_cond$mean_acc, accs_cond$cond, p.adjust.method = "none")
pwc1

## RT ##
all_RTs <- NULL
all_RTs_cond <- NULL

# gather: total RT and RT by condition
for (ptp in ptps) {
  sub_RT <- read.csv("main_RTallmeans.csv") %>%
    summarize(mean = mean(mean_RT)) %>%
    mutate(ptp = ptp)
  all_RTs <- rbind(all_RTs,sub_RT)
  cond_RT <- read.csv("main_RTallmeans.csv") %>%
    select(cond,mean_RT) %>%
    mutate(ptp = ptp)
  all_RTs_cond <- rbind(all_RTs_cond,cond_RT)
}

# descriptive stats
all_RTs_stats <- all_RTs %>%
  summarize(mean = mean(mean),SD = sd(mean))

all_RTs_cond_stats <- all_RTs_cond %>%
  group_by(cond) %>%
  summarize(mean = mean(mean_RT),SD=sd(mean_RT))

write.csv(all_RTs,"mainexp_RT_byptp.csv")
write.csv(all_RTs_stats,"mainexp_RT_descrip_stats.csv")
write.csv(all_RTs_cond,"mainexp_RT_bycond_byptp.csv")
write.csv(all_RTs_cond_stats,"mainexp_RT_bycond_descrip_stats.csv")

# stats
# every cond compared, exclude magic
all_RTs_cond <- read.csv("mainexp_RT_bycond_byptp.csv")
RTs_cond <- all_RTs_cond %>%
  filter(cond != "magic")
a2 <- aov(mean_RT ~ cond + Error(ptp/cond), data=RTs_cond)
summary(a2)
pwc2 <- pairwise.t.test(RTs_cond$mean_RT, RTs_cond$cond, p.adjust.method = "none")
pwc2

### LANG LOG ###
all_accs <- NULL
all_accs_cond <- NULL

# gather: total accuracy and accuracy by condition
for (ptp in ptps) {
  sub_acc <- read.csv("langlog_accbycond.csv") %>%
    filter(type!="space") %>%
    summarize(acc = mean(mean_acc)) %>%
    mutate(ptp = ptp)
  all_accs <- rbind(all_accs,sub_acc)
  cond_acc <- read.csv("langlog_accbycond.csv")[,2:3] %>%
    filter(type!="space") %>%
    mutate(ptp = ptp)
  all_accs_cond <- rbind(all_accs_cond,cond_acc)
}

# descriptive stats
all_accs_stats <- all_accs %>%
  summarize(mean = mean(acc),SD = sd(acc))

all_accs_cond_stats <- all_accs_cond %>%
  group_by(type) %>%
  summarize(mean = mean(mean_acc),SD=sd(mean_acc))

write.csv(all_accs,"langlog_accuracy_byptp.csv")
write.csv(all_accs_stats,"langlog_accuracy_descrip_stats.csv")
write.csv(all_accs_cond,"langlog_accuracy_bycond_byptp.csv")
write.csv(all_accs_cond_stats,"langlog_accuracy_bycond_descrip_stats.csv")

# stats

# every cond compared
a3 <- aov(mean_acc ~ type + Error(ptp/type), data=all_accs_cond)
summary(a3)
pwc3 <- pairwise.t.test(all_accs_cond$mean_acc, all_accs_cond$type, p.adjust.method = "none")
pwc3

## RT ##
all_RTs <- NULL
all_RTs_cond <- NULL

# gather: total RT and RT by condition
for (ptp in ptps) {
  sub_RT <- read.csv("langlog_RTallmeans.csv") %>%
    filter(type!="space") %>%
    summarize(mean = mean(mean_RT)) %>%
    mutate(ptp = ptp)
  all_RTs <- rbind(all_RTs,sub_RT)
  cond_RT <- read.csv("langlog_RTallmeans.csv")[,2:3] %>%
    filter(type!="space") %>%
    mutate(ptp = ptp)
  all_RTs_cond <- rbind(all_RTs_cond,cond_RT)
}

# descriptive stats
all_RTs_stats <- all_RTs %>%
  summarize(mean_RT = mean(mean),SD = sd(mean))

all_RTs_cond_stats <- all_RTs_cond %>%
  group_by(type) %>%
  summarize(mean = mean(mean_RT),SD=sd(mean_RT))

write.csv(all_RTs,"langlog_RT_byptp.csv")
write.csv(all_RTs_stats,"langlog_RT_descrip_stats.csv")
write.csv(all_RTs_cond,"langlog_RT_bycond_byptp.csv")
write.csv(all_RTs_cond_stats,"langlog_RT_bycond_descrip_stats.csv")

# stats

# every cond compared
a4 <- aov(mean_RT ~ type + Error(ptp/type), data=all_RTs_cond)
summary(a4)
pwc4 <- pairwise.t.test(all_RTs_cond$mean_RT, all_RTs_cond$type, p.adjust.method = "none")
pwc4

### SOC PHYS ###
all_accs <- NULL
all_accs_cond <- NULL

# gather: total accuracy and accuracy by condition
for (ptp in ptps) {
  sub_acc <- read.csv("socphys_accbycond.csv") %>%
    summarize(acc = mean(mean_acc)) %>%
    mutate(ptp = ptp)
  all_accs <- rbind(all_accs,sub_acc)
  cond_acc <- read.csv("socphys_accbycond.csv")[,2:3] %>%
    mutate(ptp = ptp)
  all_accs_cond <- rbind(all_accs_cond,cond_acc)
}

# descriptive stats
all_accs_stats <- all_accs %>%
  summarize(mean = mean(acc),SD = sd(acc))

all_accs_cond_stats <- all_accs_cond %>%
  group_by(condition) %>%
  summarize(mean = mean(mean_acc),SD=sd(mean_acc))

write.csv(all_accs,"socphys_accuracy_byptp.csv")
write.csv(all_accs_stats,"socphys_accuracy_descrip_stats.csv")
write.csv(all_accs_cond,"socphys_accuracy_bycond_byptp.csv")
write.csv(all_accs_cond_stats,"socphys_accuracy_bycond_descrip_stats.csv")

# stats

# every cond compared
a5 <- aov(mean_acc ~ condition + Error(ptp/condition), data=all_accs_cond)
summary(a5)

## RT ##
all_RTs <- NULL
all_RTs_cond <- NULL

# gather: total RT and RT by condition
for (ptp in ptps) {
  sub_RT <- read.csv("socphys_RTallmeans.csv") %>%
    summarize(mean = mean(mean_RT,na.rm=T)) %>%
    mutate(ptp = ptp)
  all_RTs <- rbind(all_RTs,sub_RT)
  cond_RT <- read.csv("socphys_RTallmeans.csv")[,2:3] %>%
    mutate(ptp = ptp)
  all_RTs_cond <- rbind(all_RTs_cond,cond_RT)
}

# descriptive stats
all_RTs_stats <- all_RTs %>%
  summarize(mean_RT = mean(mean),SD = sd(mean))

all_RTs_cond_stats <- all_RTs_cond %>%
  group_by(condition) %>%
  summarize(mean = mean(mean_RT),SD=sd(mean_RT))

write.csv(all_RTs,"socphys_RT_byptp.csv")
write.csv(all_RTs_stats,"socphys_RT_descrip_stats.csv")
write.csv(all_RTs_cond,"socphys_RT_bycond_byptp.csv")
write.csv(all_RTs_cond_stats,"socphys_RT_bycond_descrip_stats.csv")

# stats

# every cond compared
a6 <- aov(mean_RT ~ condition + Error(ptp/condition), data=all_RTs_cond)
summary(a6)



