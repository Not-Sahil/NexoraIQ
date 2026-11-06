import pandas as pd
import numpy as np

df = pd.read_csv("realistic_olist_business_data.csv")

print(df.isnull().sum())