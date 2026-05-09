import pandas as pd

df = pd.read_csv("pre_dataset3.csv")

df = df.drop(columns=["OBJECTID", "State", 
                      "Agency", "Collection Method", "Management Objective", "Local Incident Number",
                      "Comments", "Complex Name", "IRWIN ID", "Fire Number (historical use)",
                      "Complex ID", "Shape__Area", "Shape__Length", "DECADES"], errors="ignore")

df = df[df["Year"] >= 2000]
df["Alarm Date"] = pd.to_datetime(df["Alarm Date"]).dt.strftime("%Y-%m-%d")
df["Containment Date"] = pd.to_datetime(df["Containment Date"]).dt.strftime("%Y-%m-%d")
df["GIS Calculated Acres"] = df["GIS Calculated Acres"].astype(int)

df.rename(columns={"GIS Calculated Acres": "Acres Burned"}, inplace=True)
df = df.dropna()
df.to_csv("post_dataset3.csv", index=False)
