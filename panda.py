import pandas as pd

# Load CSV
df = pd.read_csv("heart_rate_comparison.csv")

# Calculate correlation
correlation = df["polar_heart_rate"].corr(df["heart_rate"])
print(f"Correlation coefficient: {correlation}")