# Data Warehousing & Data Mining (CSA16) – Lab Programs

Saveetha School of Engineering · Computer Science and Engineering
Code **and** output for every question of Day 1 – Day 5, numbered in the same order as the question papers.

```
common/fpm_utils.py   shared Apriori / FP-Growth / FP-tree drawing / rule generation / ARFF writer
data/                 water.csv (HSAUR::water) and diabetes.csv (Pima Indians diabetes, 768 rows)
dayN/qNN_*.R|.py      program for question NN          dayN/output/qNN_*.txt   its console output
                                                       dayN/output/*.png/.csv/.arff   plots and generated datasets
```
Run everything (from the repo root): `pip install -r requirements.txt && ./run_all.sh`  (needs Python 3.9+ and R 4.x).
Run one program, e.g.: `Rscript day1/q05_age_fat_plots.R` or `python day3/q01_apriori_fp_customers.py`.

## Question index

| Day | Q | Topic | File |
|---|---|---|---|
| 1 | 1 | Approximate median of grouped data | `day1/q01_grouped_median.R` |
| 1 | 2 | Mean, median, mode, midrange, Q1/Q3 | `day1/q02_age_statistics.R` |
| 1 | 3 | Min-max & z-score normalisation | `day1/q03_normalization.R` |
| 1 | 4 | Smoothing by bin mean / median / boundaries | `day1/q04_binning_smoothing.R` |
| 1 | 5 | Age/%fat: statistics, boxplots, scatter, q-q plot | `day1/q05_age_fat_plots.R` |
| 1 | 6 | Normalise age 35 (min-max, z-score, decimal scaling) | `day1/q06_normalization_age35.R` |
| 1 | 7 | Pencils vector: mean, median, mode | `day1/q07_pencils_mean_median_mode.R` |
| 1 | 8 | Mobile phones scatter plot | `day1/q08_mobile_scatter.R` |
| 1 | 9 | Equal-frequency / equal-width bins + histograms | `day1/q09_marks_binning_histogram.R` |
| 1 | 10 | IQR and standard deviation of speeds | `day1/q10_speed_iqr_sd.R` |
| 1 | 11 | Q1 and Q3 of age | `day1/q11_age_quartiles.R` |
| 2 | 1 | Covariance & correlation, chi-square (photographs) | `day2/q01_covariance_correlation.R` |
| 2 | 2 | AllElectronics prices: 3 equal-frequency bins, smoothing, histogram | `day2/q02_allelectronics_prices.R` |
| 2 | 3 | Two classes: mean/median/range, boxplot | `day2/q03_class_comparison_boxplot.R` |
| 2 | 4 | Min-max example and z-score | `day2/q04_minmax_zscore.R` |
| 2 | 5 | AirPassengers histogram (bins 150 wide) | `day2/q05_airpassengers_histogram.R` |
| 2 | 6 | mtcars mpg & qsec multi-line chart | `day2/q06_mtcars_multiline.R` |
| 2 | 7 | water: mortality vs hardness regression, predict at 88 | `day2/q07_water_regression.R` |
| 2 | 8 | mtcars boxplot mpg ~ cyl | `day2/q08_mtcars_mpg_cyl_boxplot.R` |
| 2 | 9 | Tennis outliers boxplot | `day2/q09_tennis_outliers_boxplot.R` |
| 2 | 10 | diabetes: BloodPressure vs Age scatter + bar chart | `day2/q10_diabetes_bp_vs_age.R` |
| 3 | 1 | Apriori + FP-Growth, support 3, conf 50% | `day3/q01_apriori_fp_customers.py` |
| 3 | 2 | Max number of rules / max frequent itemset size | `day3/q02_max_rules_and_itemset_size.py` |
| 3 | 3 | Naive Bayes and decision tree (train / test) | `day3/q03_bayes_decision_tree.py` |
| 3 | 4 | Diabetes: linear and multiple regression vs age | `day3/q04_diabetes_regression.py` |
| 3 | 5 | M,O,N,K,E,Y: Apriori + FP-tree (sup 2, conf 80%) | `day3/q05_apriori_fp_monkey.py` |
| 3 | 6 | Decision tree + preprocess + logistic | `day3/q06_weka_style_tree_preprocess_logistic.py` |
| 3 | 7 | ARFF + hot-dog rules, accepted / rejected | `day3/q07_hotdog_arff_rules.py` |
| 3 | 8 | Rule-based vs decision tree, accuracy graph | `day3/q08_rule_based_vs_decision_tree.py` |
| 4A | 1 | TV brands: Apriori + FP-tree (sup 3, conf 60%) | `day4/assignment/q01_tv_apriori_fp.py` |
| 4A | 2 | Apriori on bread/milk database (sup 2) | `day4/assignment/q02_bread_apriori.py` |
| 4A | 3 | K-means k = 3, 10 customers (numbered 4 in the paper) | `day4/assignment/q03_kmeans_customers.py` |
| 4A | 4 | Naive-Bayes accuracy / precision / recall / F1 | `day4/assignment/q04_naive_bayes_metrics.py` |
| 4A | 5 | Data integration, duplicates (numbered 7 in the paper) | `day4/assignment/q05_data_integration.py` |
| 4A | 6 | FP-Growth, support 3 | `day4/assignment/q06_fp_growth_support3.py` |
| 4E | 1 | Mall customer clustering (5 segments) | `day4/exercises/q01_mall_customer_clustering.py` |
| 4E | 2 | Employees K-means with different k | `day4/exercises/q02_kmeans_employees.py` |
| 4E | 3 | Naive Bayes vs SVM | `day4/exercises/q03_naive_bayes_vs_svm.py` |
| 4E | 4 | Vegetarian count | `day4/exercises/q04_vegetarian_count.R` |
| 4E | 5 | Mobile phones scatter | `day4/exercises/q05_mobile_scatter.R` |
| 4E | 6 | FP-Growth rules (sup 50%, conf 75%) | `day4/exercises/q06_fp_growth_rules.py` |
| 4E | 7 | Diabetes: decision tree vs SVM, accuracy & F1 | `day4/exercises/q07_diabetes_tree_vs_svm.py` |
| 4E | 8 | Marks binning: equal-freq / equal-width / clustering | `day4/exercises/q08_marks_binning.R` |
| 4E | 9 | Height/weight tree: ARFF, rules, confusion matrix | `day4/exercises/q09_decision_tree_rules.py` |
| 4E | 10 | ARFF + Apriori vs FP-Growth, unique rules | `day4/exercises/q10_tv_apriori_vs_fpgrowth.py` |
| 4E | 11 | Strike-rate normalisations | `day4/exercises/q11_strike_rate_normalization.R` |
| 4E | 12 | Std deviation and variance | `day4/exercises/q12_speed_time_variance.R` |
| 4E | 13 | Apriori vs FP-Growth + metarule rules | `day4/exercises/q13_apriori_vs_fpgrowth_metarule.py` |
| 5 | 1 | Apriori + FP-tree (sup 2, conf 80%) | `day5/q01_apriori_fp_tree.py` |
| 5 | 2 | Apriori (sup 2, conf 80%) | `day5/q02_apriori.py` |

(4A = `day4/assignment`, 4E = `day4/exercises`.)

## Please read – assumptions and honest notes
* **WEKA:** the GUI could not be run here. Every "using WEKA" question is solved with the equivalent scikit-learn / own implementation
  (J48 → decision tree, SMO → SVM, JRip → RIPPER, SimpleKMeans → KMeans). The `.arff` / `.csv` files are generated so you can open them in WEKA
  and take your own screenshots; numbers may differ slightly from WEKA's.
* **Synthetic / constructed data** (the question did not supply it): Day 4 Exercise Q1 (195 of 200 mall customers are random, seeded), Day 4 Exercise Q9 (22 height/weight records
  built to follow the tree, with 2 deliberate exceptions), Day 2 Q9 (tennis scores). Day 3 Q4/Q6/Q8 and Day 4 Q7 use the public Pima `diabetes.csv`.
* **Ambiguous questions:** Day 4 Assignment Q4 (FP/FN taken as per-class values; the question is internally inconsistent) and Q5 (duplicates interpreted as redundant copies) –
  the assumptions are printed at the end of each output. Day 2 Q2 treats the table of 18…30 values as the continuation of the AllElectronics price list. Day 3 Q1 treats each transaction as one basket.
* Support thresholds: where a percentage was given the count is shown (e.g. 50% of 5 transactions → 3, but Day 3 Q5 uses 2 as printed in the question).
* If your lecturer expects textbook quartile or sample-vs-population conventions, change them in the script – both versions are printed where it matters.

## Push to GitHub
```bash
cd dwdm-lab-programs
git init && git add . && git commit -m "DWDM lab programs with outputs"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
