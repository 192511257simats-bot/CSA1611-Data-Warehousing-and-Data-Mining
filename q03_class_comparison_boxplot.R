# Day 2 - Q3: Compare two Year-9 classes - mean, median, range, boxplot
A <- c(76, 35, 47, 64, 95, 66, 89, 36, 84)
B <- c(51, 56, 84, 60, 59, 70, 63, 66, 50)

res <- data.frame(Class = c("A", "B"),
                  Mean   = round(c(mean(A), mean(B)), 2),
                  Median = c(median(A), median(B)),
                  Range  = c(diff(range(A)), diff(range(B))))
print(res)
cat("\nHigher mean  :", ifelse(mean(A) > mean(B), "Class A", "Class B"))
cat("\nHigher median:", ifelse(median(A) > median(B), "Class A", "Class B"))
cat("\nLarger range :", ifelse(diff(range(A)) > diff(range(B)), "Class A", "Class B"), "(= less consistent)\n")

png("day2/output/q03_boxplot.png", 650, 500)
boxplot(A, B, names = c("Class A", "Class B"), col = c("lightblue", "lightgreen"),
        main = "Year 9 end-of-year exam marks", ylab = "marks")
invisible(dev.off())
cat("\nInference: Class A has the higher mean and median but also a much wider spread (range 60 vs 34), so its\nresults are less consistent. Class B is tighter around its median (60); its high mark 84 shows up as an outlier.\n")
cat("Outliers (Class B):", boxplot.stats(B)$out, "\nPlot saved: day2/output/q03_boxplot.png\n")
