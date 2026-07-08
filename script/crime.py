import pandas as pd

crime = pd.read_excel("data/crime.xlsx")

print(crime.head())
print("\nColumns:")
print(crime.columns.tolist())