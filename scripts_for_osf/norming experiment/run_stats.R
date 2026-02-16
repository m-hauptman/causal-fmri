# run_stats.R
# run statistics on online norming experiment results
# written by MH

# load libraries
library(readr)
library(plyr)
library(dplyr)
library(tidyr)
library(stringr)
library(ggplot2)
library(forcats)

group_name <- ("group")

# set directory 
wd <- ""
setwd("")

# read in data with outliers removed
data <- read.csv("") %>% 
  mutate(causality = case_when(COND2=="bio" ~ "causal",
                               COND2=="mech" ~ "causal",
                               COND2=="nocause-mech1" ~ "noncausal",
                               COND2=="nocause-bio1" ~ "noncausal"))
# factorize
data$causality <- factor(data$causality)
data$ID <- factor(data$ID)
data$COND2 <- factor(data$COND2)
data$COND2 <- fct_relevel(data$COND2, "bio", "mech", "nocause-bio1","nocause-mech1")

# get means
means <- data %>%
  group_by(COND2) %>%
  summarize(mean_select = mean(selection), sd_select = sd(selection), 
            mean_RT = mean(RT), sd_RT = sd(RT))

means_cnc <- data %>%
  group_by(causality) %>%
  summarize(mean_select = mean(selection), sd_select = sd(selection), 
            mean_RT = mean(RT), sd_RT = sd(RT))

# t test comparing within-causality judgments and RT
c_conds <- data %>% 
  filter(causality == "causal") %>% 
  group_by(ID,COND2) %>%
  summarize(mean_RT = mean(RT),mean_select=mean(selection))
nvnc_conds <-  data %>%
  group_by(ID,causality) %>%
  summarize(mean_RT = mean(RT),mean_select=mean(selection))

# comparison of causality judgments by condition
biophys_s <- t.test(mean_select ~ COND2, c_conds, paired=TRUE)
cvsnc_s <- t.test(mean_select ~ causality, nvnc_conds, paired=TRUE)
biophys_s
cvsnc_s 

# comparison of RT by condition
biophys_rt <- t.test(mean_RT ~ COND2, c_conds, paired=TRUE)
cvsnc_rt <- t.test(mean_RT ~ causality, nvnc_conds, paired=TRUE)
biophys_rt
cvsnc_rt