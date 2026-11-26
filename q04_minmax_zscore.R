# Day 2 - Q4: Min-max normalisation example and normalising 200,300,400,600,1000
cat("(a) Feature F: min = $50,000, max = $100,000, v = $80,000 -> range [0,1]\n")
v <- 80000; mn <- 50000; mx <- 100000
cat("    v' = (v - min)/(max - min) =", (v - mn) / (mx - mn), "\n\n")

x <- c(200, 300, 400, 600, 1000)
cat("(b) Data:", x, "\n")
cat("    (a) min-max (0,1):", round((x - min(x)) / (max(x) - min(x)), 4), "\n")
cat("    (b) z-score       :", round((x - mean(x)) / sd(x), 4), "  [mean =", mean(x), ", sd =", round(sd(x), 4), "]\n")
