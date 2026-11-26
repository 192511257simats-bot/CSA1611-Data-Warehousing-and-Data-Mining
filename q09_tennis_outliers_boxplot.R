# Day 2 - Q9: Tennis coach checks for outlier scorers with a boxplot (illustrative data)
points <- c(Ajay = 12, Bala = 15, Chitra = 14, Dev = 18, Esha = 16, Farhan = 13,
            Gita = 17, Hari = 15, Indu = 14, Jai = 41)          # Jai scores unusually high
print(points)

b <- boxplot.stats(points)
q <- quantile(points, c(.25, .75)); iqr <- IQR(points)
cat(sprintf("\nQ1 = %.2f  Q3 = %.2f  IQR = %.2f\n", q[1], q[2], iqr))
cat(sprintf("Outlier fences: lower = Q1 - 1.5*IQR = %.2f, upper = Q3 + 1.5*IQR = %.2f\n", q[1] - 1.5 * iqr, q[2] + 1.5 * iqr))
cat("Outlier score(s):", b$out, "-> player(s):", names(points)[points %in% b$out], "\n")

png("day2/output/q09_tennis_boxplot.png", 600, 500)
boxplot(points, col = "gold", main = "Points scored by tennis players", ylab = "points")
text(1.15, points["Jai"], "Jai (outlier)", col = "red")
invisible(dev.off())
cat("Plot saved: day2/output/q09_tennis_boxplot.png\n")
