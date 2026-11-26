# Day 2 - Q7: 'water' dataset (HSAUR): linear relation between mortality and hardness; predict at hardness = 88
water <- read.csv("data/water.csv")               # downloaded from the Rdatasets collection (HSAUR::water)
str(water)

cat("\nCorrelation(hardness, mortality) =", round(cor(water$hardness, water$mortality), 4), "\n")

png("day2/output/q07_water_regression.png", 700, 500)
plot(water$hardness, water$mortality, pch = 19, col = "blue", xlab = "hardness", ylab = "mortality",
     main = "Mortality vs water hardness")
fit <- lm(mortality ~ hardness, data = water)
abline(fit, col = "red", lwd = 2)
invisible(dev.off())

print(summary(fit))
pred <- predict(fit, data.frame(hardness = 88))
cat("\nPredicted mortality for hardness = 88 :", round(pred, 2), "\n")
cat("Conclusion: negative linear relationship - harder water goes with lower mortality.\n")
