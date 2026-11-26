# Day 4 Exercise - Q12: standard deviation and variance of AvgSpeed and TotalTime
speed <- c(78, 81, 82, 74, 83, 82, 77, 80, 70); time <- c(39, 37, 36, 42, 35, 36, 40, 38, 46)
pop_var <- function(v) mean((v - mean(v))^2)
r <- data.frame(attribute = c("AvgSpeed (kph)", "TotalTime (min)"),
                mean = c(mean(speed), mean(time)),
                sample_variance = c(var(speed), var(time)), sample_sd = c(sd(speed), sd(time)),
                population_variance = c(pop_var(speed), pop_var(time)), population_sd = c(sqrt(pop_var(speed)), sqrt(pop_var(time))))
print(format(r, digits = 5), row.names = FALSE)
cat("\nCovariance =", round(cov(speed, time), 3), " Correlation =", round(cor(speed, time), 4), "(faster average speed -> shorter total time)\n")
