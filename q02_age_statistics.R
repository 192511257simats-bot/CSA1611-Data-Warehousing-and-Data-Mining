# Day 1 - Q2: mean, median, mode, modality, midrange, Q1 and Q3 of age
age <- c(13,15,16,16,19,20,20,21,22,22,25,25,25,25,30,33,33,35,35,35,35,36,40,45,46,52,70)

cat("(a) Mean   =", round(mean(age), 2), "\n    Median =", median(age), "\n")

tab   <- table(age)
modes <- as.numeric(names(tab)[tab == max(tab)])
cat("(b) Mode(s) =", modes, " (each occurs", max(tab), "times)\n")
cat("    Modality:", c("unimodal", "bimodal", "trimodal")[min(length(modes), 3)],
    "- the data has", length(modes), "modes\n")

cat("(c) Midrange = (min + max)/2 =", (min(age) + max(age)) / 2, "\n")

cat("(d) Quartiles\n")
cat("    Textbook method (median of lower / upper half, quantile type 2): Q1 =",
    quantile(age, 0.25, type = 2), " Q3 =", quantile(age, 0.75, type = 2), "\n")
cat("    R default (type 7, interpolated):                                Q1 =",
    quantile(age, 0.25), " Q3 =", quantile(age, 0.75), "\n")
print(summary(age))
