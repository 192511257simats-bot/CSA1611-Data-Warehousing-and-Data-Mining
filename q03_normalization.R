# Day 1 - Q3: Min-max and z-score normalization of 200, 300, 400, 600, 1000
x <- c(200, 300, 400, 600, 1000)

minmax <- (x - min(x)) / (max(x) - min(x)) * (1 - 0) + 0      # new range [0, 1]
zscore <- (x - mean(x)) / sd(x)                               # sample standard deviation

cat("Data               :", x, "\n")
cat("Mean =", mean(x), " SD (sample) =", round(sd(x), 4), "\n\n")
cat("(a) Min-max [0,1]  :", round(minmax, 4), "\n")
cat("(b) Z-score        :", round(zscore, 4), "\n")
print(data.frame(original = x, min_max = round(minmax, 4), z_score = round(zscore, 4)))
