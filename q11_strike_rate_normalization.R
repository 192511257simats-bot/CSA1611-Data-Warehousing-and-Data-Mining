# Day 4 Exercise - Q11: Normalise the strike rates 100, 70, 60, 90, 90
x <- c(100, 70, 60, 90, 90); cat("Data:", x, "\nmean =", mean(x), " sd =", round(sd(x), 4), "\n\n")
mm <- (x - min(x)) / (max(x) - min(x)); cat("(a) Min-max [0,1]               :", round(mm, 4), "\n")
z  <- (x - mean(x)) / sd(x);            cat("(b) Z-score (std deviation)     :", round(z, 4), "\n")
s_A <- mean(abs(x - mean(x)));          cat("(c) Z-score with mean absolute deviation: s_A =", s_A, "->", round((x - mean(x)) / s_A, 4), "\n")
j <- floor(log10(max(abs(x)))) + 1;     cat("(d) Decimal scaling: j =", j, "->", x / 10^j, "\n")
