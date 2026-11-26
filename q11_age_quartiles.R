# Day 1 - Q11: Roughly find Q1 and Q3 of the age data
age <- c(13,15,16,16,19,20,20,21,22,22,25,25,25,25,30,33,33,35,35,35,35,36,40,45,46,52,70)
n <- length(age); cat("n =", n, " median =", median(age), "(14th value)\n")

lower <- age[1:13]; upper <- age[15:27]       # halves excluding the median
cat("Lower half:", lower, "\n  -> Q1 = median of lower half =", median(lower), "\n")
cat("Upper half:", upper, "\n  -> Q3 = median of upper half =", median(upper), "\n")
cat("\nCross-check with quantile(type = 2): Q1 =", quantile(age, .25, type = 2), " Q3 =", quantile(age, .75, type = 2), "\n")
cat("Roughly: Q1 ~ 20 and Q3 ~ 35 (IQR =", median(upper) - median(lower), ")\n")
