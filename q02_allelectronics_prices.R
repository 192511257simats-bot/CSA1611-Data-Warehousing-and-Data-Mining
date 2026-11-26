# Day 2 - Q2: AllElectronics prices: equal-frequency (3 bins), smoothing by means & boundaries, histogram
price <- c(1,1,5,5,5,5,5,8,8,10,10,10,10,12,14,14,14,15,15,15,15,15,15,18,18,18,18,18,
           18,18,18,20,20,20,20,20,20,20,21,21,21,21,25,25,25,25,25,28,28,30,30,30)
n <- length(price); k <- 3
cat("n =", n, " (data is already sorted)\n")

size <- ceiling(n / k)                         # 18,17,17
bins <- split(price, ceiling(seq_along(price) / size))
cat("\n(i) Equal-frequency partitioning into 3 bins\n")
for (i in seq_along(bins)) cat(sprintf("  Bin %d (%d values): %s\n", i, length(bins[[i]]), paste(bins[[i]], collapse = " ")))

cat("\n(ii) Smoothing by bin MEANS\n")
for (i in seq_along(bins)) cat(sprintf("  Bin %d: every value -> %.2f\n", i, mean(bins[[i]])))

cat("\n     Smoothing by bin BOUNDARIES (each value -> nearer of min / max of its bin)\n")
for (i in seq_along(bins)) {
  b <- bins[[i]]
  cat(sprintf("  Bin %d (min=%d, max=%d): %s\n", i, min(b), max(b),
              paste(ifelse(b - min(b) <= max(b) - b, min(b), max(b)), collapse = " ")))
}

png("day2/output/q02_histogram.png", 700, 500)
hist(price, breaks = c(0, sapply(bins, max)), col = "steelblue",
     main = "AllElectronics prices (equal-frequency bins)", xlab = "price ($)")
invisible(dev.off())
cat("\n(iii) Histogram saved: day2/output/q02_histogram.png\n")
