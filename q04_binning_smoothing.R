# Day 1 - Q4: Smoothing by bin means / bin medians / bin boundaries (equal-depth bins of 4 values)
data <- c(11,13,13,15,15,16,19,20,20,20,21,21,22,23,24,30,40,45,45,45,71,72,73,75)
depth <- 4
bins <- split(data, ceiling(seq_along(data) / depth))

cat("Sorted data:", data, "\nBin depth =", depth, "\n\n")
for (i in seq_along(bins)) cat("Bin", i, ":", bins[[i]], "\n")

by_mean   <- lapply(bins, function(b) rep(round(mean(b), 2), length(b)))
by_median <- lapply(bins, function(b) rep(median(b), length(b)))
by_bound  <- lapply(bins, function(b) ifelse(b - min(b) <= max(b) - b, min(b), max(b)))

cat("\n(a) Smoothing by bin MEANS\n");      for (i in seq_along(by_mean))   cat("Bin", i, ":", by_mean[[i]], "\n")
cat("\n(b) Smoothing by bin MEDIANS\n");    for (i in seq_along(by_median)) cat("Bin", i, ":", by_median[[i]], "\n")
cat("\n(c) Smoothing by bin BOUNDARIES\n"); for (i in seq_along(by_bound))  cat("Bin", i, ":", by_bound[[i]], "\n")
