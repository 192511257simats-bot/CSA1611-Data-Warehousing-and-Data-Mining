# Day 1 - Q6: Normalise age = 35 (min-max, z-score with sd = 12.94, decimal scaling)
age <- c(23,23,27,27,39,41,47,49,50,52,54,54,56,57,58,58,60,61)
v <- 35

mm <- (v - min(age)) / (max(age) - min(age))
cat(sprintf("(i)   Min-max [0,1]: (35 - %d)/(%d - %d) = %.4f\n", min(age), max(age), min(age), mm))

sd_given <- 12.94
cat(sprintf("(ii)  Z-score: (35 - %.2f)/%.2f = %.4f   [mean of age = %.2f, sd given in the question = 12.94]\n",
            mean(age), sd_given, (v - mean(age)) / sd_given, mean(age)))

j <- floor(log10(max(abs(age)))) + 1      # smallest j such that max(|v|)/10^j < 1
cat(sprintf("(iii) Decimal scaling: j = %d (max |age| = %d)  ->  35 / 10^%d = %.2f\n", j, max(age), j, v / 10^j))
