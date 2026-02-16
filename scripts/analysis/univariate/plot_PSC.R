# plot_PSC.py
# create plots of PSC data
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

#### plot PSC bar graphs and timecourses ####

# language network: main exp conditions extracted from language vertices
wd = ""
setwd(wd)

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
rois <- c("FrontLang","TempLang")
hemis <- c("lh")
cons <- c("lang_vs_math")
con_grps <- c("biomech")
vnums <- c(5)
key <- "all"

for (vnum in vnums) {
  for (con in cons) {
    for (hemi in hemis) {
      for (roi in rois) {
        for (con_grp in con_grps) {
          
          # sum data across participants
          sum_peakpsc <- rep(0,5)
          sum_pscdata <- matrix(nrow=5,ncol=11,rep(0))
          all_psc_max <- NULL
          all_psc_avg <- NULL
          all_psc_data <- NULL
          all_tc_psc <- NULL
          
          for (sub in subs) {
            psc_data <- read.csv(paste0(sub,"/",sub,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,".csv"))
            peak_psc <- psc_data$Peak.psc
            tc_psc <- psc_data[5:length(psc_data)]
            
            # check for bad values!
            if (any(abs(tc_psc) > 2)) {
              print(paste0("Check out:",sub,"_",roi,"_",hemi,"_",con,"_",con_grp))
              tc_psc[abs(tc_psc) > 2] = 0.00000
            }
            
            sum_peakpsc <-  as.data.frame(as.matrix(peak_psc) + as.matrix(sum_peakpsc))          
            sum_pscdata <- as.data.frame(as.matrix(tc_psc) + as.matrix(sum_pscdata))
            all_psc_data <- rbind(tc_psc,all_psc_data)
            
            tc_psc <- tc_psc %>%
              mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
              gather(key="TR",value="psc",1:11) %>%
              filter(cond!="magic")
            tc_psc$TR = as.double(str_sub(tc_psc$TR,2,-2))
            
            tc_psc_avg <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(mean_psc = mean(psc))
            
            all_psc_avg <- rbind(tc_psc_avg,all_psc_avg)
            
            tc_psc_max <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(max_psc = max(psc))
            
            all_psc_max <- rbind(tc_psc_max,all_psc_max)
            
            tc_psc_2 <- tc_psc %>%
              mutate(sub = sub)
            
            all_tc_psc <- rbind(tc_psc_2,all_tc_psc)
            
          }
          
          # save all psc
          write.csv(all_tc_psc,paste0("data/",key,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_data.csv"))
          
          # average and plot
          #avg_peakpsc <- sum_peakpsc/length(subs)
          avg_pscdata <- sum_pscdata/length(subs)
          avg_pscdata <- avg_pscdata %>%
            mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
            gather(key="TR",value="psc",1:11) %>%
            filter(cond!="magic")
          avg_pscdata$TR = as.double(str_sub(avg_pscdata$TR,2,-2))
          
          # plot timecourse!
          tc_dots <- ggplot(avg_pscdata, aes(x=TR,y=psc,group=cond,color=cond)) +
            geom_point(size=4,position=position_dodge(width=0.5)) + geom_line(size=3,position=position_dodge(width=0.5)) +#position_jitter(w=0.02, h=0)) +
            scale_color_manual(values = c("#B1322F","#0076BA","#929292","#000000")) +
            theme_classic() +
            theme(legend.position = "None",axis.ticks.x = element_blank(),
                  axis.line = element_line(colour = 'black', size = 2),
                  axis.text=element_text(colour = 'black',size=20),
                  axis.title=element_text(size=25,face="bold")) +
            xlab("Time after stimulus onset (s)") + ylab("PSC") + ylim(-0.25,0.75) +
            ggtitle(paste0(key," ",roi," ",hemi," ","top ", vnum, " voxels for ",con))

          ggsave(paste0("plots/red_",key,"_PTP_AVG_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_timecourse.png"), plot = tc_dots, width = 10, height = 6, units = "in", dpi = 300)

        }
      }
    }
  }
}

# logic network: main exp conditions extracted from logic vertices
wd = ""
setwd(wd)

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
rois <- c("Logic")
hemis <- c("lh")
cons <- c("log_vs_lang")
con_grps <- c("biomech")
vnums <- c(5)
key <- "all"

for (vnum in vnums) {
  for (con in cons) {
    for (hemi in hemis) {
      for (roi in rois) {
        for (con_grp in con_grps) {
          
          # sum data across participants
          sum_peakpsc <- rep(0,5)
          sum_pscdata <- matrix(nrow=5,ncol=11,rep(0))
          all_psc_max <- NULL
          all_psc_avg <- NULL
          all_psc_data <- NULL
          all_tc_psc <- NULL
          
          for (sub in subs) {
            psc_data <- read.csv(paste0(sub,"/",sub,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,".csv"))
            peak_psc <- psc_data$Peak.psc
            tc_psc <- psc_data[5:length(psc_data)]
            
            # check for bad values!
            if (any(abs(tc_psc) > 2)) {
              print(paste0("Check out:",sub,"_",roi,"_",hemi,"_",con,"_",con_grp))
              tc_psc[abs(tc_psc) > 2] = 0.00000
            }
            
            sum_peakpsc <-  as.data.frame(as.matrix(peak_psc) + as.matrix(sum_peakpsc))          
            sum_pscdata <- as.data.frame(as.matrix(tc_psc) + as.matrix(sum_pscdata))
            all_psc_data <- rbind(tc_psc,all_psc_data)
            
            tc_psc <- tc_psc %>%
              mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
              gather(key="TR",value="psc",1:11) %>%
              filter(cond!="magic")
            tc_psc$TR = as.double(str_sub(tc_psc$TR,2,-2))
            
            tc_psc_avg <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(mean_psc = mean(psc))
            
            all_psc_avg <- rbind(tc_psc_avg,all_psc_avg)
            
            tc_psc_max <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(max_psc = max(psc))
            
            all_psc_max <- rbind(tc_psc_max,all_psc_max)
            
            tc_psc_2 <- tc_psc %>%
              mutate(sub = sub)
            
            all_tc_psc <- rbind(tc_psc_2,all_tc_psc)
            
          }
          
          # save all psc
          write.csv(all_tc_psc,paste0("data/",key,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_data.csv"))
          
          # average and plot
          #avg_peakpsc <- sum_peakpsc/length(subs)
          avg_pscdata <- sum_pscdata/length(subs)
          avg_pscdata <- avg_pscdata %>%
            mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
            gather(key="TR",value="psc",1:11) %>%
            filter(cond!="magic")
          avg_pscdata$TR = as.double(str_sub(avg_pscdata$TR,2,-2))

          # plot timecourse!

          tc_dots <- ggplot(avg_pscdata, aes(x=TR,y=psc,group=cond,color=cond)) +
            geom_point(size=4,position=position_dodge(width=0.5)) + geom_line(size=3,position=position_dodge(width=0.5)) +#position_jitter(w=0.02, h=0)) +
            scale_color_manual(values = c("#B1322F","#0076BA","#929292","#000000")) +
            theme_classic() +
            theme(legend.position = "None",axis.ticks.x = element_blank(),
                  axis.line = element_line(colour = 'black', size = 2),
                  axis.text=element_text(colour = 'black',size=20),
                  axis.title=element_text(size=25,face="bold")) +
            xlab("Time after stimulus onset (s)") + ylab("PSC") + ylim(-0.25,0.75) +
            ggtitle(paste0(key," ",roi," ",hemi," ","top ", vnum, " voxels for ",con))

          ggsave(paste0("plots/red_",key,"_PTP_AVG_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_timecourse.png"), plot = tc_dots, width = 10, height = 6, units = "in", dpi = 300)
        }
      }
    }
  }
}

# PC - leave one run out: main exp conditions extracted from illness vertices
wd = ""
setwd(wd)

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
rois <- c("TPJ","PC")
hemis <- c("lh","rh")
cons <- c("bio_vs_mech")
con_grps <- c("biomech")
vnums <- c(5)
key <- "all"

for (vnum in vnums) {
  for (con in cons) {
    for (hemi in hemis) {
      for (roi in rois) {
        for (con_grp in con_grps) {
          
          sum_peakpsc <- rep(0,5)
          sum_pscdata <- matrix(nrow=5,ncol=11,rep(0))
          all_psc_max <- NULL
          all_psc_avg <- NULL
          all_psc_data <- NULL
          all_tc_psc <- NULL
          
          for (sub in subs) {
            psc_data <- read.csv(paste0(sub,"/",sub,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_avg.csv"))
            peak_psc <- psc_data$Peak.psc
            tc_psc <- psc_data[3:length(psc_data)]
            
            # check for bad values!
            if (any(abs(tc_psc) > 2)) {
              print(paste0("Check out:",sub,"_",roi,"_",hemi,"_",con,"_",con_grp))
              tc_psc[abs(tc_psc) > 2] = 0.00000
            }
            
            sum_peakpsc <-  as.data.frame(as.matrix(peak_psc) + as.matrix(sum_peakpsc))          
            sum_pscdata <- as.data.frame(as.matrix(tc_psc) + as.matrix(sum_pscdata))
            all_psc_data <- rbind(tc_psc,all_psc_data)
            
            tc_psc <- tc_psc %>%
              mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
              gather(key="TR",value="psc",1:11) %>%
              filter(cond!="magic") %>%
              mutate(sub = sub, TR = as.double(str_sub(TR,2,-2)))
            
            tc_psc_avg <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(mean_psc = mean(psc))
            
            all_psc_avg <- rbind(tc_psc_avg,all_psc_avg)
            
            tc_psc_max <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(max_psc = max(psc))
            
            all_psc_max <- rbind(tc_psc_max,all_psc_max)
            
            tc_psc_2 <- tc_psc %>%
              mutate(sub = sub)
            
            all_tc_psc <- rbind(tc_psc_2,all_tc_psc)
            
          }
          
          # # save all psc
          write.csv(all_tc_psc,paste0("data/",key,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_data.csv"))
          
          # average and plot
          #avg_peakpsc <- sum_peakpsc/length(subs)
          avg_pscdata <- sum_pscdata/length(subs)
          avg_pscdata <- avg_pscdata %>%
            mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
            gather(key="TR",value="psc",1:11) %>%
            filter(cond!="magic")
          avg_pscdata$TR = as.double(str_sub(avg_pscdata$TR,2,-2))

          # plot timecourse!

          tc_dots <- ggplot(avg_pscdata, aes(x=TR,y=psc,group=cond,color=cond)) +
            geom_point(size=4,position=position_dodge(width=0.5)) + geom_line(size=3,position=position_dodge(width=0.5)) +#position_jitter(w=0.02, h=0)) +
            scale_color_manual(values = c("#B1322F","#0076BA","#929292","#000000")) +
            theme_classic() +
            theme(legend.position = "None",axis.ticks.x = element_blank(),
                  axis.line = element_line(colour = 'black', size = 2),
                  axis.text=element_text(colour = 'black',size=20),
                  axis.title=element_text(size=25,face="bold")) +
            xlab("Time after stimulus onset (s)") + ylab("PSC") + ylim(-0.5,0.5) +
            ggtitle(paste0(key," ",roi," ",hemi," ","top ", vnum, " voxels for ",con))

          ggsave(paste0("plots/red_",key,"_PTP_AVG_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_timecourse.png"), plot = tc_dots, width = 10, height = 6, units = "in", dpi = 300)
        }
      }
    }
  }
}

# PC/TPJ: main exp conditions extracted from social vertices
wd = ""
setwd(wd)

subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
rois <- c("PC","TPJ")
hemis <- c("lh","rh")
cons <- c("soc_vs_phys")
con_grps <- c("biomech")
vnums <- c(5)
key <- "all"

for (vnum in vnums) {
  for (con in cons) {
    for (hemi in hemis) {
      for (roi in rois) {
        for (con_grp in con_grps) {
          
          # sum data across participants
          sum_peakpsc <- rep(0,5)
          sum_pscdata <- matrix(nrow=5,ncol=11,rep(0))
          all_psc_max <- NULL
          all_psc_avg <- NULL
          all_psc_data <- NULL
          all_tc_psc <- NULL
          
          for (sub in subs) {
            psc_data <- read.csv(paste0(sub,"/",sub,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,".csv"))
            peak_psc <- psc_data$Peak.psc
            tc_psc <- psc_data[5:length(psc_data)]
            
            # check for bad values!
            if (any(abs(tc_psc) > 2)) {
              print(paste0("Check out:",sub,"_",roi,"_",hemi,"_",con,"_",con_grp))
              tc_psc[abs(tc_psc) > 2] = 0.00000
            }
            
            sum_peakpsc <-  as.data.frame(as.matrix(peak_psc) + as.matrix(sum_peakpsc))          
            sum_pscdata <- as.data.frame(as.matrix(tc_psc) + as.matrix(sum_pscdata))
            all_psc_data <- rbind(tc_psc,all_psc_data)
            
            tc_psc <- tc_psc %>%
              mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
              gather(key="TR",value="psc",1:11) %>%
              filter(cond!="magic")
            tc_psc$TR = as.double(str_sub(tc_psc$TR,2,-2))
            
            tc_psc_avg <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(mean_psc = mean(psc))
            
            all_psc_avg <- rbind(tc_psc_avg,all_psc_avg)
            
            tc_psc_max <- tc_psc %>%
              filter(TR<15) %>%
              group_by(cond) %>%
              summarize(max_psc = max(psc))
            
            all_psc_max <- rbind(tc_psc_max,all_psc_max)
            
            tc_psc_2 <- tc_psc %>%
              mutate(sub = sub)
            
            all_tc_psc <- rbind(tc_psc_2,all_tc_psc)
            
          }
          
          # save all psc
          write.csv(all_tc_psc,paste0("data/",key,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_data.csv"))
          
          # average and plot
          avg_pscdata <- sum_pscdata/length(subs)
          avg_pscdata <- avg_pscdata %>%
            mutate(cond = c("bio","magic","mech","noncaus1","noncaus2")) %>%
            gather(key="TR",value="psc",1:11) %>%
            filter(cond!="magic")
          avg_pscdata$TR = as.double(str_sub(avg_pscdata$TR,2,-2))
          
          # plot timecourse!
          
          tc_dots <- ggplot(avg_pscdata, aes(x=TR,y=psc,group=cond,color=cond)) +
            geom_point(size=4,position=position_dodge(width=0.5)) + geom_line(size=3,position=position_dodge(width=0.5)) +#position_jitter(w=0.02, h=0)) +
            scale_color_manual(values = c("#B1322F","#0076BA","#929292","#000000")) +
            theme_classic() +
            theme(legend.position = "None",axis.ticks.x = element_blank(),
                  axis.line = element_line(colour = 'black', size = 2),
                  axis.text=element_text(colour = 'black',size=20),
                  axis.title=element_text(size=25,face="bold")) +
            xlab("Time after stimulus onset (s)") + ylab("PSC") + ylim(-0.5,0.5) +
            ggtitle(paste0(key," ",roi," ",hemi," ","top ", vnum, " voxels for ",con))
          
          ggsave(paste0("plots/red_",key,"_PTP_AVG_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_timecourse.png"), plot = tc_dots, width = 10, height = 6, units = "in", dpi = 300)
        }
      }
    }
  }
}

# PC/TPJ: socphys conditions extracted from illness vertices

wd = ""
setwd(wd)

# social: all
subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18","IRNX_19",
          "IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
rois <- c("PC","TPJ")
hemis <- c("lh","rh")
cons <- c("bio_vs_mech")
con_grps <- c("socphys")
vnums <- c(5)
key <- "all"

for (vnum in vnums) {
  for (con in cons) {
    for (hemi in hemis) {
      for (roi in rois) {
        for (con_grp in con_grps) {
          
          # sum data across participants
          sum_peakpsc <- rep(0,2)
          sum_pscdata <- matrix(nrow=2,ncol=16,rep(0))
          all_psc_max <- NULL
          all_psc_avg <- NULL
          all_psc_data <- NULL
          all_tc_psc <- NULL
          
          for (sub in subs) {
            psc_data <- read.csv(paste0(sub,"/",sub,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,".csv"))
            peak_psc <- psc_data$Peak.psc
            tc_psc <- psc_data[5:length(psc_data)]
            
            # check for bad values!
            if (any(abs(tc_psc) > 2)) {
              print(paste0("Check out:",sub,"_",roi,"_",hemi,"_",con,"_",con_grp))
              tc_psc[abs(tc_psc) > 2] = 0.00000
            }
            
            sum_peakpsc <-  as.data.frame(as.matrix(peak_psc) + as.matrix(sum_peakpsc))          
            sum_pscdata <- as.data.frame(as.matrix(tc_psc) + as.matrix(sum_pscdata))
            all_psc_data <- rbind(tc_psc,all_psc_data)
            
            tc_psc <- tc_psc %>%
              mutate(cond = c("belief","phys")) %>%
              gather(key="TR",value="psc",1:16)
            tc_psc$TR = as.double(str_sub(tc_psc$TR,2,-2))
            
            tc_psc_avg <- tc_psc %>%
              filter(TR<20) %>%
              group_by(cond) %>%
              summarize(mean_psc = mean(psc))
            
            all_psc_avg <- rbind(tc_psc_avg,all_psc_avg)
            
            tc_psc_max <- tc_psc %>%
              filter(TR<20) %>%
              group_by(cond) %>%
              summarize(max_psc = max(psc))
            
            all_psc_max <- rbind(tc_psc_max,all_psc_max)
            
            tc_psc_2 <- tc_psc %>%
              mutate(sub = sub)
            
            all_tc_psc <- rbind(tc_psc_2,all_tc_psc)
            
          }
          
          # save all psc
          write.csv(all_tc_psc,paste0("data/",key,"_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_data.csv"))
          
          # average and plot
          #avg_peakpsc <- sum_peakpsc/length(subs)
          avg_pscdata <- sum_pscdata/length(subs)
          avg_pscdata <- avg_pscdata %>%
            mutate(cond = c("belief","phys")) %>%
            gather(key="TR",value="psc",1:16) 
          avg_pscdata$TR = as.double(str_sub(avg_pscdata$TR,2,-2))
          
          # plot timecourse!
          
          tc_dots <- ggplot(avg_pscdata, aes(x=TR,y=psc,group=cond,color=cond)) +
            geom_point(size=4,position=position_dodge(width=0.5)) + geom_line(size=3,position=position_dodge(width=0.5)) +
            scale_color_manual(values = c("#F8BA00","#2A7100")) +  # "#CBB1D7","#86CEFA"
            theme_classic() +
            theme(legend.position = "None",axis.ticks.x = element_blank(),
                  axis.line = element_line(colour = 'black', size = 2),
                  axis.text=element_text(colour = 'black',size=20),
                  axis.title=element_text(size=25,face="bold")) +
            xlab("Time after stimulus onset (secs)") + ylab("PSC") + ylim(-0.8,0.7) +
            ggtitle(paste0(key," ",roi," ",hemi," ","top ", vnum, " voxels for ",con))
          
          ggsave(paste0("plots/green_",key,"_PTP_AVG_",roi,"_",hemi,"_",con,"_conds=",con_grp,"_top",vnum,"_timecourse.png"), plot = tc_dots, width = 10, height = 6, units = "in", dpi = 300)
        }
      }
    }
  }
}
