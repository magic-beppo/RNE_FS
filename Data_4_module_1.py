import pandas as pd
import os

# Load the CSV file
BasePath = os.path.dirname(os.path.abspath(__file__))
PathData = os.path.join(BasePath, 'data', 'Food_Security_Data_E_All_Data_(Normalized).csv')

# Read the CSV with dtype specified for 'Item Code' and low_memory set to False
df = pd.read_csv(PathData, encoding='ISO-8859-1', dtype={'Item Code': str}, low_memory=False)

# Display the first few rows to ensure data is read correctly
print(df.head())

# Select rows where 'Area Code' is 143, 420, 429, or 5308
filtered_df = df[df['Area Code'].isin([59, 103, 112, 121, 212, 276, 5305, 5000, 5308, 5103, 5100, 5300])]

# Display the filtered data
print(filtered_df.head())  # Optional: Print the first few rows of the filtered data

# Write the filtered data to a new CSV file
filtered_df.to_csv(os.path.join(BasePath, 'FS_selection.csv'), index=False)
