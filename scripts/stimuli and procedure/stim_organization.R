# stim_organization.R
# checks number of words, number of total characters, characters per word (avg), characters per word (exact), 
# avg log frequency (Google), avg 2gram surprisal (Google), avg dependency length (Stanford) 
# written by MH 

library(dplyr)
library(tidyr)
library(stringr)

## FORMATTING INPUTS ##

wd = ""
setwd(wd)
stim <- read.csv("Stimuli_FINAL.csv", header = TRUE)
freq <- read.csv("")
surp <- read.csv("")
depl <- read.csv("")

# add variables
stim <- stim %>% 
  mutate(s1_char = str_length(SENT1), s1_word = str_count(SENT1,"\\S+"),
         s2_char = str_length(SENT2), s2_word = str_count(SENT2,"\\S+"),
         s1_cpw = s1_char/s1_word, s2_cpw = s2_char/s2_word,
         combined_char = s1_char + s2_char,
         combined_word = s1_word + s2_word,
         combined_cpw = combined_char/combined_word) %>%
  filter(s1_char>0) %>%
  mutate(s1_deplength = depl$s1_deplength) %>%
  # clunky way of keeping track of dep length due to parsing error
  mutate(s2_deplength = case_when(SENT2.DEPL.TYPE == 1 ~ 1.714286,
                                  SENT2.DEPL.TYPE == 2 ~ 2,
                                  SENT2.DEPL.TYPE == 3 ~ 2.285714,
                                  SENT2.DEPL.TYPE == 4 ~ 1.8,
                                  SENT2.DEPL.TYPE == 5 ~ 1.875,
                                  SENT2.DEPL.TYPE == 6 ~ 2,
                                  SENT2.DEPL.TYPE == 7 ~ 1.875,
                                  SENT2.DEPL.TYPE == 8 ~ 2.166667,
                                  SENT2.DEPL.TYPE == 9 ~ 1.8,
                                  SENT2.DEPL.TYPE == 10 ~ 1.875,
                                  SENT2.DEPL.TYPE == 11 ~ 2.285714,
                                  SENT2.DEPL.TYPE == 12 ~ 1.875,
                                  SENT2.DEPL.TYPE == 13 ~ 2.2,
                                  SENT2.DEPL.TYPE == 14 ~ 1.666667,
                                  SENT2.DEPL.TYPE == 15 ~ 1.875,
                                  SENT2.DEPL.TYPE == 16 ~ 1.875,
                                  SENT2.DEPL.TYPE == 17 ~ 2.285714),
         combined_depl = (s1_deplength+s2_deplength)/2,
         s1_freq = freq$s1_freq, s2_freq = freq$s2_freq,
         combined_freq = freq$comb_freq,
         s1_surp = surp$s1_surp, s2_surp = surp$s2_surp,
         combined_surp = surp$comb_surp,
         caus_cond = case_when(COND2=="bio" ~ "causal",
                               COND2=="mech" ~ "causal",
                               COND2=="nocause-bio1" ~ "noncausal",
                               COND2=="nocause-mech1" ~ "noncausal"))

# exact characters per word
s1_ecpw <- NULL
s2_ecpw <- NULL
combined_ecpw <- NULL
for (i in 1:(nrow(stim))) {
  this_row <- stim[i,]
  s1 <- mean(str_length(sapply((strsplit(this_row$SENT1,"\\s")),"[",1:this_row$s1_word)))
  s2 <- mean(str_length(sapply((strsplit(this_row$SENT2,"\\s")),"[",1:this_row$s2_word)))
  s1_ecpw[i] <- s1
  s2_ecpw[i] <- s2
  combined_ecpw[i] <- mean(c(s1,s2))
}
stim$s1_ecpw <- s1_ecpw
stim$s2_ecpw <- s2_ecpw
stim$combined_ecpw <- combined_ecpw

# identify which stimulus version
grpA <- stim %>% filter(Group == "A")
grpB <- stim %>% filter(Group == "B")

which_grp <- grpB

## STATS ##

# get means
avgs_compare <- which_grp %>%
  group_by(COND2) %>%
  summarize(s1_mean_char = mean(s1_char, na.rm=TRUE), s1_mean_word = mean(s1_word,na.rm=TRUE),
    s1_mean_ecpw = mean(s1_ecpw,na.rm=TRUE), s1_mean_freq = mean(s1_freq,na.rm=TRUE), 
    s1_mean_surp = mean(s1_surp,na.rm=TRUE), s1_mean_depl = mean(s1_deplength,na.rm=TRUE), 
    s2_mean_char = mean(s2_char,na.rm=TRUE), s2_mean_word = mean(s2_word,na.rm=TRUE),
    s2_mean_ecpw = mean(s2_ecpw,na.rm=TRUE), s2_mean_freq = mean(s2_freq,na.rm=TRUE), 
    s2_mean_surp = mean(s2_surp,na.rm=TRUE), s2_mean_depl = mean(s2_deplength,na.rm=TRUE),
    combined_mean_char = mean(combined_char,na.rm=TRUE), 
    combined_mean_word = mean(combined_word,na.rm=TRUE),
    combined_mean_ecpw = mean(combined_ecpw,na.rm=TRUE),
    combined_mean_freq = mean(combined_freq,na.rm=TRUE),
    combined_mean_surp = mean(combined_surp,na.rm=TRUE),
    combined_mean_depl = mean(combined_depl,na.rm=TRUE))

# pairwise comparisons
which_grp$COND2 = factor(which_grp$COND2)

# combined across both sentences
pw_char_total <- pairwise.t.test(which_grp$combined_char, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_word_total <- pairwise.t.test(which_grp$combined_word, which_grp$COND2, 
                           paired = FALSE, p.adjust.method = "none")
pw_ecpw_total <- pairwise.t.test(which_grp$combined_ecpw, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_freq_total <- pairwise.t.test(which_grp$combined_freq, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_surp_total <- pairwise.t.test(which_grp$combined_surp, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_depl_total <- pairwise.t.test(which_grp$combined_depl, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")

# by sentence: sentence 1 and sentence 2
pw_char_total1 <- pairwise.t.test(which_grp$s1_char, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_word_total1 <- pairwise.t.test(which_grp$s1_word, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_ecpw_total1 <- pairwise.t.test(which_grp$s1_ecpw, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_freq_total1 <- pairwise.t.test(which_grp$s1_freq, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_surp_total1 <- pairwise.t.test(which_grp$s1_surp, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_depl_total1 <- pairwise.t.test(which_grp$s1_deplength, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")

pw_char_total2 <- pairwise.t.test(which_grp$s2_char, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_word_total2 <- pairwise.t.test(which_grp$s2_word, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_ecpw_total2 <- pairwise.t.test(which_grp$s2_ecpw, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_freq_total2 <- pairwise.t.test(which_grp$s2_freq, which_grp$COND2, 
                                 paired = FALSE, p.adjust.method = "none")
pw_surp_total2 <- pairwise.t.test(which_grp$s2_surp, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")
pw_depl_total2 <- pairwise.t.test(which_grp$s2_deplength, which_grp$COND2, 
                                  paired = FALSE, p.adjust.method = "none")

# inspect results
View(pw_char_total[["p.value"]])
View(pw_word_total[["p.value"]])
View(pw_ecpw_total[["p.value"]]) 
View(pw_freq_total[["p.value"]])
View(pw_surp_total[["p.value"]])
View(pw_depl_total[["p.value"]])

View(pw_char_total1[["p.value"]])
View(pw_word_total1[["p.value"]])
View(pw_ecpw_total1[["p.value"]])
View(pw_freq_total1[["p.value"]])
View(pw_surp_total1[["p.value"]])
View(pw_depl_total1[["p.value"]])

View(pw_char_total2[["p.value"]])
View(pw_word_total2[["p.value"]])
View(pw_ecpw_total2[["p.value"]])
View(pw_freq_total2[["p.value"]])
View(pw_surp_total2[["p.value"]])
View(pw_depl_total2[["p.value"]])
