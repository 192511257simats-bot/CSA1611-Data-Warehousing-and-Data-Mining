# Day 1 - Q8: scatter plot of mobile phones sold (x) vs money (y)
x <- c(4, 1, 5, 7, 10, 2, 50, 25, 90, 36)
y <- c(12, 5, 13, 19, 31, 7, 153, 72, 275, 110)

png("day1/output/q08_scatter.png", 650, 500)
plot(x, y, pch = 19, col = "darkgreen", main = "Mobile phones sold vs money",
     xlab = "Number of mobile phones sold (x)", ylab = "Money (y)")
abline(lm(y ~ x), col = "red", lwd = 2)
invisible(dev.off())

fit <- lm(y ~ x)
cat("Linear fit: y =", round(coef(fit)[1], 3), "+", round(coef(fit)[2], 3), "* x\n")
cat("Correlation r =", round(cor(x, y), 4), "-> strong positive linear relationship\n")
cat("Plot saved: day1/output/q08_scatter.png\n")
