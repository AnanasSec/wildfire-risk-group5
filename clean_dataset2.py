import pandas as pd

df = pd.read_csv("pre_dataset2.csv")

cols_to_remove = [
    "incident_is_final", 
    "incident_administrative_unit_url",
    "incident_containment",
    "incident_control",
    "incident_cooperating_agencies",
    "incident_type",
    "is_active",
    "calfire_incident",
    "notification_desired"
]

df = df.drop(columns=[c for c in cols_to_remove if c in df.columns])

df = df.dropna()
df.to_csv("post_dataset2.csv", index=False)
