# Day 1 - Q9: Partition marks into 3 bins: equal-frequency and equal-width, plot histograms
marks <- sort(c(55,60,71,63,55,65,50,55,58,59,61,63,65,67,71,72,75))
n <- length(marks); k <- 3
cat("Sorted marks:", marks, "\nn =", n, "\n")

# (a) equal-frequency (equi-depth): same number of values per bin (6,6,5)
size <- ceiling(n / k)
ef <- split(marks, ceiling(seq_along(marks) / size))
cat("\n(a) Equal-frequency partitioning\n")
for (i in seq_along(ef)) cat("  Bin", i, ":", ef[[i]], "\n")

# (b) equal-width: width = (max - min)/k
w <- (max(marks) - min(marks)) / k
br <- min(marks) + w * 0:k
ew <- split(marks, cut(marks, br, include.lowest = TRUE))
cat(sprintf("\n(b) Equal-width partitioning, width = (%d-%d)/%d = %.2f\n", max(marks), min(marks), k, w))
for (i in seq_along(ew)) cat("  Bin", names(ew)[i], ":", ew[[i]], "\n")

png("day1/output/q09_histograms.png", 900, 450)
par(mfrow = c(1, 2))
hist(marks, breaks = c(min(marks) - 0.5, sapply(ef, max)[-length(ef)] + 0.5, max(marks) + 0.5),
     main = "Equal-frequency bins", xlab = "marks", col = "skyblue")
hist(marks, breaks = br, main = "Equal-width bins", xlab = "marks", col = "orange")
invisible(dev.off())
cat("\nHistograms saved: day1/output/q09_histograms.png\n")
