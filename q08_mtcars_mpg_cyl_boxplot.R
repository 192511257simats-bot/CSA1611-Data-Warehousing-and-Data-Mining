# Day 2 - Q8: Boxplot of mpg for each number of cylinders (mtcars)
png("day2/output/q08_mpg_cyl_boxplot.png", 650, 500)
boxplot(mpg ~ cyl, data = mtcars, col = c("lightgreen", "lightblue", "salmon"),
        xlab = "Number of cylinders", ylab = "Miles per gallon", main = "Mileage by cylinders")
invisible(dev.off())
print(aggregate(mpg ~ cyl, data = mtcars, FUN = function(x) c(mean = mean(x), median = median(x), min = min(x), max = max(x))))
cat("Inference: more cylinders -> lower mpg.\nPlot saved: day2/output/q08_mpg_cyl_boxplot.png\n")
