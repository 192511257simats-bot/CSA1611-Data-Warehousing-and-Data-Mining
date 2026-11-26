"""Day 3 - Q4: Diabetes trend across ages with linear and multiple regression (diabetes.csv)."""
import pandas as pd, numpy as np, matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

d = pd.read_csv("data/diabetes.csv")
d = d[(d.Glucose > 0) & (d.BMI > 0) & (d.BloodPressure > 0)]       # 0 = missing value in this dataset
print("Rows used:", len(d))
d["AgeGroup"] = pd.cut(d.Age, [20, 30, 40, 50, 60, 90], labels=["21-30", "31-40", "41-50", "51-60", "60+"])
trend = d.groupby("AgeGroup", observed=True).agg(patients=("Outcome", "size"), diabetic_rate=("Outcome", "mean"),
                                                mean_glucose=("Glucose", "mean")).round(3)
print("\nDiabetes trend by age group:\n", trend)

print("\n=============== SIMPLE LINEAR REGRESSION: Glucose ~ Age ===============")
m1 = sm.OLS(d.Glucose, sm.add_constant(d[["Age"]])).fit()
print(m1.summary().tables[1], f"\nR-squared = {m1.rsquared:.3f}")
print("\n=============== SIMPLE LINEAR REGRESSION: Outcome (diabetic = 1) ~ Age ===============")
m1b = sm.OLS(d.Outcome, sm.add_constant(d[["Age"]])).fit()
print(m1b.summary().tables[1], f"\nR-squared = {m1b.rsquared:.3f}")
print("\n=============== MULTIPLE REGRESSION: Outcome ~ Age + BMI + Glucose + BloodPressure + Pregnancies ===============")
X = sm.add_constant(d[["Age", "BMI", "Glucose", "BloodPressure", "Pregnancies"]])
m2 = sm.OLS(d.Outcome, X).fit()
print(m2.summary().tables[1], f"\nR-squared = {m2.rsquared:.3f}, adj R-squared = {m2.rsquared_adj:.3f}")
print("\nInterpretation: diabetes prevalence rises with age until the 40s-50s; Glucose and BMI are the strongest "
      "predictors in the multiple model (largest t-values), age adds a smaller effect once they are controlled for.")

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
trend.diabetic_rate.plot.bar(ax=ax[0], color="indianred"); ax[0].set_title("Share of diabetic patients by age group"); ax[0].set_ylabel("rate")
ax[1].scatter(d.Age, d.Glucose, s=8, alpha=.4); xs = np.linspace(d.Age.min(), d.Age.max(), 50)
ax[1].plot(xs, m1.params["const"] + m1.params["Age"] * xs, "r"); ax[1].set_title("Linear regression: Glucose vs Age"); ax[1].set_xlabel("Age")
plt.tight_layout(); plt.savefig("day3/output/q04_regression.png", dpi=120)
