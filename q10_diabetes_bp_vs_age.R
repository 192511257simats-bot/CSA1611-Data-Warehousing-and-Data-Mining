# Day 2 - Q10: BloodPressure vs Age in diabetes.csv - scatter plot and bar chart
d <- read.csv("data/diabetes.csv")
cat("Rows:", nrow(d), " | BloodPressure = 0 means 'not recorded' ->", sum(d$BloodPressure == 0), "rows removed\n")
d <- d[d$BloodPressure > 0, ]

png("day2/output/q10_scatter.png", 700, 500)
plot(d$Age, d$BloodPressure, pch = 19, col = rgb(0, 0, 1, 0.4), xlab = "Age", ylab = "Blood pressure (diastolic, mm Hg)",
     main = "BloodPressure vs Age")
abline(lm(BloodPressure ~ Age, d), col = "red", lwd = 2)
invisible(dev.off())

d$AgeGroup <- cut(d$Age, c(20, 30, 40, 50, 60, 100), labels = c("21-30", "31-40", "41-50", "51-60", "60+"))
avg <- tapply(d$BloodPressure, d$AgeGroup, mean)
print(round(avg, 2))

png("day2/output/q10_barchart.png", 700, 500)
barplot(avg, col = "steelblue", ylim = c(0, 90), xlab = "Age group", ylab = "Mean blood pressure",
        main = "Mean blood pressure by age group")
invisible(dev.off())
cat("\ncor(Age, BloodPressure) =", round(cor(d$Age, d$BloodPressure), 3),
    "-> blood pressure rises with age; the 41-60 age groups are most affected.\n")
cat("Plots saved: day2/output/q10_scatter.png, q10_barchart.png\n")
