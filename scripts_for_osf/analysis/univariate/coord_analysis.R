# coord_analysis.R
# compare z coordinate of top illness and mentalizing vertices
# written by MH

library(tidyr)
library(dplyr)
library(plyr)
library(stringr)

wd = ""
setwd(wd)

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
con_bm <- "bio_vs_mech"
con_sp <- "soc_vs_phys"
vals_bm <- vector()
vals_sp <- vector()

# get values for each participant
for (sub in subs) {
  val_bm <- read.table(paste0(sub,"_",con_bm,".txt"))[["V7"]]
  val_sp <- read.table(paste0(sub,"_",con_sp,".txt"))[["V7"]]
  vals_bm <- append(vals_bm,val_bm)
  vals_sp <- append(vals_sp,val_sp)
}

# combine into one data frame
all_coords <- data.frame(subs = subs, biomech = vals_bm, socphys = vals_sp) %>%
  pivot_longer(cols=c("biomech","socphys"),names_to="con",values_to="val")

# stats
a1 <- aov(val ~ con + Error(subs/con), all_coords)
capture_a1 <- summary(a1)
capture.output(print(a1), capture_a1, file = "coord_analysis_results.txt")

# means
means <- all_coords %>%
  group_by(con) %>%
  summarize(mean_val = mean(val), sd_val = sd(val))
