"""Basic data mining pipeline for the city-level traffic congestion dataset."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
source = ROOT / "data" / "cleaned_traffic_data.csv"
output = ROOT / "data" / "traffic_mining_summary.csv"

def main():
    df = pd.read_csv(source, encoding="utf-8-sig")
    df["AverageTCI"] = pd.to_numeric(df["AverageTCI"], errors="coerce")
    df["MaxTCI"] = pd.to_numeric(df["MaxTCI"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["City", "AverageTCI", "MaxTCI"]).drop_duplicates(subset=["City"])
    df["CongestionLevel"] = pd.cut(
        df["AverageTCI"], bins=[-float("inf"), 10, 25, float("inf")],
        labels=["Low", "Medium", "High"], right=False
    ).astype(str)
    df = df.sort_values("AverageTCI", ascending=False)
    df.to_csv(output, index=False)
    print("Traffic Congestion Data Mining Summary")
    print(f"Rows before cleaning: {before}")
    print(f"Rows after cleaning: {len(df)}")
    print(f"Duplicate/missing rows removed: {before-len(df)}")
    print(f"Average TCI: {df['AverageTCI'].mean():.2f}")
    print(f"Maximum TCI: {df['MaxTCI'].max():.2f}")
    print(f"Highest average congestion city: {df.iloc[0]['City']} ({df.iloc[0]['AverageTCI']:.2f})")
    print("\nCongestion category counts:")
    print(df["CongestionLevel"].value_counts().to_string())
    print(f"\nSaved ranked data to: {output}")

if __name__ == "__main__":
    main()
