# Day 2 - Q5: Histogram of AirPassengers, x-axis starts at 100, bins 150 wide from 200 to 700
br <- c(100, seq(200, 700, by = 150))          # 100,200,350,500,650
cat("Break points:", br, "\nRange of data:", range(AirPassengers), "\n")
png("day2/output/q05_airpassengers_hist.png", 700, 500)
hist(AirPassengers, breaks = br, xlim = c(100, 700), col = "tomato",
     main = "Histogram of AirPassengers", xlab = "Monthly passengers (thousands)")
invisible(dev.off())
h <- hist(AirPassengers, breaks = br, plot = FALSE)
print(data.frame(bin = paste0("(", head(br, -1), ",", br[-1], "]"), count = h$counts))
cat("Plot saved: day2/output/q05_airpassengers_hist.png\n")
