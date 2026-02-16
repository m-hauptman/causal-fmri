# analyze_groupdata_culling.R
# remove participants from online norming exp who failed attention check, plus trials 
# with outlier RTs
# written by MH 

# load libraries
library(readr)
library(dplyr)
library(tidyr)
library(stringr)
library(ggplot2)

### defaults ###

group_name <- ("group")
wd <- ""
setwd(wd)

### stats ###

# read in
main_all <- read.csv("ALL_mainresults.csv", header = TRUE)
fillers_all <- read.csv("ALL_fillerresults.csv", header = TRUE)

# factorize
main_all$COND2 <- factor(main_all$COND2)
main_all$COND2 <- fct_relevel(main_all$COND2, "bio", "mech", "nocause-bio1", "nocause-mech1")
main_all$GROUP_NAME <- factor(main_all$GROUP_NAME)

# cull

# inspect fillers
is_outlier <- function(x) {
  return(x < quantile(x, .25) - 1.5*IQR(x) | x > quantile(x, .75) + 1.5*IQR(x))
}

# make table of filler results
fill_byptp <- fillers_all %>% 
  group_by(ID,COND2) %>%
  filter(GROUP_NAME == "filler") %>%
  summarize(mean_judg = mean(selection, na.rm=T)) #%>%

fill_byptp2 <- fill_byptp %>% 
  group_by(ID) %>% 
  mutate(diff = c(abs(diff(mean_judg)), NA)) %>% 
  fill(diff, .direction="down") %>% 
  pivot_wider(names_from=COND2,values_from=mean_judg)

# get trial counts based on within ptp RT exclusion
trialcounts_byptp <- main_all %>%
  group_by(ID) %>%
  summarize(all = sum(!is.na(RT)), rmv1 = sum(!is.na(RT_OUTLIER_1)), rmv2 = sum(!is.na(RT_OUTLIER_2)), rmv3 = sum(!is.na(RT_OUTLIER_3)), rmv4 = sum(!is.na(RT_OUTLIER_4)))

# remove ptps with low trial counts or filler accuracy 
main_rmv1 <- main_all %>%
  filter(ID != "" & ID != "")

# filter outlier trials within ptp
main_rmv2 <- main_rmv1 %>%
  filter(!is.na(RT_OUTLIER_3))

# filter outlier trials across ptps
df_outliers <- main_rmv2 %>%
  group_by(COND2) %>%
  mutate(outlier = ifelse(is_outlier(RT), RT, NA))

# count and remove outlier trials
out_counts <- df_outliers %>% ungroup() %>% summarize(sum(!is.na(outlier)))
main_rmv3 <- df_outliers %>% filter(is.na(outlier))
write.csv(main_rmv2,"")
write.csv(main_rmv3,"")
main_rmv3 <- read.csv("")

# get means by condition
condmeans <- main_rmv2 %>%
  group_by(COND2) %>%
  summarize(mean_judg=mean(selection),sd_judg=sd(selection),mean_rt=mean(RT),sd_rt=sd(RT),counts=n())
