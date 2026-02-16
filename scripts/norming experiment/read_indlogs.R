# read_indlogs.R
# process online data from norming experiment
# written by MH, plus a function from PCIBEX

# load libraries
library(readr)
library(dplyr)
library(plyr)
library(tidyr)
library(stringr)
library(ggplot2)
library(forcats)

# set directory 
wd <- ""
setwd("")

### functions ###

# split groups into individual csv files
split.main.trials <- function(filepath) {
  
  # read in
  trials <- read.csv(filepath)
  not_all_na <- function(x) any(!is.na(x))
  trials <- trials %>% select(where(not_all_na)) %>% filter(GROUP1 > 0)
  groups <- max(trials$GROUP1)
  
  # create subsets
  for (group in 1:groups) {
    group_trials <- trials %>% filter(GROUP1==group)
    group_name <- group_trials$GROUP_NAME[1]
    write.csv(group_trials, paste("sep_group/",group_name,"_trials.csv",sep=""))
  }
  
}

# convert the results.txt file from PCIbex into an organized csv format
# code from PCIbex's developer -- function to convert results to csv file
read.pcibex <- function(filepath, auto.colnames=TRUE, fun.col=function(col,cols){cols[cols==col]<-paste(col,"Ibex",sep=".");return(cols)}) {
  n.cols <- max(count.fields(filepath,sep=",",quote=NULL),na.rm=TRUE)
  if (auto.colnames){
    cols <- c()
    con <- file(filepath, "r")
    while ( TRUE ) {
      line <- readLines(con, n = 1, warn=FALSE)
      if ( length(line) == 0) {
        break
      }
      m <- regmatches(line,regexec("^# (\\d+)\\. (.+)\\.$",line))[[1]]
      if (length(m) == 3) {
        index <- as.numeric(m[2])
        value <- m[3]
        if (index < length(cols)){
          cols <- c()
        }
        if (is.function(fun.col)){
          cols <- fun.col(value,cols)
        }
        cols[index] <- value
        if (index == n.cols){
          break
        }
      }
    }
    close(con)
    return(read.csv(filepath, comment.char="#", header=FALSE, col.names=cols))
  }
  else{
    return(read.csv(filepath, comment.char="#", header=FALSE, col.names=seq(1:n.cols)))
  }
}

# check for two initial exclusion criteria
check.skip <- function(temp, ptp, num_trials) {
  
  skip <- FALSE
  ptp_report <- ""
  
  # check number of trials (arbitrary)
  if (nrow(temp) < num_trials) {
    skip <- TRUE
    ptp_report <- "missingtrials"
  }
  
  # check whether responses were actually recorded at least 75% of the time
  pressedkey <- temp %>% filter(PennElementName=="©1234") %>% select(Value)
  if (sum(is.na(pressedkey)) > (nrow(pressedkey)/4)) {
    skip <- TRUE
    ptp_report <- "missingkeypress"
  }
  
  return(list(skip=skip, ptp_report=ptp_report))
}

# check training trial accuracy
check.training <- function(temp,ptp,counter) {
  
  training_results <- temp %>%
    unite("Descriptor",PennElementName:Parameter,remove=FALSE) %>%
    filter(Descriptor == "timeout_Start" | Descriptor == "©1234_PressedKey", Type == "training_3") %>%
    select(Descriptor, Value, EventTime, UNIQUE_ID, GROUP1, GROUP2, GROUP_NAME, COND1, COND2, Group, SENT1, SENT2, PTP_GENDER, MECHTYPE, ILLCAUS, ILLTYPE, ILLORG, NAMES, TARGET, ID, LANG, ENGLISH, AGE, EDU, RACE, ETHNIC, GENDER) %>%
    mutate(event = case_when(Descriptor == "timeout_Start" ~ "start_time",
                             Descriptor == "©1234_PressedKey" ~ "end_time"),
           selection = ifelse((Value=="1"|Value=="2"|Value=="3"|Value=="4"),Value,NA_character_),
           EventTime = if_else(EventTime == "Never", NA_real_,
                               suppressWarnings(as.numeric(EventTime)))) %>%
    fill(selection, .direction="up") %>%
    select(-Descriptor, -Value) %>%
    pivot_wider(names_from = event, values_from = EventTime,values_fn=length) %>%
    mutate(RT = end_time - start_time,
           selection = as.numeric(selection)) %>%
    drop_na()
  
  # check for accuracy
  if ((sum(training_results$selection[training_results$COND2 == "related"]) > 6) && (sum(training_results$selection[training_results$COND2 == "unrelated"]) < 5)) {
    training_check <- TRUE
  } else {
    training_check <- FALSE
  }
  
  # add results of check to data frame
  training_results <- training_results %>%
    mutate(CHECK1 = rep(training_check))
  
  # save formatted data frame
  write.csv(training_results, file.path(ptp,"trainingresults.csv"))
  
  return(training_check)
}

# check filler trial accuracy
check.fillers <- function(temp,ptp,counter) {
  
  filler_results <- temp %>%
    unite("Descriptor",PennElementName:Parameter,remove=FALSE) %>%
    filter(Descriptor == "timeout_Start" | Descriptor == "©1234_PressedKey", Type == "filler" | Type == "myersfiller") %>%
    select(Descriptor, Value, EventTime, UNIQUE_ID, GROUP1, GROUP2, GROUP_NAME, COND1, COND2, Group, SENT1, SENT2, PTP_GENDER, MECHTYPE, ILLCAUS, ILLTYPE, ILLORG, NAMES, TARGET, ID, LANG, ENGLISH, AGE, EDU, RACE, ETHNIC, GENDER) %>%
    mutate(event = case_when(Descriptor == "timeout_Start" ~ "start_time",
                             Descriptor == "©1234_PressedKey" ~ "end_time"),
           selection = ifelse((Value=="1"|Value=="2"|Value=="3"|Value=="4"),Value,NA_character_),
           EventTime = if_else(EventTime == "Never", NA_real_,
                               suppressWarnings(as.numeric(EventTime)))) %>%
    fill(selection, .direction="up") %>%
    select(-Descriptor, -Value) %>%
    pivot_wider(names_from = event, values_from = EventTime) %>%
    mutate(RT = end_time - start_time,
           selection = as.numeric(selection)) %>%
    drop_na()
  
  # check for accuracy, allow 1 wrong answer in each category
  if ((all(filler_results$selection[filler_results$COND2 == "related"] > 2)) && (all(filler_results$selection[filler_results$COND2 == "unrelated"] < 3))) {
    filler_check <- TRUE
  } else if ((sum(filler_results$selection[filler_results$COND2 == "related"] < 3) < 2) && (sum(filler_results$selection[filler_results$COND2 == "unrelated"] > 2) < 2)) {
    filler_check <- TRUE
  } else {
    filler_check <- FALSE
  }
  
  # add results of check to data frame
  filler_results <- filler_results %>%
    mutate(CHECK2 = rep(filler_check))
  
  # save formatted data frame
  write.csv(filler_results, file.path(ptp,"fillerresults.csv"))
  
  return(list(filler_check=filler_check,filler_results=filler_results))
}

# print filter for format.main
print.main <- function() {
  
  illnesses <- c("covid1","type2diabetes","skincancer1","liver1","heart1","cancer2","skincancer2",
    "lung1","covid2","braincancer","heart2","breastcancer","liver3","heart3","throatcancer",
    "lung2","pneumonia","GI1","GI2","lungcancer2","bloodcancer2","bloodpressure","epilepsy",
    "HIV-AIDS1","acne1","acne2","allergies","anemia","asthma","chickenpox","cold1","cold2","cancer1",
    "flu3","flu1","foodpoison2","malaria","pimples","stomachflu2","tetanus","flu2","bloodcancer1")
  
  typelist <- " "
  for (i in 1:length(illnesses)) {
    typelist = paste(typelist,"Type == '",illnesses[i],"' | ",sep="")
  }
  print(typelist)
}

# format main experimental trials
format.main <- function(temp,ptp,counter) {
  
  main_results <- temp %>%
    unite("Descriptor",PennElementName:Parameter,remove=FALSE) %>%
    filter(Descriptor == "timeout_Start" | Descriptor == "©1234_PressedKey",  Type == 'covid1' | Type == 'type2diabetes' | Type == 'skincancer1' | Type == 'liver1' | Type == 'heart1' | Type == 'cancer2' | Type == 'skincancer2' | Type == 'lung1' | Type == 'covid2' | Type == 'braincancer' | Type == 'heart2' | Type == 'breastcancer' | Type == 'liver3' | Type == 'heart3' | Type == 'throatcancer' | Type == 'lung2' | Type == 'pneumonia' | Type == 'GI1' | Type == 'GI2' | Type == 'lungcancer2' | Type == 'bloodcancer2' | Type == 'bloodpressure' | Type == 'epilepsy' | Type == 'HIV-AIDS1' | Type == 'acne1' | Type == 'acne2' | Type == 'allergies' | Type == 'anemia' | Type == 'asthma' | Type == 'chickenpox' | Type == 'cold1' | Type == 'cold2' | Type == 'cancer1' | Type == 'flu3' | Type == 'flu1' | Type == 'foodpoison2' | Type == 'malaria' | Type == 'pimples' | Type == 'stomachflu2' | Type == 'tetanus' | Type == 'flu2' | Type == 'bloodcancer1') %>%
    select(Descriptor, Value, EventTime, UNIQUE_ID, GROUP1, GROUP2, GROUP_NAME, COND1, COND2, Group, SENT1, SENT2, PTP_GENDER, MECHTYPE, ILLCAUS, ILLTYPE, ILLORG, NAMES, TARGET, ID, LANG, ENGLISH, AGE, EDU, RACE, ETHNIC, GENDER) %>% 
    mutate(event = case_when(Descriptor == "timeout_Start" ~ "start_time",
                             Descriptor == "©1234_PressedKey" ~ "end_time"),
           selection = ifelse((Value=="1"|Value=="2"|Value=="3"|Value=="4"),Value,NA_character_),
           EventTime = if_else(EventTime == "Never", NA_real_,
                               suppressWarnings(as.numeric(EventTime)))) %>%
    fill(selection, .direction="up") %>%
    select(-Descriptor, -Value) %>% 
    pivot_wider(names_from = event, values_from = EventTime) %>%
    mutate(RT = end_time - start_time,
           selection = as.numeric(selection),
           PTP = rep(counter)) %>%
    group_by(COND2) %>%
    mutate(RT_OUTLIER_3 = ifelse((abs(RT-mean(RT,na.rm=TRUE))>(sd(RT,na.rm=TRUE)*2.5)),NA,RT),
           RT_OUTLIER_4 = ifelse((abs(RT-mean(RT,na.rm=TRUE))>(sd(RT,na.rm=TRUE)*3)),NA,RT))
  
  # mark outliers
  RT_mean <- mean(main_results$RT, na.rm=TRUE)
  RT_sd <- sd(main_results$RT, na.rm=TRUE)
  main_results <- main_results %>%
    mutate(RT_OUTLIER_1 = ifelse(((RT < (RT_mean - 2.5*RT_sd)) | (RT > (RT_mean + 2.5*RT_sd))),NA,RT),
           RT_OUTLIER_2 = ifelse(((RT < (RT_mean - 2*RT_sd)) | (RT > (RT_mean + 2*RT_sd))),NA,RT))
  
  # save formatted data frame
  write.csv(main_results, file.path(ptp,"mainresults.csv"))
  
  return(main_results)
  
}

# get illness survey responses
get.illsurvey <- function(temp) {
  responses <- temp %>% 
    filter(Type == "illness_survey" & (PennElementType == "TextInput" | PennElementType == "DropDown")) %>%
    select(Value)
  attncheck <- temp %>%
    filter(Type == "illness_survey" & PennElementName == "attnchck") %>%
    select(Value)
  
  illsurveycheck <- TRUE
  if (attncheck != "Last") {
    illsurveycheck <- FALSE
  }
  
  return(list(responses=responses,illsurveycheck=illsurveycheck))
}

# get survey responses
get.survey <- function(temp) {
  responses <- temp %>% 
    filter(Type == "survey" & PennElementType == "TextInput") %>%
    select(Value)
  return(responses)
}

### main ####

# prepare csvs for online experiment
filepath = "Stimuli_FINAL.csv"

# prepare script for online experiment given specific illnesses

# read in results and set defaults
results <- read.pcibex("results")
ptps_record <- data.frame(matrix(ncol = 2, nrow = 0))
colnames(ptps_record) <- c("ptp","report")
main_all <- NULL
fillers_all <- NULL
illsurvey_resp <- data.frame(matrix(ncol = 2, nrow = 0))
colnames(illsurvey_resp) <- c("ptp","value")
survey_resp <- data.frame(matrix(ncol = 2, nrow = 0))
colnames(survey_resp) <- c("ptp","value")
counter <- 1
num_trials <- 800
ID_filter <- results %>% filter(nchar(ID) > 13)
ptps <- na.omit(unique(ID_filter$ID))

# read in, format, plot each ptp's data
for (ptp in ptps) {
  
  dir.create(paste(ptp))
  ptp_report <- NULL
  temp <- results[results$ID==ptp,]
  
  # check for initial exclusion criteria
  checked <- check.skip(temp, ptp, num_trials)
  if (checked$skip == TRUE) {
    ptp_record <- data.frame(ptp=ptp,report=checked$ptp_report)
    ptps_record <- rbind(ptps_record,ptp_record)
    next
  }
  
  # get survey responses
  illresponses <- get.illsurvey(temp)
  illsurvey_resp <- rbind(illsurvey_resp,data.frame(ptp = ptp, value = illresponses$responses))
  if (illresponses$illsurveycheck == FALSE) {
    ptp_report <- "failedillsurvey"
    ptp_record <- data.frame(ptp=ptp,report=ptp_report)
    ptps_record <- rbind(ptps_record,ptp_record)
  }
  responses <- get.survey(temp)
  survey_resp <- rbind(survey_resp,data.frame(ptp = ptp, value = responses))
  
  # check training trials
  traincheck <- check.training(temp, ptp, counter)
  if (traincheck == FALSE) {
    ptp_report <- "failedtraining"
    ptp_record <- data.frame(ptp=ptp,report=ptp_report)
    ptps_record <- rbind(ptps_record,ptp_record)
  }
  
  # check filler trials
  fillcheck <- check.fillers(temp, ptp, counter)
  fillers_all <- rbind(fillers_all,fillcheck$filler_results)
  if (fillcheck$filler_check == FALSE) {
    ptp_report <- "failedfillers"
    ptp_record <- data.frame(ptp=ptp,report=ptp_report)
    ptps_record <- rbind(ptps_record,ptp_record)
  }
  
  # report success
  if (traincheck == TRUE & fillcheck$filler_check == TRUE){ #& pi_check == TRUE) {
    ptp_report <- "success"
    ptp_record <- data.frame(ptp=ptp,report=ptp_report)
    ptps_record <- rbind(ptps_record,ptp_record)
  }
  
  # format main trials
  main_results <- format.main(temp, ptp, counter)
  main_all <- rbind(main_all, main_results)
  
  counter = counter + 1
}

# save larger dfs
write.csv(main_all, "ALL_mainresults.csv")
write.csv(ptps_record, "ALL_ptpsrecord.csv")
write.csv(fillers_all, "ALL_fillerresults.csv")
write.csv(survey_resp, "ALL_end_surveyresp.csv")
write.csv(illsurvey_resp, "ALL_ill_surveyresp.csv")

