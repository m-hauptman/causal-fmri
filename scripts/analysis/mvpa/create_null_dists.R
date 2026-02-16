# create_null_dists.R
# create null distributions for each stat test of ROI MVPA results
# written by MH, adapted from GE

# set defaults
wd = ""
setwd(wd)
test = "biomech"

# initialize data frame where null dists of stat tests stored
nboot = 15000
boot.stats = data.frame(iter=1:nboot,t.LPC_socphys=rep(NA, nboot),t.RPC_socphys=rep(NA, nboot),
                        t.LTPJ_socphys=rep(NA, nboot),t.RTPJ_socphys=rep(NA, nboot),
                        t.LPC_causrest=rep(NA, nboot),t.RPC_causrest=rep(NA, nboot),
                        t.LTPJ_causrest=rep(NA, nboot),t.RTPJ_causrest=rep(NA, nboot),
                        t.Lang=rep(NA, nboot),t.Logic=rep(NA, nboot))
                  
# read the null distribution matrix. each column contains the null
# classification performance for one subject, ROI, test word class.
nulls = read.csv(paste0(test,'_nulldists_zbetamaps_all'), header=F)

# matrix's columns
factors = read.csv(paste0(test,'_factors_zbetamaps_all'), header=T, stringsAsFactors=T)

rois1 <- c("PC","TPJ")
rois2 <- c("Lang","Logic")
hemis <- c("lh","rh")
contrasts <- c("soc_vs_phys", "caus_vs_rest")
subs <- c("IRNX_05","IRNX_06","IRNX_07","IRNX_08","IRNX_10","IRNX_11","IRNX_12",
          "IRNX_13","IRNX_14","IRNX_15","IRNX_16","IRNX_17","IRNX_18",
          "IRNX_19","IRNX_20","IRNX_22","IRNX_23","IRNX_24","IRNX_25","IRNX_26")
n <- (length(subs)*length(contrasts)*length(rois1)*length(hemis)) + (length(subs)*length(rois2))
v_num <- 300

for (row_n in 1:nboot) {
  
  # print iteration periodically.
  if (row_n %% 100 == 0) {
    cat("Iteration:", row_n, "\n", file="", sep=" ")
  }
  
  # pick one acc val from each sub's column. 
  col.samples = sample.int(1000, size=n, replace=T)
  # http://stackoverflow.com/questions/9655750/select-an-element-from-each-row-of-a-matrix-in-r 
  inds = cbind(col.samples, 1:n)
  null.sample = nulls[inds]

  # one-sample t-tests
  col_n = 2
  for (roi in rois1) {
    for (con in contrasts) {
      for (hemi in hemis) {
        # Get the null classification values for the ROI
        vals = null.sample[factors$roi == roi & factors$hemi == hemi & factors$v_num == v_num & factors$contrast == con]
        # Run the t-test.
        t.results = t.test(vals, mu=.5, alternative='greater')
        # Record the results in the bootstrap table.
        boot.stats[row_n, col_n] = as.numeric(t.results$statistic)
        col_n = col_n+1   
      }
    }
  }
  for (roi in rois2) {
    if (roi == "Lang") {
      con = "lang_vs_math"
    }
    else {
      con = "log_vs_lang"
    }
    # Get the null classification values for the ROI
    vals = null.sample[factors$roi == roi & factors$v_num == v_num & factors$contrast == con]
    # Run the t-test.
    t.results = t.test(vals, mu=.5, alternative='greater')
    # Record the results in the bootstrap table.
    boot.stats[row_n, col_n] = as.numeric(t.results$statistic)
    col_n = col_n+1
  }
    
}

# save
write.csv(boot.stats, paste0(test,"_bootstrap_stats.csv"), quote=F, row.names=F)

# compare null & true stats
source("compare_obs_boot.R")
 