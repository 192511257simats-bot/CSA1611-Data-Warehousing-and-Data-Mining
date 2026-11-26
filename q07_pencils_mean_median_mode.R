# Day 1 - Q7: vector of pencils per box -> mean, median, mode
pencils <- c(9, 25, 23, 12, 11, 6, 7, 8, 9, 10)
names(pencils) <- paste0("Box", 1:10)
print(pencils)

get_mode <- function(v) { u <- unique(v); u[which.max(tabulate(match(v, u)))] }   # R has no built-in mode()

cat("\nMean   =", mean(pencils), "\n")
cat("Median =", median(pencils), "\n")
cat("Mode   =", get_mode(pencils), "(appears", sum(pencils == get_mode(pencils)), "times)\n")
