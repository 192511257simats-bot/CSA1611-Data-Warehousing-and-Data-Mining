# Day 2 - Q1: Photograph preference by age of child: chi-square test, covariance and correlation
pref <- data.frame(A = c(18, 2, 20), B = c(22, 28, 10), C = c(20, 40, 40),
                   row.names = c("5-6 years", "7-8 years", "9-10 years"))
print(pref)

cat("\n--- Is there a relationship between age and photograph preference? (chi-square test of independence) ---\n")
print(chisq.test(as.matrix(pref)))

cat("\n--- Covariance / correlation ---\n")
cat("cov(B, C) =", cov(pref$B, pref$C), "\n")
cat("\nSample covariance matrix:\n");  print(cov(pref))
cat("\ncor(B, C) =", round(cor(pref$B, pref$C), 4), "\n")
cat("\nSample correlation matrix:\n"); print(round(cor(pref), 4))

cat("\n--- What is wrong with this study? ---
 * The test assumes every count is an independent observation. If each child gave a preference for several
   photographs (or the same child is counted in more than one cell) the counts are not independent, and the
   chi-square p-value is not valid.
 * The three age groups have different numbers of choices (60, 70, 70), so raw counts are not directly comparable.
 * Only 3 age groups and 3 photos (n = 200 choices): a significant result says there is an association but not
   WHY - the photographs differ in many ways (person, pose, background), so age effects are confounded with
   picture content. The order in which photos were shown is not controlled either.
 * cov()/cor() here are computed across only 3 rows (age groups), so they are very unstable and should not be
   over-interpreted.\n")
