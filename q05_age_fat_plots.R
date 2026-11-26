# Day 1 - Q5: age & %fat of 18 adults - mean/median/sd, boxplots, scatter plot, q-q plot
age <- c(23,23,27,27,39,41,47,49,50,52,54,54,56,57,58,58,60,61)
fat <- c(9.5,26.5,7.8,17.8,31.4,25.9,27.4,27.2,31.2,34.6,42.5,28.8,33.4,30.2,34.1,32.9,41.2,35.7)

cat("(a) Descriptive statistics\n")
print(data.frame(attribute = c("age", "%fat"),
                 mean   = round(c(mean(age),   mean(fat)),   2),
                 median = c(median(age), median(fat)),
                 sd     = round(c(sd(age),     sd(fat)),     2)))

png("day1/output/q05_boxplots.png", 900, 450)
par(mfrow = c(1, 2))
boxplot(age, main = "Boxplot of age", ylab = "years", col = "lightblue")
boxplot(fat, main = "Boxplot of %fat", ylab = "% body fat", col = "lightgreen")
invisible(dev.off())

png("day1/output/q05_scatter.png", 600, 500)
plot(age, fat, pch = 19, col = "blue", main = "Scatter plot: age vs %fat", xlab = "age", ylab = "%fat")
abline(lm(fat ~ age), col = "red")
invisible(dev.off())

png("day1/output/q05_qqplot.png", 600, 500)
qqplot(age, fat, main = "Q-Q plot: age vs %fat", xlab = "age quantiles", ylab = "%fat quantiles", pch = 19)
abline(lm(sort(fat) ~ sort(age)), col = "red")
invisible(dev.off())

cat("\n(b)(c) Plots saved: q05_boxplots.png, q05_scatter.png, q05_qqplot.png\n")
cat("Correlation(age, %fat) =", round(cor(age, fat), 3), "\n")
