import pandas as pd
import re

# === Step 1: Load your data ===
file_path = "./all_colors.csv"   # Change to your CSV file path
df = pd.read_csv(file_path)

# === Step 2: extract column groups ===
cols = list(df.columns)
paired_cols = [(cols[i], cols[i+1]) for i in range(0, len(cols), 2)]

# === Step 3: Prepare a clean dataframe ===
clean_rows = []

for label_col, value_col in paired_cols:
    color_name = re.sub(r'[^a-zA-Z]', '', label_col).lower()  # simplify column name

    # Only keep target colors
    if any(c in color_name for c in ["red", "orange", "yellow", "green", "black", "white"]):
        color_general = next((c for c in ["red", "orange", "yellow", "green", "black", "white"] if c in color_name), None)

        # Extract values
        data = dict(zip(df[label_col], df[value_col]))
        clean_rows.append({
            "color": color_general,
            "R_mean": float(data.get("R Mean", "nan")),
            "R_std": float(data.get("R Stdv", "nan")),
            "G_mean": float(data.get("G Mean", "nan")),
            "G_std": float(data.get("G Stdv", "nan")),
            "B_mean": float(data.get("B Mean", "nan")),
            "B_std": float(data.get("B Stdv", "nan")),
        })

# === Step 4: Create a cleaned DataFrame ===
clean_df = pd.DataFrame(clean_rows)

# === Step 5: Compute average mean and average std per color ===
summary = clean_df.groupby("color").agg({
    "R_mean": "mean",
    "R_std": "mean",   # average of the stds
    "G_mean": "mean",
    "G_std": "mean",   # average of the stds
    "B_mean": "mean",
    "B_std": "mean"    # average of the stds
}).round(2)

# === Step 6: Save and print ===
summary.to_csv("color_summary.csv")
print("\n=== COLOR SUMMARY ===")
print(summary)


#55.45