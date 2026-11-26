# Day 1 - Q1: Approximate median of grouped (interval) data
lower <- c(1, 5, 15, 20, 50, 80)
upper <- c(5, 15, 20, 50, 80, 110)
freq  <- c(200, 450, 300, 1500, 700, 44)

N   <- sum(freq)
cum <- cumsum(freq)
cat("Total frequency N =", N, "\nN/2 =", N / 2, "\nCumulative frequencies:", cum, "\n")

m  <- which(cum >= N / 2)[1]                # median class
L  <- lower[m]; w <- upper[m] - lower[m]
cf <- ifelse(m == 1, 0, cum[m - 1]); f <- freq[m]
cat(sprintf("Median class: %d-%d  (L=%d, cf before=%d, f=%d, width=%d)\n", lower[m], upper[m], L, cf, f, w))

median_approx <- L + ((N / 2 - cf) / f) * w
cat("Approximate median = L + ((N/2 - cf)/f) * width =", round(median_approx, 2), "years\n")
