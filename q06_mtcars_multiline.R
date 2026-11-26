# Day 2 - Q6: Multiple lines in one line chart with a single plot call (mpg and qsec of mtcars)
png("day2/output/q06_mtcars_lines.png", 750, 500)
matplot(mtcars[, c("mpg", "qsec")], type = "l", lty = 1, lwd = 2, col = c("blue", "red"),
        xlab = "Car index (row in mtcars)", ylab = "Value", main = "mpg and qsec of mtcars")
legend("topright", legend = c("mpg", "qsec"), col = c("blue", "red"), lty = 1, lwd = 2)
invisible(dev.off())
print(head(mtcars[, c("mpg", "qsec")]))
cat("Plot saved: day2/output/q06_mtcars_lines.png\n")
